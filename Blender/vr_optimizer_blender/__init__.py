bl_info = {
    "name": "Optimize Your Project for Blender",
    "author": "FISHHWB | Ded Zed",
    "version": (0, 7, 4),
    "blender": (3, 6, 0),
    "location": "View3D > Sidebar > FISHHWB",
    "description": "Multilingual one-click and batch mesh optimization with cleanup, LOD and review tools",
    "category": "Mesh",
}

import bpy
import bmesh
import math
from pathlib import Path
import bpy.utils.previews
from array import array
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, StringProperty

_brand_preview = None

LANGUAGE_ITEMS = (
    ('EN', 'English', 'English'),
    ('JA', '日本語', 'Japanese'),
    ('ZH', '简体中文', 'Chinese (Simplified)'),
    ('KO', '한국어', 'Korean'),
)

_TRANSLATIONS = {
    'language': {'EN': 'Language', 'JA': '言語', 'ZH': '语言', 'KO': '언어'},
    'title': {'EN': 'OPTIMIZE YOUR PROJECT', 'JA': 'プロジェクトを最適化', 'ZH': '优化你的项目', 'KO': '프로젝트 최적화'},
    'subtitle': {'EN': 'Free one-click tools for developers', 'JA': '開発者向け無料ワンクリックツール', 'ZH': '面向开发者的免费一键工具', 'KO': '개발자를 위한 무료 원클릭 도구'},
    'selection': {'EN': 'CURRENT SELECTION', 'JA': '現在の選択', 'ZH': '当前选择', 'KO': '현재 선택'},
    'select_mesh': {'EN': 'Select one or more mesh objects to begin', 'JA': '開始するには1つ以上のメッシュを選択', 'ZH': '请选择一个或多个网格对象', 'KO': '시작하려면 하나 이상의 메시 오브젝트를 선택하세요'},
    'quick': {'EN': 'ONE-CLICK CLEANUP', 'JA': 'ワンクリッククリーンアップ', 'ZH': '一键清理', 'KO': '원클릭 정리'},
    'quick_desc': {'EN': 'Fast, safe actions that create new copies.', 'JA': '新しいコピーを作成する安全で高速な処理です。', 'ZH': '快速、安全，并创建新副本。', 'KO': '새 복사본을 만드는 빠르고 안전한 작업입니다.'},
    'clean_one': {'EN': 'CLEAN ACTIVE MESH', 'JA': 'アクティブメッシュをクリーン', 'ZH': '清理活动网格', 'KO': '활성 메시 정리'},
    'clean_many': {'EN': 'CLEAN SELECTED MESHES', 'JA': '選択メッシュを一括クリーン', 'ZH': '批量清理所选网格', 'KO': '선택 메시 일괄 정리'},
    'game_ready': {'EN': 'CREATE GAME-READY COPY', 'JA': 'ゲーム用コピーを作成', 'ZH': '创建游戏就绪副本', 'KO': '게임용 복사본 만들기'},
    'remesh': {'EN': 'ONE-CLICK REMESH', 'JA': 'ワンクリックリメッシュ', 'ZH': '一键重网格', 'KO': '원클릭 리메시'},
    'merge': {'EN': 'MERGE DUPLICATE VERTICES', 'JA': '重複頂点をマージ', 'ZH': '合并重复顶点', 'KO': '중복 정점 병합'},
    'batch': {'EN': 'BATCH MESH PREP', 'JA': 'メッシュ一括準備', 'ZH': '批量网格准备', 'KO': '메시 일괄 준비'},
    'batch_desc': {'EN': 'Prepare several static meshes without replacing the originals.', 'JA': '元データを置き換えずに複数の静的メッシュを準備します。', 'ZH': '在不替换原始对象的情况下准备多个静态网格。', 'KO': '원본을 교체하지 않고 여러 정적 메시를 준비합니다.'},
    'batch_lods': {'EN': 'CREATE LODS FOR SELECTION', 'JA': '選択メッシュの LOD を作成', 'ZH': '为所选网格创建 LOD', 'KO': '선택 메시 LOD 생성'},
    'heavy': {'EN': 'SHOW HEAVY MESHES', 'JA': '重いメッシュを表示', 'ZH': '显示高开销网格', 'KO': '무거운 메시 표시'},
    'heavy_limit': {'EN': 'Heavy Triangle Limit', 'JA': '重いメッシュの三角形しきい値', 'ZH': '高开销网格三角形阈值', 'KO': '무거운 메시 삼각형 기준'},
    'more_tools': {'EN': 'MORE TOOLS', 'JA': 'その他のツール', 'ZH': '更多工具', 'KO': '추가 도구'},
    'advanced_toggle': {'EN': 'Show Advanced Mesh Tools', 'JA': '高度なメッシュツールを表示', 'ZH': '显示高级网格工具', 'KO': '고급 메시 도구 표시'},
    'tri_reduce': {'EN': 'Triangle Reduction', 'JA': '三角形削減', 'ZH': '三角形缩减', 'KO': '삼각형 감소'},
    'reduced_copy': {'EN': 'CREATE REDUCED COPY', 'JA': '削減コピーを作成', 'ZH': '创建缩减副本', 'KO': '감소된 복사본 생성'},
    'join_atlas': {'EN': 'Join + Atlas', 'JA': '結合 + アトラス', 'ZH': '合并 + 图集', 'KO': '결합 + 아틀라스'},
    'join': {'EN': 'JOIN SELECTED MESHES', 'JA': '選択メッシュを結合', 'ZH': '合并所选网格', 'KO': '선택 메시 결합'},
    'static_lods': {'EN': 'Static Mesh LODs', 'JA': '静的メッシュ LOD', 'ZH': '静态网格 LOD', 'KO': '정적 메시 LOD'},
    'create_lods': {'EN': 'CREATE LOD0 / LOD1 / LOD2', 'JA': 'LOD0 / LOD1 / LOD2 を作成', 'ZH': '创建 LOD0 / LOD1 / LOD2', 'KO': 'LOD0 / LOD1 / LOD2 생성'},
    'last_result': {'EN': 'LAST RESULT', 'JA': '最後の結果', 'ZH': '上次结果', 'KO': '마지막 결과'},
    'free': {'EN': 'FREE FOR DEVELOPERS', 'JA': '開発者向け無料ツール', 'ZH': '面向开发者免费', 'KO': '개발자 무료 도구'},
    'free_1': {'EN': 'Built to save time and reduce repetitive optimization work.', 'JA': '時間を節約し、反復的な最適化作業を減らすためのツールです。', 'ZH': '用于节省时间并减少重复的优化工作。', 'KO': '시간을 절약하고 반복적인 최적화 작업을 줄이기 위한 도구입니다.'},
    'free_2': {'EN': 'Optional Patreon support funds new tools, tests and documentation.', 'JA': '任意の Patreon 支援は新機能、テスト、文書作成に使われます。', 'ZH': '可选 Patreon 支持将用于新工具、测试和文档。', 'KO': '선택적인 Patreon 후원은 새 도구, 테스트 및 문서에 사용됩니다.'},
    'free_3': {'EN': 'The project stays free either way.', 'JA': '支援の有無にかかわらず無料です。', 'ZH': '无论是否支持，本项目都会保持免费。', 'KO': '후원 여부와 관계없이 무료로 유지됩니다.'},
    'support': {'EN': 'SUPPORT DEVELOPMENT ON PATREON', 'JA': 'PATREON で開発を支援', 'ZH': '在 PATREON 支持开发', 'KO': 'PATREON에서 개발 후원'},
    'merge_distance': {'EN': 'Merge Distance', 'JA': 'マージ距離', 'ZH': '合并距离', 'KO': '병합 거리'},
    'triangle_limit': {'EN': 'Triangle Limit', 'JA': '三角形上限', 'ZH': '三角形上限', 'KO': '삼각형 제한'},
    'apply_modifiers': {'EN': 'Apply Existing Modifiers', 'JA': '既存モディファイアを適用', 'ZH': '应用现有修改器', 'KO': '기존 모디파이어 적용'},
    'make_atlas': {'EN': 'Merge Base Color Textures + UVs', 'JA': 'ベースカラーテクスチャ + UV を統合', 'ZH': '合并基础颜色纹理 + UV', 'KO': '베이스 컬러 텍스처 + UV 병합'},
    'atlas_size': {'EN': 'Atlas Size', 'JA': 'アトラスサイズ', 'ZH': '图集尺寸', 'KO': '아틀라스 크기'},
    'padding': {'EN': 'Padding (Pixels)', 'JA': 'パディング（ピクセル）', 'ZH': '边距（像素）', 'KO': '패딩(픽셀)'},
}

def tr(context, key):
    lang = getattr(context.scene, 'fishhwb_language', 'EN') if context and context.scene else 'EN'
    values = _TRANSLATIONS.get(key, {})
    return values.get(lang, values.get('EN', key))



def triangle_count(mesh):
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def evaluated_count(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return triangle_count(mesh)
    finally:
        evaluated.to_mesh_clear()


class FISHHWB_OT_tri_limit(bpy.types.Operator):
    bl_idname = "fishhwb.tri_limit"
    bl_label = "Create Reduced Copy"
    bl_description = "Duplicate the active mesh and reduce its triangle count"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        source = context.active_object
        limit = context.scene.fishhwb_tri_limit
        before = triangle_count(source.data)
        if before == 0:
            self.report({'ERROR'}, "The source mesh has no triangles")
            return {'CANCELLED'}

        copy = source.copy()
        copy.data = source.data.copy()
        copy.name = source.name + "_TriLimit"
        context.collection.objects.link(copy)
        copy.matrix_world = source.matrix_world.copy()

        # Apply existing modifiers to the copy only, when requested.
        if context.scene.fishhwb_apply_modifiers:
            depsgraph = context.evaluated_depsgraph_get()
            evaluated = copy.evaluated_get(depsgraph)
            try:
                result = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
            except Exception as exc:
                bpy.data.objects.remove(copy, do_unlink=True)
                self.report({'ERROR'}, "Could not evaluate modifiers: " + str(exc))
                return {'CANCELLED'}
            old_mesh = copy.data
            copy.modifiers.clear()
            copy.data = result
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)

        before = triangle_count(copy.data)
        if before > limit:
            modifier = copy.modifiers.new("Triangle Limit", 'DECIMATE')
            modifier.decimate_type = 'COLLAPSE'
            modifier.use_collapse_triangulate = True
            depsgraph = context.evaluated_depsgraph_get()
            low, high = 0.0, 1.0
            best_ratio = None
            best_count = -1
            for i in range(24):
                ratio = (low + high) * 0.5
                modifier.ratio = ratio
                context.view_layer.update()
                count = evaluated_count(copy, depsgraph)
                if count <= limit:
                    if count > best_count:
                        best_count, best_ratio = count, ratio
                    low = ratio
                else:
                    high = ratio
            if best_ratio is None or best_count == 0:
                bpy.data.objects.remove(copy, do_unlink=True)
                self.report({'ERROR'}, "This mesh cannot retain any triangles at that limit")
                return {'CANCELLED'}
            modifier.ratio = best_ratio
            context.view_layer.update()
            evaluated = copy.evaluated_get(depsgraph)
            result = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
            final_count = triangle_count(result)
            if final_count > limit:
                bpy.data.meshes.remove(result)
                bpy.data.objects.remove(copy, do_unlink=True)
                self.report({'ERROR'}, "Could not satisfy the requested limit")
                return {'CANCELLED'}
            old_mesh = copy.data
            copy.modifiers.remove(modifier)
            copy.data = result
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)
        else:
            final_count = before

        for obj in context.selected_objects:
            obj.select_set(False)
        copy.select_set(True)
        context.view_layer.objects.active = copy
        self.report({'INFO'}, f"Created {copy.name}: {final_count:,} triangles (limit {limit:,})")
        return {'FINISHED'}


def reduce_copy_to_limit(obj, target, context):
    """Replace only this object's mesh with an evaluated Decimate result."""
    if triangle_count(obj.data) <= target:
        return triangle_count(obj.data)
    modifier = obj.modifiers.new("LOD Triangle Limit", 'DECIMATE')
    modifier.decimate_type = 'COLLAPSE'
    modifier.use_collapse_triangulate = True
    depsgraph = context.evaluated_depsgraph_get()
    low, high = 0.0, 1.0
    best_ratio, best_count = None, -1
    for _ in range(24):
        ratio = (low + high) * 0.5
        modifier.ratio = ratio
        context.view_layer.update()
        count = evaluated_count(obj, depsgraph)
        if count <= target:
            if count > best_count:
                best_ratio, best_count = ratio, count
            low = ratio
        else:
            high = ratio
    if best_ratio is None or best_count < 1:
        raise ValueError("Unable to preserve a triangle within this LOD limit")
    modifier.ratio = best_ratio
    context.view_layer.update()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = bpy.data.meshes.new_from_object(
        evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
    count = triangle_count(mesh)
    if count < 1 or count > target:
        bpy.data.meshes.remove(mesh)
        raise ValueError("The evaluated LOD did not meet its triangle target")
    old_mesh = obj.data
    obj.modifiers.remove(modifier)
    obj.data = mesh
    if old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)
    return count


class FISHHWB_OT_create_lods(bpy.types.Operator):
    bl_idname = "fishhwb.create_lods"
    bl_label = "Create LOD0 / LOD1 / LOD2"
    bl_description = "Create static mesh copies at 100%, up to 66%, and up to 33% of the original triangle count"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        source = context.active_object
        if source.data.shape_keys or source.vertex_groups or any(m.type == 'ARMATURE' for m in source.modifiers):
            self.report({'ERROR'}, "LOD copies currently support static meshes without shape keys, vertex groups or armature modifiers")
            return {'CANCELLED'}
        original_selection = list(context.selected_objects)
        made = []
        collection = bpy.data.collections.new(source.name + "_LODs")
        context.scene.collection.children.link(collection)
        try:
            base = source.copy()
            base.data = source.data.copy()
            collection.objects.link(base)
            made.append(base)
            base.matrix_world = source.matrix_world.copy()
            base.name = source.name + "_LOD0"
            if context.scene.fishhwb_apply_modifiers:
                depsgraph = context.evaluated_depsgraph_get()
                evaluated = base.evaluated_get(depsgraph)
                mesh = bpy.data.meshes.new_from_object(
                    evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
                old_mesh = base.data
                base.modifiers.clear()
                base.data = mesh
                if old_mesh.users == 0:
                    bpy.data.meshes.remove(old_mesh)
            elif base.modifiers:
                raise ValueError("Enable Apply Existing Modifiers to make measurable LOD meshes")
            count = triangle_count(base.data)
            if count < 1:
                raise ValueError("The selected object has no triangles")
            base['fishhwb_lod_level'] = 0
            for level, fraction in ((1, 0.66), (2, 0.33)):
                copy = base.copy()
                copy.data = base.data.copy()
                collection.objects.link(copy)
                made.append(copy)
                copy.matrix_world = source.matrix_world.copy()
                copy.name = source.name + f"_LOD{level}"
                target = max(1, int(count * fraction))
                actual = reduce_copy_to_limit(copy, target, context)
                copy['fishhwb_lod_level'] = level
                copy['fishhwb_triangle_target'] = target
                copy.hide_set(True)
            for obj in context.selected_objects:
                obj.select_set(False)
            base.select_set(True)
            context.view_layer.objects.active = base
            self.report({'INFO'},
                f"LODs created from {count:,} triangles: LOD1 {triangle_count(made[1].data):,}, LOD2 {triangle_count(made[2].data):,}")
            return {'FINISHED'}
        except Exception as exc:
            for copy in made:
                mesh = copy.data
                bpy.data.objects.remove(copy, do_unlink=True)
                if mesh and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            bpy.data.collections.remove(collection)
            for obj in context.selected_objects:
                obj.select_set(False)
            for obj in original_selection:
                obj.select_set(True)
            context.view_layer.objects.active = source
            self.report({'ERROR'}, "LOD generation failed: " + str(exc))
            return {'CANCELLED'}


def base_color_image(material):
    if not material or not material.use_nodes:
        raise ValueError("Atlas requires node-based materials with direct image Base Color")
    outputs = [n for n in material.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output]
    if not outputs or not outputs[0].inputs['Surface'].is_linked:
        raise ValueError(f"{material.name} has no active surface output")
    shader = outputs[0].inputs['Surface'].links[0].from_node
    if shader.type != 'BSDF_PRINCIPLED':
        raise ValueError(f"{material.name} needs a Principled BSDF")
    color = shader.inputs.get('Base Color')
    if not color or len(color.links) != 1 or color.links[0].from_node.type != 'TEX_IMAGE':
        raise ValueError(f"{material.name} needs an image directly linked to Base Color")
    node = color.links[0].from_node
    if node.inputs['Vector'].is_linked:
        raise ValueError(f"{material.name} uses mapped texture coordinates; atlas skipped")
    image = node.image
    if not image or image.source != 'FILE' or image.size[0] == 0 or image.size[1] == 0:
        raise ValueError(f"{material.name} needs a loaded single-file image")
    if image.tiles and len(image.tiles) > 1:
        raise ValueError(f"{material.name} uses UDIM tiles; atlas skipped")
    if any(inp.is_linked for inp in shader.inputs if inp != color):
        raise ValueError(f"{material.name} uses additional shader maps; baking is needed")
    return image


def build_atlas(obj, material_images, size, padding):
    images = list(dict.fromkeys(material_images.values()))
    cols = math.ceil(math.sqrt(len(images)))
    rows = math.ceil(len(images) / cols)
    tile = min((size - (cols + 1) * padding) // cols,
               (size - (rows + 1) * padding) // rows)
    if tile < 2:
        raise ValueError("Atlas too small for the number of images and padding")
    uv_layer = obj.data.uv_layers.get("FISHHWB_Atlas_UV")
    if not uv_layer:
        raise ValueError("Joined mesh lost its active UV map")
    obj.data.uv_layers.active_index = obj.data.uv_layers.find(uv_layer.name)

    pixels = array('f', [0.0]) * (size * size * 4)
    placements = {}
    for i, image in enumerate(images):
        scaled = image.copy()
        try:
            scaled.scale(tile, tile)
            source_pixels = array('f', scaled.pixels[:])
            x = padding + (i % cols) * (tile + padding)
            y = padding + (i // cols) * (tile + padding)
            for line in range(tile):
                start = ((y + line) * size + x) * 4
                src = line * tile * 4
                pixels[start:start + tile * 4] = source_pixels[src:src + tile * 4]
            placements[image] = (x, y)
        finally:
            bpy.data.images.remove(scaled)

    # Do not rewrite material assignments or UVs until every image was copied.
    atlas = bpy.data.images.new(obj.name + "_BaseColor_Atlas", width=size, height=size, alpha=True)
    atlas.pixels[:] = pixels
    atlas.update()
    atlas_material = bpy.data.materials.new(obj.name + "_Atlas")
    atlas_material.use_nodes = True
    atlas_material.blend_method = 'BLEND'
    nodes = atlas_material.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    tex = nodes.new('ShaderNodeTexImage')
    tex.image = atlas
    atlas_material.node_tree.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    atlas_material.node_tree.links.new(tex.outputs['Alpha'], bsdf.inputs['Alpha'])

    original_slots = [slot.material for slot in obj.material_slots]
    for face in obj.data.polygons:
        material = original_slots[face.material_index]
        image = material_images.get(material)
        if image is None:
            raise ValueError(f"Joined material {material.name if material else '<empty>'} changed unexpectedly")
        x, y = placements[image]
        for index in face.loop_indices:
            uv = uv_layer.data[index].uv
            uv.x = (x + min(1.0, max(0.0, uv.x)) * (tile - 1) + 0.5) / size
            uv.y = (y + min(1.0, max(0.0, uv.y)) * (tile - 1) + 0.5) / size
        face.material_index = 0
    obj.data.materials.clear()
    obj.data.materials.append(atlas_material)


class FISHHWB_OT_join_merge(bpy.types.Operator):
    bl_idname = "fishhwb.join_merge"
    bl_label = "Join Selected and Merge Vertices"
    bl_description = "Create one new mesh from selected meshes and weld nearby vertices"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and len([o for o in context.selected_objects if o.type == 'MESH']) >= 2

    def execute(self, context):
        sources = [o for o in context.selected_objects if o.type == 'MESH']
        if any(o.data.shape_keys for o in sources):
            self.report({'ERROR'}, "Shape keys are not supported by vertex merging; remove them from copies first")
            return {'CANCELLED'}

        make_atlas = context.scene.fishhwb_make_atlas
        material_images = {}
        if make_atlas:
            try:
                for source in sources:
                    if not source.data.uv_layers.active:
                        raise ValueError(f"{source.name} has no active UV map")
                    for poly in source.data.polygons:
                        material = source.material_slots[poly.material_index].material
                        if material not in material_images:
                            material_images[material] = base_color_image(material)
                        for index in poly.loop_indices:
                            uv = source.data.uv_layers.active.data[index].uv
                            if not (-0.00001 <= uv.x <= 1.00001 and -0.00001 <= uv.y <= 1.00001):
                                raise ValueError(f"{source.name} has tiled UVs outside 0–1; atlas skipped")
                if not material_images:
                    raise ValueError("No textured faces found")
                if len(set(material_images.values())) > 64:
                    raise ValueError("Atlas supports up to 64 distinct images")
            except (ValueError, IndexError, AttributeError) as exc:
                self.report({'ERROR'}, str(exc))
                return {'CANCELLED'}

        original_active = context.view_layer.objects.active
        original_selection = list(context.selected_objects)
        copies = []
        try:
            for source in sources:
                copy = source.copy()
                copy.data = source.data.copy()
                context.collection.objects.link(copy)
                copies.append(copy)
                copy.matrix_world = source.matrix_world.copy()
                if make_atlas:
                    # Give each active UV map a common name so Blender's Join combines it.
                    uv = copy.data.uv_layers.active
                    uv.name = "FISHHWB_Atlas_UV"
                    copy.data.uv_layers.active_index = copy.data.uv_layers.find(uv.name)

                if context.scene.fishhwb_apply_modifiers:
                    depsgraph = context.evaluated_depsgraph_get()
                    evaluated = copy.evaluated_get(depsgraph)
                    mesh = bpy.data.meshes.new_from_object(
                        evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
                    old_mesh = copy.data
                    copy.modifiers.clear()
                    copy.data = mesh
                    if old_mesh.users == 0:
                        bpy.data.meshes.remove(old_mesh)

            for obj in context.selected_objects:
                obj.select_set(False)
            for obj in copies:
                obj.select_set(True)
            joined = copies[0]
            context.view_layer.objects.active = joined
            result = bpy.ops.object.join()
            if 'FINISHED' not in result:
                raise RuntimeError("Blender could not join the selected meshes")
            joined.name = "Joined_TriLimit"
            joined.data.name = joined.name

            before = len(joined.data.vertices)
            bm = bmesh.new()
            try:
                bm.from_mesh(joined.data)
                bmesh.ops.remove_doubles(
                    bm, verts=list(bm.verts), dist=context.scene.fishhwb_merge_distance)
                bm.to_mesh(joined.data)
            finally:
                bm.free()
            joined.data.update()
            if make_atlas:
                build_atlas(joined, material_images, context.scene.fishhwb_atlas_size,
                            context.scene.fishhwb_atlas_padding)
            joined.select_set(True)
            context.view_layer.objects.active = joined
            self.report({'INFO'},
                f"Joined {len(sources)} meshes: {before - len(joined.data.vertices):,} vertices merged")
            return {'FINISHED'}
        except Exception as exc:
            for copy in copies:
                if copy.name in bpy.data.objects:
                    mesh = copy.data
                    bpy.data.objects.remove(copy, do_unlink=True)
                    if mesh and mesh.users == 0:
                        bpy.data.meshes.remove(mesh)
            for obj in context.selected_objects:
                obj.select_set(False)
            for obj in original_selection:
                obj.select_set(True)
            context.view_layer.objects.active = original_active
            self.report({'ERROR'}, "Join failed: " + str(exc))
            return {'CANCELLED'}



def _copy_mesh_object(source, context, suffix):
    copy = source.copy()
    mesh = None
    try:
        mesh = source.data.copy()
        copy.data = mesh
        base = source.name + suffix
        name, number = base, 1
        while name in bpy.data.objects:
            name = f"{base}_{number:03d}"
            number += 1
        copy.name = name
        mesh.name = name
        context.collection.objects.link(copy)
        copy.matrix_world = source.matrix_world.copy()
        return copy
    except Exception:
        bpy.data.objects.remove(copy, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        raise


def _action_report(operator, context, detail, changed=0, unchanged=0,
                   skipped=0, unsupported=0, failed=0):
    counts = (f"Changed: {changed} | Unchanged: {unchanged} | Skipped: {skipped} | "
              f"Unsupported: {unsupported} | Failed: {failed}")
    context.scene.fishhwb_last_result = counts + "\n" + detail
    operator.report({'WARNING'} if failed or unsupported else {'INFO'}, counts + ". " + detail)


def _cleanup_unsupported(source):
    if source.data.shape_keys:
        return "Shape keys depend on the original topology."
    if source.vertex_groups or source.find_armature():
        return "Rigged meshes and vertex groups depend on the original topology."
    if source.modifiers:
        return "Apply modifiers to a separate static copy before cleanup."
    if source.data.has_custom_normals:
        return "Custom split normals need a dedicated shading workflow."
    if source.library or source.data.library or source.override_library or source.data.override_library:
        return "Linked or overridden meshes must be made local before cleanup."
    if any(not math.isfinite(value) for vertex in source.data.vertices for value in vertex.co):
        return "Mesh coordinates contain non-finite values."
    if not source.data.vertices:
        return "The mesh has no vertices."
    return None


def _game_ready_unsupported(source, apply_modifiers):
    if source.data.shape_keys:
        return "Shape keys depend on the original topology."
    if source.vertex_groups or source.find_armature() or any(mod.type == 'ARMATURE' for mod in source.modifiers):
        return "Game-ready copy currently supports static meshes without rigs or vertex groups."
    if source.data.has_custom_normals:
        return "Custom split normals need a dedicated shading workflow."
    if source.library or source.data.library or source.override_library or source.data.override_library:
        return "Linked or overridden meshes must be made local first."
    if any(not math.isfinite(value) for vertex in source.data.vertices for value in vertex.co):
        return "Mesh coordinates contain non-finite values."
    if not source.data.vertices:
        return "The mesh has no vertices."
    if source.modifiers and not apply_modifiers:
        return "Enable Apply Existing Modifiers before creating a game-ready copy."
    return None


def _clean_mesh(mesh):
    """Clean only the caller-owned mesh. Keep open surfaces and their winding."""
    stats = dict(vertices=0, loose_edges=0, duplicates=0, zero_faces=0,
                 material_slots=0, normals=0)
    before_vertices = len(mesh.vertices)
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        # Exact coordinates only: no proximity threshold can erase thin details.
        targets, coordinates = {}, {}
        for vertex in bm.verts:
            key = tuple(vertex.co)
            if key in coordinates:
                targets[vertex] = coordinates[key]
            else:
                coordinates[key] = vertex
        count = len(bm.verts)
        if targets:
            bmesh.ops.weld_verts(bm, targetmap=targets)
        stats['duplicates'] = count - len(bm.verts)

        zero_faces = [face for face in bm.faces if face.calc_area() == 0.0]
        stats['zero_faces'] = len(zero_faces)
        if zero_faces:
            bmesh.ops.delete(bm, geom=zero_faces, context='FACES_ONLY')
        loose_edges = [edge for edge in bm.edges if not edge.link_faces]
        stats['loose_edges'] = len(loose_edges)
        if loose_edges:
            bmesh.ops.delete(bm, geom=loose_edges, context='EDGES')
        loose_verts = [vertex for vertex in bm.verts if not vertex.link_edges]
        if loose_verts:
            bmesh.ops.delete(bm, geom=loose_verts, context='VERTS')

        # Only closed manifold components have a meaningful outside direction.
        bm.normal_update()
        remaining = set(bm.faces)
        while remaining:
            seed = remaining.pop()
            component, pending = [seed], [seed]
            while pending:
                face = pending.pop()
                for edge in face.edges:
                    for neighbor in edge.link_faces:
                        if neighbor in remaining:
                            remaining.remove(neighbor)
                            pending.append(neighbor)
                            component.append(neighbor)
            if all(edge.is_manifold for face in component for edge in face.edges):
                normals = [(face, face.normal.copy()) for face in component]
                bmesh.ops.recalc_face_normals(bm, faces=component)
                bm.normal_update()
                stats['normals'] += sum(face.normal.dot(normal) < 0.0 for face, normal in normals)
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()
    stats['vertices'] = before_vertices - len(mesh.vertices)
    used = {face.material_index for face in mesh.polygons}
    # Removing in descending order lets Blender remap face indices correctly.
    for index in reversed(range(len(mesh.materials))):
        if index not in used:
            mesh.materials.pop(index=index)
            stats['material_slots'] += 1
    return stats


class FISHHWB_OT_clean_selected_mesh(bpy.types.Operator):
    bl_idname = "fishhwb.clean_selected_mesh"
    bl_label = "Clean Selected Mesh"
    bl_description = "Clean the active static mesh on a new copy; preserve the original"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT' and context.active_object is not None
                and context.active_object.type == 'MESH'
                and context.active_object.select_get())

    def execute(self, context):
        source = context.active_object
        reason = _cleanup_unsupported(source)
        if reason:
            _action_report(self, context, reason, unsupported=1)
            return {'CANCELLED'}
        selection = list(context.selected_objects)
        copy = None
        try:
            copy = _copy_mesh_object(source, context, "_Clean")
            stats = _clean_mesh(copy.data)
            _select_only(context, copy)
            changed = any(stats.values())
            detail = (f"{copy.name}: Vertices removed: {stats['vertices']:,} "
                      f"(exact duplicates merged: {stats['duplicates']:,}); "
                      f"Loose edges removed: {stats['loose_edges']:,}; "
                      f"Zero-area faces removed: {stats['zero_faces']:,}; "
                      f"Unused material slots removed: {stats['material_slots']:,}; "
                      f"Faces reoriented: {stats['normals']:,}. Original object preserved.")
            _action_report(self, context, detail, changed=int(changed), unchanged=int(not changed))
            return {'FINISHED'}
        except Exception as exc:
            if copy is not None:
                mesh = copy.data
                bpy.data.objects.remove(copy, do_unlink=True)
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            for item in context.selected_objects:
                item.select_set(False)
            for item in selection:
                item.select_set(True)
            context.view_layer.objects.active = source
            _action_report(self, context, "Mesh cleanup failed: " + str(exc), failed=1)
            return {'CANCELLED'}


def _select_only(context, obj):
    for item in context.selected_objects:
        item.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


class FISHHWB_OT_one_click_remesh(bpy.types.Operator):
    bl_idname = "fishhwb.one_click_remesh"
    bl_label = "One-Click Remesh"
    bl_description = "Create a safe remeshed copy using an automatic voxel size"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        source = context.active_object
        if source.data.shape_keys or source.vertex_groups or any(m.type == 'ARMATURE' for m in source.modifiers):
            _action_report(self, context, "One-Click Remesh supports static meshes without rigs or shape keys.", unsupported=1)
            return {'CANCELLED'}

        copy = None
        original_selection = list(context.selected_objects)
        original_active = source

        try:
            copy = _copy_mesh_object(source, context, "_Remesh")
            before = triangle_count(copy.data)
            if before < 1:
                raise ValueError("The selected mesh has no triangles")

            max_dimension = max(abs(v) for v in copy.dimensions)
            if max_dimension <= 0:
                raise ValueError("The selected mesh has no usable size")

            modifier = copy.modifiers.new("One Click Remesh", 'REMESH')
            try:
                modifier.mode = 'VOXEL'
            except (TypeError, ValueError):
                modifier.mode = 'SMOOTH'

            if hasattr(modifier, "voxel_size"):
                modifier.voxel_size = max(max_dimension / 96.0, 0.0001)
            if hasattr(modifier, "octree_depth"):
                modifier.octree_depth = 6
            if hasattr(modifier, "use_smooth_shade"):
                modifier.use_smooth_shade = True

            depsgraph = context.evaluated_depsgraph_get()
            context.view_layer.update()
            evaluated = copy.evaluated_get(depsgraph)
            result = bpy.data.meshes.new_from_object(
                evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)

            after = triangle_count(result)
            if after < 1:
                bpy.data.meshes.remove(result)
                raise ValueError("Remesh produced no triangles")

            old_mesh = copy.data
            copy.modifiers.clear()
            copy.data = result
            if old_mesh.users == 0:
                bpy.data.meshes.remove(old_mesh)

            _select_only(context, copy)
            _action_report(self, context, f"Remeshed copy created: {before:,} -> {after:,} triangles. Original object preserved.", changed=1)
            return {'FINISHED'}
        except Exception as exc:
            if copy is not None:
                mesh = copy.data
                bpy.data.objects.remove(copy, do_unlink=True)
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            for item in context.selected_objects:
                item.select_set(False)
            for item in original_selection:
                if item and item.name in bpy.data.objects:
                    item.select_set(True)
            context.view_layer.objects.active = original_active
            _action_report(self, context, "Remesh failed: " + str(exc), failed=1)
            return {'CANCELLED'}


class FISHHWB_OT_merge_vertices(bpy.types.Operator):
    bl_idname = "fishhwb.merge_vertices"
    bl_label = "Merge Duplicate Vertices"
    bl_description = "Create a copy and merge nearby duplicate vertices using the Merge Distance"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        source = context.active_object
        if source.data.shape_keys:
            _action_report(self, context, "Shape keys depend on the original topology.", unsupported=1)
            return {'CANCELLED'}

        copy = None
        original_selection = list(context.selected_objects)
        try:
            copy = _copy_mesh_object(source, context, "_Merged")
            before = len(copy.data.vertices)
            bm = bmesh.new()
            try:
                bm.from_mesh(copy.data)
                bmesh.ops.remove_doubles(
                    bm,
                    verts=list(bm.verts),
                    dist=max(context.scene.fishhwb_merge_distance, 0.0))
                bm.to_mesh(copy.data)
            finally:
                bm.free()

            copy.data.update()
            after = len(copy.data.vertices)
            _select_only(context, copy)
            _action_report(self, context, f"Merged {before - after:,} vertices on {copy.name}. Original object preserved.", changed=int(before != after), unchanged=int(before == after))
            return {'FINISHED'}
        except Exception as exc:
            if copy is not None:
                mesh = copy.data
                bpy.data.objects.remove(copy, do_unlink=True)
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            for item in context.selected_objects:
                item.select_set(False)
            for item in original_selection:
                item.select_set(True)
            context.view_layer.objects.active = source
            _action_report(self, context, "Vertex merge failed: " + str(exc), failed=1)
            return {'CANCELLED'}



class FISHHWB_OT_clean_selected_meshes(bpy.types.Operator):
    bl_idname = "fishhwb.clean_selected_meshes"
    bl_label = "Clean Selected Meshes"
    bl_description = "Clean all selected supported static meshes on new copies"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        sources = [obj for obj in context.selected_objects if obj.type == 'MESH']
        original_active = context.view_layer.objects.active
        original_selection = list(context.selected_objects)
        created = []
        changed = unchanged = skipped = unsupported = failed = 0

        for source in sources:
            reason = _cleanup_unsupported(source)
            if reason:
                unsupported += 1
                continue

            copy = None
            try:
                copy = _copy_mesh_object(source, context, "_Clean")
                stats = _clean_mesh(copy.data)
                created.append(copy)
                if any(stats.values()):
                    changed += 1
                else:
                    unchanged += 1
            except Exception:
                failed += 1
                if copy is not None and copy.name in bpy.data.objects:
                    mesh = copy.data
                    bpy.data.objects.remove(copy, do_unlink=True)
                    if mesh and mesh.users == 0:
                        bpy.data.meshes.remove(mesh)

        for obj in context.selected_objects:
            obj.select_set(False)

        if created:
            for obj in created:
                obj.select_set(True)
            context.view_layer.objects.active = created[0]
        else:
            for obj in original_selection:
                if obj and obj.name in bpy.data.objects:
                    obj.select_set(True)
            context.view_layer.objects.active = original_active

        detail = f"Processed {len(sources)} selected meshes. {len(created)} cleaned copies created; originals preserved."
        _action_report(self, context, detail, changed=changed, unchanged=unchanged,
                       skipped=skipped, unsupported=unsupported, failed=failed)
        return {'FINISHED'} if created else {'CANCELLED'}


class FISHHWB_OT_create_lods_selected(bpy.types.Operator):
    bl_idname = "fishhwb.create_lods_selected"
    bl_label = "Create LODs for Selection"
    bl_description = "Create LOD0, LOD1 and LOD2 copies for every supported selected static mesh"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and any(obj.type == 'MESH' for obj in context.selected_objects)

    def execute(self, context):
        sources = [obj for obj in context.selected_objects if obj.type == 'MESH']
        original_active = context.view_layer.objects.active
        outputs = []
        changed = unsupported = failed = 0

        for source in sources:
            if source.data.shape_keys or source.vertex_groups or any(m.type == 'ARMATURE' for m in source.modifiers):
                unsupported += 1
                continue
            if source.modifiers and not context.scene.fishhwb_apply_modifiers:
                unsupported += 1
                continue

            _select_only(context, source)
            try:
                result = bpy.ops.fishhwb.create_lods()
                if 'FINISHED' in result:
                    changed += 1
                    if context.active_object:
                        outputs.append(context.active_object)
                else:
                    failed += 1
            except Exception:
                failed += 1

        for obj in context.selected_objects:
            obj.select_set(False)
        if outputs:
            for obj in outputs:
                obj.select_set(True)
            context.view_layer.objects.active = outputs[0]
        elif original_active and original_active.name in bpy.data.objects:
            original_active.select_set(True)
            context.view_layer.objects.active = original_active

        detail = f"Created LOD sets for {changed} of {len(sources)} selected meshes. Originals preserved."
        _action_report(self, context, detail, changed=changed, unsupported=unsupported, failed=failed)
        return {'FINISHED'} if changed else {'CANCELLED'}


class FISHHWB_OT_create_game_ready_copy(bpy.types.Operator):
    bl_idname = "fishhwb.create_game_ready_copy"
    bl_label = "Create Game-Ready Copy"
    bl_description = "Create a cleaned static copy with optional modifiers and applied rotation/scale"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'OBJECT' and context.active_object is not None
                and context.active_object.type == 'MESH'
                and context.active_object.select_get())

    def execute(self, context):
        source = context.active_object
        reason = _game_ready_unsupported(source, context.scene.fishhwb_apply_modifiers)
        if reason:
            _action_report(self, context, reason, unsupported=1)
            return {'CANCELLED'}

        original_selection = list(context.selected_objects)
        original_active = source
        copy = None
        try:
            before = triangle_count(source.data)
            modifier_count = len(source.modifiers)
            copy = _copy_mesh_object(source, context, "_GameReady")

            if copy.modifiers:
                depsgraph = context.evaluated_depsgraph_get()
                context.view_layer.update()
                evaluated = copy.evaluated_get(depsgraph)
                result = bpy.data.meshes.new_from_object(
                    evaluated, preserve_all_data_layers=True, depsgraph=depsgraph)
                if result is None:
                    raise RuntimeError("Blender could not evaluate the mesh modifiers")
                old_mesh = copy.data
                copy.modifiers.clear()
                copy.data = result
                if old_mesh.users == 0:
                    bpy.data.meshes.remove(old_mesh)

            _select_only(context, copy)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
            stats = _clean_mesh(copy.data)
            copy.data.name = copy.name
            after = triangle_count(copy.data)

            detail = (
                f"{copy.name}: {before:,} -> {after:,} triangles; "
                f"{modifier_count} modifiers applied; "
                f"{stats['duplicates']:,} exact duplicate vertices merged; "
                f"{stats['loose_edges']:,} loose edges removed; "
                f"{stats['zero_faces']:,} zero-area faces removed; "
                f"{stats['material_slots']:,} unused material slots removed; "
                "rotation and scale applied. Original object preserved."
            )
            _action_report(self, context, detail, changed=1)
            return {'FINISHED'}
        except Exception as exc:
            if copy is not None and copy.name in bpy.data.objects:
                mesh = copy.data
                bpy.data.objects.remove(copy, do_unlink=True)
                if mesh and mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
            for item in context.selected_objects:
                item.select_set(False)
            for item in original_selection:
                if item and item.name in bpy.data.objects:
                    item.select_set(True)
            context.view_layer.objects.active = original_active
            _action_report(self, context, "Game-ready copy failed: " + str(exc), failed=1)
            return {'CANCELLED'}


class FISHHWB_OT_show_heavy_meshes(bpy.types.Operator):
    bl_idname = "fishhwb.show_heavy_meshes"
    bl_label = "Show Heavy Meshes"
    bl_description = "Select mesh objects whose source triangle count exceeds the chosen threshold"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        threshold = max(1, context.scene.fishhwb_heavy_triangles)
        candidates = [obj for obj in context.scene.objects if obj.type == 'MESH' and obj.data]
        heavy = [(triangle_count(obj.data), obj) for obj in candidates if triangle_count(obj.data) >= threshold]
        heavy.sort(key=lambda item: item[0], reverse=True)

        for obj in context.selected_objects:
            obj.select_set(False)
        for _, obj in heavy:
            obj.select_set(True)
        if heavy:
            context.view_layer.objects.active = heavy[0][1]

        top = ", ".join(f"{obj.name}: {count:,}" for count, obj in heavy[:5])
        detail = f"Found {len(heavy)} meshes at or above {threshold:,} triangles."
        if top:
            detail += " Largest: " + top
        _action_report(self, context, detail, unchanged=len(heavy), skipped=max(0, len(candidates) - len(heavy)))
        return {'FINISHED'}

class FISHHWB_PT_tri_limit(bpy.types.Panel):
    bl_label = "Optimize Your Project"
    bl_idname = "FISHHWB_PT_tri_limit"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'FISHHWB'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        brand = layout.box()
        if _brand_preview and "logo" in _brand_preview:
            brand.template_icon(icon_value=_brand_preview["logo"].icon_id, scale=3)
        brand.label(text=tr(context, 'title'), icon='TOOL_SETTINGS')
        brand.label(text=tr(context, 'subtitle'))
        brand.label(text="v0.7.4 • Blender")
        brand.prop(context.scene, 'fishhwb_language', text=tr(context, 'language'))

        obj = context.active_object
        selected_meshes = [item for item in context.selected_objects if item.type == 'MESH']
        selected = layout.box()
        selected.label(text=tr(context, 'selection'), icon='MESH_DATA')
        if obj and obj.type == 'MESH':
            selected.label(text=obj.name)
            stats = selected.row(align=True)
            stats.label(text=f"Triangles: {triangle_count(obj.data):,}")
            stats.label(text=f"Vertices: {len(obj.data.vertices):,}")
            if len(selected_meshes) > 1:
                selected.label(text=f"{len(selected_meshes)} mesh objects selected")
        else:
            selected.label(text=tr(context, 'select_mesh'), icon='INFO')

        quick = layout.box()
        quick.label(text=tr(context, 'quick'), icon='MODIFIER')
        quick.label(text=tr(context, 'quick_desc'))
        quick.separator()

        clean = quick.row()
        clean.scale_y = 1.35
        clean.operator('fishhwb.clean_selected_mesh', text=tr(context, 'clean_one'), icon='BRUSH_DATA')

        batch_clean = quick.row()
        batch_clean.scale_y = 1.45
        batch_clean.operator('fishhwb.clean_selected_meshes', text=tr(context, 'clean_many'), icon='MODIFIER')

        game_ready = quick.row()
        game_ready.scale_y = 1.45
        game_ready.operator('fishhwb.create_game_ready_copy', text=tr(context, 'game_ready'), icon='OUTLINER_OB_MESH')
        quick.prop(context.scene, 'fishhwb_apply_modifiers', text=tr(context, 'apply_modifiers'))

        quick.separator()
        remesh = quick.row()
        remesh.scale_y = 1.35
        remesh.operator('fishhwb.one_click_remesh', text=tr(context, 'remesh'), icon='MOD_REMESH')

        quick.separator()
        quick.prop(context.scene, 'fishhwb_merge_distance', text=tr(context, 'merge_distance'))
        merge = quick.row()
        merge.scale_y = 1.35
        merge.operator('fishhwb.merge_vertices', text=tr(context, 'merge'), icon='AUTOMERGE_ON')

        batch = layout.box()
        batch.label(text=tr(context, 'batch'), icon='MODIFIER')
        batch.label(text=tr(context, 'batch_desc'))

        lod_row = batch.row()
        lod_row.scale_y = 1.35
        lod_row.operator('fishhwb.create_lods_selected', text=tr(context, 'batch_lods'), icon='MOD_DECIM')

        batch.prop(context.scene, 'fishhwb_heavy_triangles', text=tr(context, 'heavy_limit'))
        heavy = batch.row()
        heavy.scale_y = 1.25
        heavy.operator('fishhwb.show_heavy_meshes', text=tr(context, 'heavy'), icon='MESH_DATA')

        tools = layout.box()
        tools.label(text=tr(context, 'more_tools'), icon='PREFERENCES')
        tools.prop(context.scene, 'fishhwb_show_advanced', text=tr(context, 'advanced_toggle'), toggle=True)

        if context.scene.fishhwb_show_advanced:
            advanced = tools.column(align=False)
            advanced.separator()
            advanced.label(text=tr(context, 'tri_reduce'), icon='MOD_DECIM')
            advanced.prop(context.scene, 'fishhwb_tri_limit', text=tr(context, 'triangle_limit'))
            advanced.prop(context.scene, 'fishhwb_apply_modifiers', text=tr(context, 'apply_modifiers'))
            row = advanced.row()
            row.scale_y = 1.2
            row.operator('fishhwb.tri_limit', text=tr(context, 'reduced_copy'), icon='MOD_DECIM')

            advanced.separator()
            advanced.label(text=tr(context, 'join_atlas'), icon='AUTOMERGE_ON')
            advanced.prop(context.scene, 'fishhwb_make_atlas', text=tr(context, 'make_atlas'))
            if context.scene.fishhwb_make_atlas:
                advanced.prop(context.scene, 'fishhwb_atlas_size', text=tr(context, 'atlas_size'))
                advanced.prop(context.scene, 'fishhwb_atlas_padding', text=tr(context, 'padding'))
            row = advanced.row()
            row.scale_y = 1.2
            row.operator('fishhwb.join_merge', text=tr(context, 'join'), icon='AUTOMERGE_ON')

            advanced.separator()
            advanced.label(text=tr(context, 'static_lods'), icon='MOD_DECIM')
            row = advanced.row()
            row.scale_y = 1.2
            row.operator('fishhwb.create_lods', text=tr(context, 'create_lods'), icon='MOD_DECIM')

        if context.scene.fishhwb_last_result:
            result = layout.box()
            result.label(text=tr(context, 'last_result'), icon='INFO')
            import textwrap
            width = max(24, int(context.region.width / (7 * context.preferences.system.ui_scale)))
            for line in context.scene.fishhwb_last_result.splitlines():
                for wrapped in textwrap.wrap(line, width=width):
                    result.label(text=wrapped)

        support = layout.box()
        support.label(text=tr(context, 'free'), icon='HEART')
        support.label(text=tr(context, 'free_1'))
        support.separator()
        support.label(text=tr(context, 'free_2'))
        support.label(text=tr(context, 'free_3'))

        donate = support.row()
        donate.scale_y = 1.35
        donate.operator("wm.url_open", text=tr(context, 'support'), icon='URL').url = "https://www.patreon.com/cw/DedZed"

        links = layout.row(align=True)
        links.operator("wm.url_open", text="GitHub", icon='URL').url = "https://github.com/dedzedofficial/Optimize-Your-Project"
        links.operator("wm.url_open", text="Website", icon='URL').url = "https://fishhwb.github.io/"

classes = (FISHHWB_OT_clean_selected_mesh, FISHHWB_OT_clean_selected_meshes, FISHHWB_OT_tri_limit,
           FISHHWB_OT_join_merge, FISHHWB_OT_one_click_remesh, FISHHWB_OT_merge_vertices,
           FISHHWB_OT_create_lods, FISHHWB_OT_create_lods_selected, FISHHWB_OT_create_game_ready_copy,
           FISHHWB_OT_show_heavy_meshes, FISHHWB_PT_tri_limit)


def register():
    global _brand_preview
    _brand_preview = bpy.utils.previews.new()
    _brand_preview.load("logo", str(Path(__file__).with_name("optimize-your-project-logo.png")), 'IMAGE')
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.fishhwb_last_result = StringProperty(options={'SKIP_SAVE'})
    bpy.types.Scene.fishhwb_language = EnumProperty(
        name="Language", items=LANGUAGE_ITEMS, default='EN',
        description="Interface language for Optimize Your Project")
    bpy.types.Scene.fishhwb_heavy_triangles = IntProperty(
        name="Heavy Triangle Limit", default=100000, min=1,
        description="Triangle count used by Show Heavy Meshes")
    bpy.types.Scene.fishhwb_tri_limit = IntProperty(name="Triangle Limit", default=1000, min=1)
    bpy.types.Scene.fishhwb_apply_modifiers = BoolProperty(name="Apply Existing Modifiers", default=True,
        description="Include existing modifiers in the new copy before decimation")
    bpy.types.Scene.fishhwb_make_atlas = BoolProperty(
        name="Merge Base Color Textures + UVs", default=False,
        description="Pack supported image textures into one atlas and remap UVs on the joined copy")
    bpy.types.Scene.fishhwb_atlas_size = IntProperty(
        name="Atlas Size", default=1024, min=256, max=4096)
    bpy.types.Scene.fishhwb_atlas_padding = IntProperty(
        name="Padding (Pixels)", default=4, min=0, max=32)
    bpy.types.Scene.fishhwb_merge_distance = FloatProperty(
        name="Merge Distance", default=0.0001, min=0.0, precision=5, subtype='DISTANCE',
        description="World-space proximity used to merge vertices after joining")
    bpy.types.Scene.fishhwb_show_advanced = BoolProperty(
        name="Show Advanced Mesh Tools", default=False,
        description="Reveal the optional triangle reduction, joining, atlas and LOD tools")


def unregister():
    global _brand_preview
    if _brand_preview is not None:
        bpy.utils.previews.remove(_brand_preview)
        _brand_preview = None
    del bpy.types.Scene.fishhwb_last_result
    del bpy.types.Scene.fishhwb_language
    del bpy.types.Scene.fishhwb_heavy_triangles
    del bpy.types.Scene.fishhwb_tri_limit
    del bpy.types.Scene.fishhwb_apply_modifiers
    del bpy.types.Scene.fishhwb_merge_distance
    del bpy.types.Scene.fishhwb_make_atlas
    del bpy.types.Scene.fishhwb_atlas_size
    del bpy.types.Scene.fishhwb_atlas_padding
    del bpy.types.Scene.fishhwb_show_advanced
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    register()
