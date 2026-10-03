# SPDX-License-Identifier: GPL-3.0-or-later
"""Rest-space surface projection for remesh deformation data."""
import hashlib
import struct

import bpy
from mathutils import Vector, geometry
from mathutils.bvhtree import BVHTree


def has_deformation(obj):
    return bool(obj.data.shape_keys or obj.vertex_groups or any(m.type == 'ARMATURE' for m in obj.modifiers))


def unsupported_reason(obj):
    keys = obj.data.shape_keys
    if keys and not keys.use_relative:
        return 'Absolute/time-based shape keys are unsupported. Use relative blendshapes or a separate static copy.'
    if keys and keys.animation_data and keys.animation_data.nla_tracks:
        return 'Shape-key NLA tracks require baking to a supported action before transfer.'
    if has_deformation(obj) and any(m.type != 'ARMATURE' for m in obj.modifiers):
        return 'Apply non-armature modifiers on a separate copy before deformation-aware remesh.'
    if any(m.type == 'ARMATURE' and not m.object for m in obj.modifiers):
        return 'An armature modifier has no armature object; repair the binding before remesh.'
    return None


def prepare_neutral_copy(source, target, context):
    """Only mutate the separate target; never change the source rig's pose."""
    keys = source.data.shape_keys
    basis = [item.co.copy() for item in keys.key_blocks[0].data] if keys else [v.co.copy() for v in source.data.vertices]
    if target.data.shape_keys:
        target.shape_key_clear()
    for vertex, co in zip(target.data.vertices, basis):
        vertex.co = co
    target.modifiers.clear()
    target.data.update()
    context.view_layer.update()


def _copy_rna(source, target, excluded=()):
    for prop in source.bl_rna.properties:
        name = prop.identifier
        if name in {'rna_type', 'type', *excluded} or prop.is_readonly:
            continue
        value = getattr(source, name)
        if prop.type == 'COLLECTION':
            raise ValueError('Unsupported animated property collection: ' + name)
        setattr(target, name, list(value) if getattr(prop, "is_array", False) else value)


def _copy_key_animation(source_obj, target_obj):
    source = source_obj.data.shape_keys
    target = target_obj.data.shape_keys
    for name in source.keys():
        value = source[name]
        target[name] = value.to_dict() if hasattr(value, 'to_dict') else value.to_list() if hasattr(value, 'to_list') else value
    animation = source.animation_data
    if not animation:
        return
    destination = target.animation_data_create()
    if animation.action:
        # Same named shape paths, independent editable action.
        destination.action = animation.action.copy()
        destination.action['fishhwb_owned_transfer'] = True
    for name in ('action_blend_type', 'action_extrapolation', 'action_influence', 'use_nla'):
        setattr(destination, name, getattr(animation, name))
    for curve in animation.drivers:
        new_curve = target.driver_add(curve.data_path)
        if isinstance(new_curve, (list, tuple)):
            new_curve = new_curve[curve.array_index]
        new_curve.mute = curve.mute
        new_curve.extrapolation = curve.extrapolation
        driver = new_curve.driver
        driver.type = curve.driver.type
        driver.use_self = curve.driver.use_self
        driver.expression = curve.driver.expression
        for variable in list(driver.variables):
            driver.variables.remove(variable)
        for variable in curve.driver.variables:
            new_variable = driver.variables.new()
            new_variable.name = variable.name
            new_variable.type = variable.type
            for original, copied in zip(variable.targets, new_variable.targets):
                if variable.type == 'SINGLE_PROP' and hasattr(original, 'id_type'):
                    copied.id_type = original.id_type
                original_id = original.id
                copied.id = target if original_id == source else target_obj if original_id == source_obj else target_obj.data if original_id == source_obj.data else original_id
                for field in ('data_path', 'bone_target', 'transform_type', 'transform_space', 'rotation_mode', 'use_fallback_value', 'fallback_value'):
                    if hasattr(original, field):
                        setattr(copied, field, getattr(original, field))
        driver.expression = curve.driver.expression
        for modifier in list(new_curve.modifiers):
            new_curve.modifiers.remove(modifier)
        for modifier in curve.modifiers:
            _copy_rna(modifier, new_curve.modifiers.new(modifier.type))
        if curve.keyframe_points:
            new_curve.keyframe_points.add(len(curve.keyframe_points))
            for original, copied in zip(curve.keyframe_points, new_curve.keyframe_points):
                _copy_rna(original, copied)
        new_curve.update()


def transfer(source, target):
    """Interpolate weights and basis-relative offsets on the final reduced topology."""
    keys = source.data.shape_keys
    basis = [item.co.copy() for item in keys.key_blocks[0].data] if keys else [v.co.copy() for v in source.data.vertices]
    source.data.calc_loop_triangles()
    triangles = [tuple(triangle.vertices) for triangle in source.data.loop_triangles
                 if (basis[triangle.vertices[1]] - basis[triangle.vertices[0]]).cross(basis[triangle.vertices[2]] - basis[triangle.vertices[0]]).length_squared > 1e-20]
    if not triangles:
        raise ValueError('No usable source surface for deformation transfer.')
    tree = BVHTree.FromPolygons(basis, triangles, all_triangles=True)
    mapping = []
    max_distance = 0.0
    for vertex in target.data.vertices:
        position, _, index, distance = tree.find_nearest(vertex.co)
        if position is None or index is None:
            raise ValueError('Unable to map a remeshed vertex to the source surface.')
        indices = triangles[index]
        weights = geometry.barycentric_transform(position, *(basis[i] for i in indices),
            Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1)))
        weights = [max(0.0, min(1.0, w)) for w in weights]
        total = sum(weights)
        if total <= 1e-12:
            raise ValueError('Invalid source triangle interpolation.')
        mapping.append((indices, [w / total for w in weights]))
        max_distance = max(max_distance, distance)

    target.vertex_groups.clear()
    groups = [target.vertex_groups.new(name=group.name) for group in source.vertex_groups]
    source_weights = [{entry.group: entry.weight for entry in vertex.groups} for vertex in source.data.vertices]
    for vertex, (indices, weights) in zip(target.data.vertices, mapping):
        mixed = {}
        for index, factor in zip(indices, weights):
            for group, weight in source_weights[index].items():
                mixed[group] = mixed.get(group, 0.0) + factor * weight
        for group, weight in mixed.items():
            if weight > 1e-8:
                groups[group].add([vertex.index], min(1.0, max(0.0, weight)), 'REPLACE')
    for original, copied in zip(source.vertex_groups, groups):
        copied.lock_weight = original.lock_weight

    if keys:
        blocks = {}
        for original in keys.key_blocks:
            copied = target.shape_key_add(name=original.name, from_mix=False)
            blocks[original.name] = copied
            if original != keys.key_blocks[0]:
                for vertex, (indices, weights) in zip(target.data.vertices, mapping):
                    offset = sum(((original.data[i].co - basis[i]) * w for i, w in zip(indices, weights)), Vector((0, 0, 0)))
                    copied.data[vertex.index].co = vertex.co + offset
            copied.interpolation = original.interpolation
            copied.vertex_group = original.vertex_group
            copied.mute = original.mute
            copied.slider_min = min(copied.slider_min, original.slider_min)
            copied.slider_max = max(copied.slider_max, original.slider_max)
            copied.slider_min = original.slider_min
            copied.slider_max = original.slider_max
            copied.value = original.value
        for original in keys.key_blocks:
            blocks[original.name].relative_key = blocks[original.relative_key.name]
        target.data.shape_keys.use_relative = True
        _copy_key_animation(source, target)

    for original in source.modifiers:
        if original.type == 'ARMATURE':
            copied = target.modifiers.new(original.name, 'ARMATURE')
            _copy_rna(original, copied, excluded=('name',))
    target.data.update()
    return len(groups), len(keys.key_blocks) - 1 if keys else 0, max_distance


def signature(obj):
    """Include unposed deformation data so animation playback is not a manual mesh edit."""
    digest = hashlib.sha256()
    for group in obj.vertex_groups:
        digest.update(repr((group.name, group.lock_weight)).encode())
    for vertex in obj.data.vertices:
        for assignment in vertex.groups:
            digest.update(struct.pack('<IIf', vertex.index, assignment.group, assignment.weight))
    keys = obj.data.shape_keys
    if keys:
        digest.update(str(keys.use_relative).encode())
        for block in keys.key_blocks:
            digest.update(repr((block.name, block.relative_key.name, block.vertex_group, block.mute, block.slider_min, block.slider_max, block.interpolation)).encode())
            if not keys.animation_data:
                digest.update(str(block.value).encode())
            for point in block.data:
                digest.update(struct.pack('<3f', *point.co))
        animation = keys.animation_data
        if animation:
            digest.update(repr((animation.action.name_full if animation.action else '', animation.action_blend_type, animation.action_influence, animation.action_extrapolation, animation.use_nla)).encode())
            curves = list(animation.drivers) + (list(animation.action.fcurves) if animation.action else [])
            for curve in curves:
                digest.update(repr((curve.data_path, curve.array_index, curve.mute, curve.extrapolation)).encode())
                for point in curve.keyframe_points:
                    digest.update(repr((tuple(point.co), tuple(point.handle_left), tuple(point.handle_right), point.interpolation, point.handle_left_type, point.handle_right_type, point.easing, point.amplitude, point.back, point.period)).encode())
                for modifier in curve.modifiers:
                    digest.update(repr([(prop.identifier, repr(getattr(modifier, prop.identifier))) for prop in modifier.bl_rna.properties if prop.identifier != "rna_type" and not prop.is_readonly]).encode())
                if curve in animation.drivers[:]:
                    digest.update(repr((curve.driver.type, curve.driver.expression, curve.driver.use_self)).encode())
                    for variable in curve.driver.variables:
                        digest.update(repr((variable.name, variable.type)).encode())
                        for target in variable.targets:
                            digest.update(repr((target.id.name_full if target.id else '', target.data_path, target.bone_target, target.transform_type, target.transform_space)).encode())
    for modifier in obj.modifiers:
        if modifier.type == 'ARMATURE':
            digest.update(repr([(prop.identifier, repr(getattr(modifier, prop.identifier))) for prop in modifier.bl_rna.properties
                               if prop.identifier not in {'rna_type', 'execution_time'} and not prop.is_readonly]).encode())
    return digest.digest()
