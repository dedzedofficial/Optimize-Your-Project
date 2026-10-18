# SPDX-License-Identifier: GPL-3.0-or-later
"""v0.8.8 source-preserving Smart Optimize and guarded PBR atlas extension."""
import bpy
from bpy.props import BoolProperty, EnumProperty

from . import v08_tools as _v08

_ORIGINAL_BAKE = None


def _principled_graphs(obj):
    """Only handle graphs that directly output a Principled shader."""
    graphs = []
    seen = set()
    for slot in obj.material_slots:
        mat = slot.material
        if mat is None:
            raise ValueError("Every material slot must have a material for PBR atlas baking.")
        if mat.as_pointer() in seen:
            continue
        seen.add(mat.as_pointer())
        if not mat.use_nodes or not mat.node_tree:
            raise ValueError("Use node-based Principled materials before PBR merging.")
        nodes = mat.node_tree.nodes
        shader = next((node for node in nodes if node.type == 'BSDF_PRINCIPLED'), None)
        output = next((node for node in nodes if node.type == 'OUTPUT_MATERIAL' and node.is_active_output), None)
        if not shader or not output or not output.inputs['Surface'].is_linked:
            raise ValueError("PBR atlases require a connected Principled BSDF material.")
        if output.inputs['Surface'].links[0].from_node != shader:
            raise ValueError("Complex mixed/transparent shader graphs are not safely supported for PBR atlas baking.")
        graphs.append((mat, shader, output))
    if not graphs:
        raise ValueError("No compatible materials were found for PBR atlas baking.")
    return graphs


def _channel_needed(graphs, socket_name, threshold=1.0e-5):
    values = []
    for _, bsdf, _ in graphs:
        socket = bsdf.inputs.get(socket_name)
        if socket is None:
            return False
        if socket.is_linked:
            return True
        value = socket.default_value
        if hasattr(value, '__len__'):
            value = tuple(round(float(item), 5) for item in value[:3])
        else:
            value = round(float(value), 5)
        values.append(value)
    return any(value != values[0] for value in values[1:])


def _new_image(obj, label, size, data=True):
    image = bpy.data.images.new(
        name=obj.name + "_Atlas_" + label, width=size, height=size,
        alpha=False, float_buffer=False)
    if data:
        image.colorspace_settings.name = 'Non-Color'
    return image


def _bake_extra_channel(obj, context, graphs, image, socket_name=None, normal=False):
    """Bake a scalar channel through temporary Emission nodes; restore every graph."""
    temporary = []
    scene = context.scene
    old_engine = scene.render.engine
    old_margin = scene.render.bake.margin
    old_samples = scene.cycles.samples
    try:
        scene.cycles.samples = min(old_samples, 16)
        for mat, shader, output in graphs:
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            active = nodes.active
            old_surface = [(link.from_socket, link.to_socket)
                           for link in output.inputs['Surface'].links]
            tex = nodes.new('ShaderNodeTexImage')
            tex.image = image
            nodes.active = tex
            emission = None
            temporary.append((mat, tex, active, emission, old_surface))
            if not normal:
                emission = nodes.new('ShaderNodeEmission')
                socket = shader.inputs.get(socket_name)
                if socket is None:
                    raise ValueError("Unsupported shader channel: " + socket_name)
                if socket.is_linked:
                    links.new(socket.links[0].from_socket, emission.inputs['Color'])
                else:
                    value = socket.default_value
                    if hasattr(value, '__len__'):
                        emission.inputs['Color'].default_value = tuple(value)
                    else:
                        scalar = float(value)
                        emission.inputs['Color'].default_value = (scalar, scalar, scalar, 1.0)
                links.new(emission.outputs['Emission'], output.inputs['Surface'])
                temporary[-1] = (mat, tex, active, emission, old_surface)

        scene.render.engine = 'CYCLES'
        scene.render.bake.margin = max(4, int(image.size[0] / 128))
        _v08._activate_only(context, obj)
        if normal:
            bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT', use_clear=True)
        else:
            bpy.ops.object.bake(type='EMIT', use_clear=True)
        image.pack()
    finally:
        scene.render.engine = old_engine
        scene.render.bake.margin = old_margin
        scene.cycles.samples = old_samples
        for mat, tex, active, emission, old_surface in temporary:
            links = mat.node_tree.links
            nodes = mat.node_tree.nodes
            if emission and emission.name in nodes:
                nodes.remove(emission)
                for source, destination in old_surface:
                    links.new(source, destination)
            if tex.name in nodes:
                nodes.remove(tex)
            if active and active.name in nodes:
                nodes.active = active


def _bake_pbr_atlas(obj, context, size=2048):
    """Wrap the existing colour bake with selected PBR channels on private copies."""
    graphs = _principled_graphs(obj)
    channels = (
        ('Roughness', 'Roughness', 'Roughness'),
        ('Metallic', 'Metallic', 'Metallic'),
        ('Alpha', 'Alpha', 'Alpha'),
        ('Emission', 'Emission Color', 'Emission Color'),
        ('Normal', 'Normal', None),
    )
    strengths = [
        float(shader.inputs['Emission Strength'].default_value)
        for _, shader, _ in graphs if shader.inputs.get('Emission Strength')
    ]
    if len({round(strength, 5) for strength in strengths}) > 1:
        raise ValueError("Different Emission Strength values require separate materials; PBR merge skipped.")
    baked = {}
    created = []
    try:
        for label, socket, output_input in channels:
            if label == 'Normal':
                needed = any(shader.inputs.get('Normal') and
                             shader.inputs['Normal'].is_linked
                             for _, shader, _ in graphs)
            elif label == 'Emission':
                needed = _channel_needed(graphs, socket) or any(
                    shader.inputs.get('Emission Strength') and
                    float(shader.inputs['Emission Strength'].default_value) > 0.0
                    for _, shader, _ in graphs)
            else:
                needed = _channel_needed(graphs, socket)
            if not needed:
                continue
            image = _new_image(obj, label, size)
            created.append(image)
            _bake_extra_channel(obj, context, graphs, image,
                                socket_name=socket if label != 'Normal' else None,
                                normal=(label == 'Normal'))
            baked[label] = image

        base_image, atlas_material = _ORIGINAL_BAKE(obj, context, size)
        shader = atlas_material.node_tree.nodes.get('Principled BSDF')
        nodes = atlas_material.node_tree.nodes
        links = atlas_material.node_tree.links
        if shader:
            first = graphs[0][1]
            for label, socket, output_input in channels:
                if label in baked:
                    image = baked[label]
                    tex = nodes.new('ShaderNodeTexImage')
                    tex.image = image
                    tex.label = label + ' Atlas'
                    if label == 'Normal':
                        normal_map = nodes.new('ShaderNodeNormalMap')
                        normal_map.uv_map = 'AtlasUV'
                        links.new(tex.outputs['Color'], normal_map.inputs['Color'])
                        links.new(normal_map.outputs['Normal'], shader.inputs['Normal'])
                    elif label == 'Alpha':
                        separate = nodes.new('ShaderNodeSeparateColor')
                        links.new(tex.outputs['Color'], separate.inputs['Color'])
                        links.new(separate.outputs['Red'], shader.inputs['Alpha'])
                    elif label == 'Emission':
                        links.new(tex.outputs['Color'], shader.inputs['Emission Color'])
                        strength = first.inputs.get('Emission Strength')
                        if strength:
                            shader.inputs['Emission Strength'].default_value = float(strength.default_value)
                    else:
                        separate = nodes.new('ShaderNodeSeparateColor')
                        links.new(tex.outputs['Color'], separate.inputs['Color'])
                        links.new(separate.outputs['Red'], shader.inputs[output_input])
                else:
                    value = first.inputs.get(socket)
                    target = shader.inputs.get(output_input) if output_input else None
                    if value and target and not value.is_linked:
                        target.default_value = value.default_value
            if 'Alpha' in baked and hasattr(atlas_material, 'surface_render_method'):
                atlas_material.surface_render_method = 'DITHERED'
        obj['fishhwb_pbr_atlas_channels'] = ', '.join(['Base Color'] + list(baked.keys()))
        obj['fishhwb_pbr_atlas_images'] = ', '.join(
            [base_image.name] + [image.name for image in baked.values()])
        return base_image, atlas_material
    except Exception:
        for image in created:
            if image.name in bpy.data.images and image.users == 0:
                bpy.data.images.remove(image)
        raise


class FISHHWB_OT_smart_optimize(bpy.types.Operator):
    bl_idname = 'fishhwb.smart_optimize'
    bl_label = 'Smart Optimize'
    bl_description = 'Preview and coordinate existing safe optimizers on preserved copies of selected meshes'
    bl_options = {'REGISTER', 'UNDO'}

    clean_geometry: BoolProperty(
        name='Clean Geometry', default=False,
        description='Create a private cleaned copy of each supported static mesh')
    remesh: BoolProperty(
        name='Remesh if Above Triangle Target', default=True,
        description='Use the existing source-preserving Remesh operation when needed')
    lods: BoolProperty(
        name='Generate LODs', default=True,
        description='Generate LOD0, LOD1 and LOD2 for static optimized meshes')
    atlas: BoolProperty(
        name='Merge PBR Textures', default=False,
        description='Bake a material atlas only when explicitly selected; may take time')
    lightmap: BoolProperty(
        name='Generate Lightmap UV', default=False,
        description='Generate a secondary lightmap UV channel on the optimized output')

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(
            ob.type == 'MESH' for ob in context.selected_objects)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=450)

    def draw(self, context):
        layout = self.layout
        meshes = [obj for obj in context.selected_objects if obj.type == 'MESH']
        triangles = sum(
            sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons)
            for obj in meshes)
        layout.label(text=f'{len(meshes)} selected mesh(es); about {triangles:,} triangles', icon='INFO')
        layout.label(text='Original objects stay untouched; optional jobs are independent.')
        layout.prop(self, 'clean_geometry')
        layout.prop(self, 'remesh')
        layout.prop(self, 'lods')
        layout.prop(self, 'atlas')
        layout.prop(self, 'lightmap')
        layout.label(text='Complex, rigged or protected meshes may be skipped.', icon='ERROR')

    def execute(self, context):
        if not any((self.clean_geometry, self.remesh, self.lods, self.atlas, self.lightmap)):
            self.report({'WARNING'}, 'No optimization actions selected.')
            return {'CANCELLED'}
        from . import _static_mesh_reason, _copy_mesh_object, _remove_object_and_mesh, _select_only
        from . import triangle_count
        selected = list(dict.fromkeys(
            obj for obj in context.selected_objects if obj.type == 'MESH'))
        results = []
        optimized = []
        completed, skipped, failed = 0, 0, 0
        for source in selected:
            if (source.library or source.data.library or
                    getattr(source, 'fishhwb_protect_detail', False)):
                skipped += 1
                results.append(source.name + ': linked/protected')
                continue
            current = source
            jobs = []
            try:
                if self.clean_geometry and not _v08._has_deformation(current):
                    clean = _copy_mesh_object(current, context, '_Clean')
                    if _v08._repair_static_mesh(clean.data, fill_holes=False):
                        current = clean
                        current['fishhwb_generated_job'] = 'smart_clean'
                        jobs.append('clean')
                    else:
                        _remove_object_and_mesh(clean)
                if self.remesh and triangle_count(current.data) > context.scene.fishhwb_triangle_target:
                    _select_only(context, current)
                    if 'FINISHED' in bpy.ops.fishhwb.one_click_remesh():
                        current = context.active_object
                        jobs.append('remesh')
                    else:
                        results.append(source.name + ': remesh skipped/rejected')
                if self.atlas and any(slot.material for slot in current.material_slots):
                    _select_only(context, current)
                    if 'FINISHED' in bpy.ops.fishhwb.merge_textures():
                        current = context.active_object
                        jobs.append('atlas')
                if self.lightmap and not _v08._has_deformation(current):
                    lightmap_copy = None
                    if current is source:
                        lightmap_copy = _copy_mesh_object(source, context, '_OptimizedUV')
                        lightmap_copy['fishhwb_generated_job'] = 'smart_lightmap'
                        current = lightmap_copy
                    _select_only(context, current)
                    if 'FINISHED' in bpy.ops.fishhwb.generate_lightmap_uv():
                        jobs.append('lightmap UV')
                    elif lightmap_copy is not None:
                        _remove_object_and_mesh(lightmap_copy)
                        current = source
                if self.lods and not _v08._has_deformation(current):
                    if _static_mesh_reason(current) is None:
                        _select_only(context, current)
                        if 'FINISHED' in bpy.ops.fishhwb.create_lods():
                            current = context.active_object
                            jobs.append('LODs')
                if jobs:
                    optimized.append(current)
                    completed += 1
                else:
                    skipped += 1
                results.append(source.name + ': ' + (', '.join(jobs) or 'no safe changes'))
            except Exception as exc:
                failed += 1
                results.append(source.name + ': error: ' + str(exc))
        for item in list(context.selected_objects):
            item.select_set(False)
        for obj in optimized:
            if obj and obj.name in bpy.data.objects:
                obj.select_set(True)
        if optimized:
            context.view_layer.objects.active = optimized[0]
        elif selected:
            for obj in selected:
                if obj.name in bpy.data.objects:
                    obj.select_set(True)
            context.view_layer.objects.active = selected[0]
        summary = (f'Smart Optimize: {completed} optimized, {skipped} unchanged/unsupported, '
                   f'{failed} failed. Original sources preserved. ' + '; '.join(results))
        context.scene.fishhwb_last_result = summary
        self.report({'WARNING'} if failed or skipped else {'INFO'}, summary[:900])
        return {'FINISHED'} if completed else {'CANCELLED'}


classes = (FISHHWB_OT_smart_optimize,)


def register(addon):
    global _ORIGINAL_BAKE
    if _ORIGINAL_BAKE is None:
        _ORIGINAL_BAKE = _v08._bake_material_atlas
    _v08._bake_material_atlas = _bake_pbr_atlas
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.fishhwb_atlas_size = EnumProperty(
        name='Atlas Resolution',
        items=(('1024', '1024', 'Fast and compact'),
               ('2048', '2048', 'Balanced'),
               ('4096', '4096', 'High detail and higher memory use')),
        default='2048')


def unregister():
    global _ORIGINAL_BAKE
    if hasattr(bpy.types.Scene, 'fishhwb_atlas_size'):
        del bpy.types.Scene.fishhwb_atlas_size
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if _ORIGINAL_BAKE is not None:
        _v08._bake_material_atlas = _ORIGINAL_BAKE
        _ORIGINAL_BAKE = None
