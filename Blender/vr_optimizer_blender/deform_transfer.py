# SPDX-License-Identifier: GPL-3.0-or-later
"""Topology-correspondent transfer of remesh deformation data."""
import hashlib
import struct
import uuid

import bpy


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
    attributes = []
    if keys:
        for block in list(keys.key_blocks)[1:]:
            attribute = target.data.attributes.new(
                name="fishhwb_shape_" + uuid.uuid4().hex, type='FLOAT_VECTOR', domain='POINT')
            attribute.data.foreach_set('vector', [component for i, item in enumerate(block.data)
                                                 for component in (item.co - basis[i])])
            attributes.append(attribute.name)
    return attributes


def _copy_rna(source, target, excluded=()):
    for prop in source.bl_rna.properties:
        name = prop.identifier
        if name in {'rna_type', 'type', *excluded} or prop.is_readonly:
            continue
        value = getattr(source, name)
        if prop.type == 'COLLECTION':
            raise ValueError('Unsupported animated property collection: ' + name)
        setattr(target, name, list(value) if getattr(prop, "is_array", False) else value)


def _action_fcurves(animation):
    """Return action curves on Blender 4.2 legacy actions or 4.4+ slotted actions."""
    action = animation.action if animation else None
    if not action:
        return []
    if hasattr(action, 'fcurves'):
        return list(action.fcurves)

    slot = getattr(animation, 'action_slot', None)
    if slot is None:
        return []
    try:
        from bpy_extras import anim_utils
        channelbag = anim_utils.action_get_channelbag_for_slot(action, slot)
    except (ImportError, AttributeError, RuntimeError):
        channelbag = None
    return list(channelbag.fcurves) if channelbag else []


def _restore_copied_action_slot(source_animation, destination_animation):
    """Keep a copied slotted Action bound to the corresponding copied slot."""
    source_slot = getattr(source_animation, 'action_slot', None)
    copied_action = destination_animation.action
    if source_slot is None or not copied_action or not hasattr(destination_animation, 'action_slot'):
        return
    slots = getattr(copied_action, 'slots', None)
    if slots is None:
        return
    copied_slot = next(
        (slot for slot in slots if getattr(slot, 'identifier', None) == getattr(source_slot, 'identifier', None)),
        None,
    )
    if copied_slot is not None:
        destination_animation.action_slot = copied_slot


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
        destination.action = animation.action.copy()
        destination.action['fishhwb_owned_transfer'] = True
        _restore_copied_action_slot(animation, destination)
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


def transfer(source, target, attributes):
    """Restore offsets carried through reduction, without nearest-surface guesses."""
    keys = source.data.shape_keys
    expected = len(keys.key_blocks) - 1 if keys else 0
    if len(attributes) != expected:
        raise ValueError('Missing blendshape correspondence data.')
    offsets = []
    for name in attributes:
        attribute = target.data.attributes.get(name)
        if attribute is None or attribute.domain != 'POINT' or attribute.data_type != 'FLOAT_VECTOR':
            raise ValueError('Reduction lost blendshape correspondence; output discarded.')
        offsets.append([item.vector.copy() for item in attribute.data])
    groups = list(target.vertex_groups)
    if [g.name for g in groups] != [g.name for g in source.vertex_groups]:
        raise ValueError('Reduction lost vertex-group correspondence.')
    for original, copied in zip(source.vertex_groups, groups):
        copied.lock_weight = original.lock_weight

    if keys:
        blocks = {}
        for key_index, original in enumerate(keys.key_blocks):
            copied = target.shape_key_add(name=original.name, from_mix=False)
            blocks[original.name] = copied
            if original != keys.key_blocks[0]:
                for vertex, offset in zip(target.data.vertices, offsets[key_index - 1]):
                    copied.data[vertex.index].co = vertex.co + offset
            copied.interpolation = original.interpolation
            copied.vertex_group = original.vertex_group
            copied.mute = original.mute
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
    for name in attributes:
        target.data.attributes.remove(target.data.attributes[name])
    target.data.update()
    return len(groups), expected


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
            slot = getattr(animation, 'action_slot', None)
            digest.update(repr((
                animation.action.name_full if animation.action else '',
                getattr(slot, 'identifier', ''),
                animation.action_blend_type,
                animation.action_influence,
                animation.action_extrapolation,
                animation.use_nla,
            )).encode())
            drivers = list(animation.drivers)
            driver_pointers = {curve.as_pointer() for curve in drivers}
            curves = drivers + _action_fcurves(animation)
            for curve in curves:
                digest.update(repr((curve.data_path, curve.array_index, curve.mute, curve.extrapolation)).encode())
                for point in curve.keyframe_points:
                    digest.update(repr((tuple(point.co), tuple(point.handle_left), tuple(point.handle_right), point.interpolation, point.handle_left_type, point.handle_right_type, point.easing, point.amplitude, point.back, point.period)).encode())
                for modifier in curve.modifiers:
                    digest.update(repr([(prop.identifier, repr(getattr(modifier, prop.identifier))) for prop in modifier.bl_rna.properties if prop.identifier != "rna_type" and not prop.is_readonly]).encode())
                if curve.as_pointer() in driver_pointers:
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
