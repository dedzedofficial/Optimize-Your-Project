# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender 4.2+ extension entry point for Optimize Your Project."""

import textwrap
import bpy

from .Blender import vr_optimizer_blender as _addon
from .Blender.vr_optimizer_blender import tools_42 as _tools42
from .Blender.vr_optimizer_blender import v08_tools as _v08
from .Blender.vr_optimizer_blender import v088_tools as _v088
from .Blender.vr_optimizer_blender import smart_remesh as _smart

bl_info = dict(_addon.bl_info)
bl_info.update({
    "version": (8, 8, 3),
    "blender": (4, 2, 0),
    "description": "One-click Remesh, LOD, Clean Mesh, lightmap and static-mesh optimization tools",
})
_addon.bl_info.update(bl_info)

# Unity and Blender both expose Auto plus the same 14 actual languages.
_addon.LANGUAGE_ITEMS = (
    ('AUTO', 'Auto', 'Follow Blender interface language'),
    ('EN', 'English', 'English'),
    ('JA', '日本語', 'Japanese'),
    ('ZH', '简体中文', 'Chinese (Simplified)'),
    ('ZT', '繁體中文', 'Chinese (Traditional)'),
    ('KO', '한국어', 'Korean'),
    ('ES', 'Español', 'Spanish'),
    ('FR', 'Français', 'French'),
    ('DE', 'Deutsch', 'German'),
    ('PT', 'Português', 'Portuguese'),
    ('RU', 'Русский', 'Russian'),
    ('IT', 'Italiano', 'Italian'),
    ('NL', 'Nederlands', 'Dutch'),
    ('PL', 'Polski', 'Polish'),
    ('TR', 'Türkçe', 'Turkish'),
)


def _set_translation(key, values):
    table = _addon._TRANSLATIONS.setdefault(key, {})
    table.update(values)


_set_translation('language', {
    'EN': 'Language', 'JA': '言語', 'ZH': '语言', 'ZT': '語言', 'KO': '언어',
    'ES': 'Idioma', 'FR': 'Langue', 'DE': 'Sprache', 'PT': 'Idioma', 'RU': 'Язык',
    'IT': 'Lingua', 'NL': 'Taal', 'PL': 'Język', 'TR': 'Dil',
})
_set_translation('title', {
    'EN': 'OPTIMIZE YOUR PROJECT', 'JA': 'プロジェクトを最適化', 'ZH': '优化你的项目', 'ZT': '最佳化你的專案',
    'KO': '프로젝트 최적화', 'ES': 'OPTIMIZA TU PROYECTO', 'FR': 'OPTIMISEZ VOTRE PROJET',
    'DE': 'PROJEKT OPTIMIEREN', 'PT': 'OTIMIZE SEU PROJETO', 'RU': 'ОПТИМИЗИРОВАТЬ ПРОЕКТ',
    'IT': 'OTTIMIZZA IL PROGETTO', 'NL': 'OPTIMALISEER JE PROJECT', 'PL': 'OPTYMALIZUJ PROJEKT',
    'TR': 'PROJENİ OPTİMİZE ET',
})
_set_translation('subtitle', {code: 'Blender v8.8.3' for code, _, _ in _addon.LANGUAGE_ITEMS if code != 'AUTO'})
_set_translation('smart_optimize', {
    'EN': 'SMART OPTIMIZE (PREVIEW)', 'JA': 'スマート最適化 (プレビュー)',
    'ZH': '智能优化 (预览)', 'ZT': '智慧最佳化 (預覽)', 'KO': '스마트 최적화 (미리보기)',
    'ES': 'OPTIMIZACIÓN INTELIGENTE', 'FR': 'OPTIMISATION INTELLIGENTE',
    'DE': 'SMART OPTIMIEREN', 'PT': 'OTIMIZAÇÃO INTELIGENTE',
    'RU': 'УМНАЯ ОПТИМИЗАЦИЯ', 'IT': 'OTTIMIZZAZIONE SMART',
    'NL': 'SLIM OPTIMALISEREN', 'PL': 'INTELIGENTNA OPTYMALIZACJA',
    'TR': 'AKILLI OPTİMİZASYON',
})
_set_translation('selection', {
    'EN': 'CURRENT SELECTION', 'JA': '現在の選択', 'ZH': '当前选择', 'ZT': '目前選取', 'KO': '현재 선택',
    'ES': 'SELECCIÓN ACTUAL', 'FR': 'SÉLECTION ACTUELLE', 'DE': 'AKTUELLE AUSWAHL', 'PT': 'SELEÇÃO ATUAL',
    'RU': 'ТЕКУЩИЙ ВЫБОР', 'IT': 'SELEZIONE CORRENTE', 'NL': 'HUIDIGE SELECTIE', 'PL': 'BIEŻĄCY WYBÓR', 'TR': 'GEÇERLİ SEÇİM',
})
_set_translation('protect_detail', {
    'EN': 'Protect detail', 'JA': 'ディテールを保護', 'ZH': '保护细节', 'ZT': '保護細節', 'KO': '디테일 보호',
    'ES': 'Proteger detalle', 'FR': 'Protéger les détails', 'DE': 'Details schützen', 'PT': 'Proteger detalhes',
    'RU': 'Защитить детали', 'IT': 'Proteggi dettagli', 'NL': 'Details beschermen', 'PL': 'Chroń szczegóły', 'TR': 'Detayı koru',
})
_set_translation('reset_history', {
    'EN': 'Reset history', 'JA': '履歴をリセット', 'ZH': '重置历史', 'ZT': '重設歷史', 'KO': '기록 초기화',
    'ES': 'Restablecer historial', 'FR': 'Réinitialiser l’historique', 'DE': 'Verlauf zurücksetzen', 'PT': 'Redefinir histórico',
    'RU': 'Сбросить историю', 'IT': 'Reimposta cronologia', 'NL': 'Geschiedenis resetten', 'PL': 'Resetuj historię', 'TR': 'Geçmişi sıfırla',
})
_set_translation('triangle_target', {
    'EN': 'Triangle target', 'JA': '三角形の上限', 'ZH': '三角面目标', 'ZT': '三角形目標', 'KO': '삼각형 목표',
    'ES': 'Objetivo de triángulos', 'FR': 'Cible de triangles', 'DE': 'Dreiecks-Ziel', 'PT': 'Meta de triângulos',
    'RU': 'Цель по треугольникам', 'IT': 'Obiettivo triangoli', 'NL': 'Doel driehoeken', 'PL': 'Docelowa liczba trójkątów', 'TR': 'Üçgen hedefi',
})
_set_translation('primary_actions', {
    'EN': 'PRIMARY ACTIONS', 'JA': '主要アクション', 'ZH': '主要操作', 'ZT': '主要操作', 'KO': '주요 작업',
    'ES': 'ACCIONES PRINCIPALES', 'FR': 'ACTIONS PRINCIPALES', 'DE': 'HAUPTAKTIONEN', 'PT': 'AÇÕES PRINCIPAIS',
    'RU': 'ОСНОВНЫЕ ДЕЙСТВИЯ', 'IT': 'AZIONI PRINCIPALI', 'NL': 'HOOFDACTIES', 'PL': 'GŁÓWNE DZIAŁANIA', 'TR': 'ANA İŞLEMLER',
})
_set_translation('remesh_action', {
    'EN': 'REMESH TO TRIANGLE TARGET', 'JA': '目標三角形数へリメッシュ', 'ZH': '重网格到目标三角面', 'ZT': '重新網格至目標三角形', 'KO': '목표 삼각형으로 리메시',
    'ES': 'REMALLAR AL OBJETIVO', 'FR': 'REMESH VERS LA CIBLE', 'DE': 'AUF DREIECKSZIEL REMESHEN', 'PT': 'REMESH PARA A META',
    'RU': 'РЕМЕШ ДО ЦЕЛИ', 'IT': 'REMESH AL TARGET', 'NL': 'REMESH NAAR DOEL', 'PL': 'REMESH DO CELU', 'TR': 'ÜÇGEN HEDEFİNE REMESH',
})
_set_translation('lod_action', {
    'EN': 'CREATE LOD0 / LOD1 / LOD2', 'JA': 'LOD0 / LOD1 / LOD2 を作成', 'ZH': '创建 LOD0 / LOD1 / LOD2', 'ZT': '建立 LOD0 / LOD1 / LOD2', 'KO': 'LOD0 / LOD1 / LOD2 생성',
    'ES': 'CREAR LOD0 / LOD1 / LOD2', 'FR': 'CRÉER LOD0 / LOD1 / LOD2', 'DE': 'LOD0 / LOD1 / LOD2 ERSTELLEN', 'PT': 'CRIAR LOD0 / LOD1 / LOD2',
    'RU': 'СОЗДАТЬ LOD0 / LOD1 / LOD2', 'IT': 'CREA LOD0 / LOD1 / LOD2', 'NL': 'MAAK LOD0 / LOD1 / LOD2', 'PL': 'UTWÓRZ LOD0 / LOD1 / LOD2', 'TR': 'LOD0 / LOD1 / LOD2 OLUŞTUR',
})
_set_translation('clean_mesh', {
    'EN': 'CLEAN MESH', 'JA': 'メッシュをクリーン', 'ZH': '清理网格', 'ZT': '清理網格', 'KO': '메시 정리',
    'ES': 'LIMPIAR MALLA', 'FR': 'NETTOYER LE MAILLAGE', 'DE': 'MESH BEREINIGEN', 'PT': 'LIMPAR MALHA',
    'RU': 'ОЧИСТИТЬ СЕТКУ', 'IT': 'PULISCI MESH', 'NL': 'MESH OPSCHONEN', 'PL': 'WYCZYŚĆ SIATKĘ', 'TR': 'MESH TEMİZLE',
})
_set_translation('lightmap_uv', {
    'EN': 'GENERATE LIGHTMAP UV', 'JA': 'ライトマップ UV を生成', 'ZH': '生成光照贴图 UV', 'ZT': '產生光照貼圖 UV', 'KO': '라이트맵 UV 생성',
    'ES': 'GENERAR UV DE LIGHTMAP', 'FR': 'GÉNÉRER UV LIGHTMAP', 'DE': 'LIGHTMAP-UV ERSTELLEN', 'PT': 'GERAR UV DE LIGHTMAP',
    'RU': 'СОЗДАТЬ LIGHTMAP UV', 'IT': 'GENERA UV LIGHTMAP', 'NL': 'LIGHTMAP UV GENEREREN', 'PL': 'GENERUJ UV LIGHTMAPY', 'TR': 'LIGHTMAP UV OLUŞTUR',
})
_set_translation('link_mesh_data', {
    'EN': 'LINK IDENTICAL MESH DATA', 'JA': '同一メッシュデータをリンク', 'ZH': '链接相同网格数据', 'ZT': '連結相同網格資料', 'KO': '동일 메시 데이터 연결',
    'ES': 'VINCULAR MALLAS IDÉNTICAS', 'FR': 'LIER LES MAILLAGES IDENTIQUES', 'DE': 'IDENTISCHE MESH-DATEN VERKNÜPFEN', 'PT': 'VINCULAR MALHAS IDÊNTICAS',
    'RU': 'СВЯЗАТЬ ОДИНАКОВЫЕ СЕТКИ', 'IT': 'COLLEGA MESH IDENTICHE', 'NL': 'IDENTIEKE MESH-DATA KOPPELEN', 'PL': 'POŁĄCZ IDENTYCZNE SIATKI', 'TR': 'AYNI MESH VERİSİNİ BAĞLA',
})
_set_translation('strip_collider', {
    'EN': 'STRIP COLLIDER RENDER DATA', 'JA': 'コライダー描画データを削除', 'ZH': '移除碰撞体渲染数据', 'ZT': '移除碰撞器渲染資料', 'KO': '콜라이더 렌더 데이터 제거',
    'ES': 'QUITAR DATOS DE RENDER DEL COLISOR', 'FR': 'RETIRER LE RENDU DU COLLIDER', 'DE': 'COLLIDER-RENDERDATEN ENTFERNEN', 'PT': 'REMOVER RENDER DO COLISOR',
    'RU': 'УДАЛИТЬ РЕНДЕР-ДАННЫЕ КОЛЛАЙДЕРА', 'IT': 'RIMUOVI DATI RENDER COLLIDER', 'NL': 'COLLIDER-RENDERDATA VERWIJDEREN', 'PL': 'USUŃ DANE RENDERERA KOLIDERA', 'TR': 'COLLIDER RENDER VERİSİNİ KALDIR',
})
_set_translation('last_result', {
    'EN': 'LAST RESULT', 'JA': '最後の結果', 'ZH': '上次结果', 'ZT': '上次結果', 'KO': '마지막 결과',
    'ES': 'ÚLTIMO RESULTADO', 'FR': 'DERNIER RÉSULTAT', 'DE': 'LETZTES ERGEBNIS', 'PT': 'ÚLTIMO RESULTADO',
    'RU': 'ПОСЛЕДНИЙ РЕЗУЛЬТАТ', 'IT': 'ULTIMO RISULTATO', 'NL': 'LAATSTE RESULTAAT', 'PL': 'OSTATNI WYNIK', 'TR': 'SON SONUÇ',
})

_LOCALE_MAP = {
    'ja': 'JA', 'zh_hans': 'ZH', 'zh_cn': 'ZH', 'zh_sg': 'ZH', 'zh_hant': 'ZT', 'zh_tw': 'ZT', 'zh_hk': 'ZT',
    'ko': 'KO', 'es': 'ES', 'fr': 'FR', 'de': 'DE', 'pt': 'PT', 'ru': 'RU', 'it': 'IT', 'nl': 'NL', 'pl': 'PL', 'tr': 'TR',
}


def _effective_language(context):
    selected = getattr(context.scene, 'fishhwb_language', 'EN') if context and context.scene else 'EN'
    if selected != 'AUTO':
        return selected
    locale = str(getattr(context.preferences.view, 'language', 'en_US') or 'en_US').lower()
    for prefix, code in _LOCALE_MAP.items():
        if locale.startswith(prefix):
            return code
    return 'EN'


def _tr_v080(context, key):
    values = _addon._TRANSLATIONS.get(key, {})
    lang = _effective_language(context)
    return values.get(lang, values.get('EN', key))


_addon.tr = _tr_v080


def _wrapped(layout, text, context, icon=None):
    width = max(28, int(context.region.width / (7 * max(context.preferences.system.ui_scale, 0.5))))
    lines = textwrap.wrap(text, width=width) or [text]
    for index, line in enumerate(lines):
        if icon and index == 0:
            layout.label(text=line, icon=icon)
        else:
            layout.label(text=line)


def _draw_core_080(self, context):
    """Compact public UI: selection, smart remesh, LODs and material merge."""
    layout = self.layout
    layout.use_property_split = False
    layout.use_property_decorate = False

    layout.label(text=_addon.tr(context, 'title'), icon='MOD_REMESH')
    layout.prop(context.scene, 'fishhwb_language', text=_addon.tr(context, 'language'))

    selection = layout.box()
    selection.label(text=_addon.tr(context, 'selection'), icon='MESH_DATA')
    obj = context.active_object
    meshes = [item for item in context.selected_objects if item.type == 'MESH']
    if obj and obj.type == 'MESH':
        selection.label(text=obj.name, icon='OBJECT_DATA')
        selection.label(text=f"Triangles: {_addon.triangle_count(obj.data):,}")
        selection.label(text=f"Vertices: {len(obj.data.vertices):,}")
        selection.label(text=f"Faces: {len(obj.data.polygons):,}")
        if len(meshes) > 1:
            selection.label(text=f"{len(meshes)} mesh objects selected")
        selection.prop(
            context.scene, 'fishhwb_show_mesh_inspector',
            text='Mesh Health Details',
            icon=('TRIA_DOWN' if context.scene.fishhwb_show_mesh_inspector
                  else 'TRIA_RIGHT'), emboss=False)
        if context.scene.fishhwb_show_mesh_inspector:
            from .Blender.vr_optimizer_blender import mesh_quality
            stats = mesh_quality.inspect_mesh(obj.data)
            selection.label(text=(
                f"UVs: {stats['uv_layers']}  |  "
                f"Materials: {stats['material_slots']}  |  "
                f"N-gons: {stats['ngons']}"))
            warnings = mesh_quality.summary_lines(stats)
            if warnings:
                for issue in warnings[:5]:
                    selection.label(text=issue, icon='ERROR')
            else:
                selection.label(text='No basic mesh-health warnings', icon='CHECKMARK')
            selection.label(text='Inspect shading and UV quality manually', icon='INFO')
    else:
        selection.label(text=_addon.tr(context, 'select_mesh'), icon='INFO')

    smart = layout.box()
    row = smart.row()
    row.scale_y = 1.55
    row.operator('fishhwb.smart_remesh', text='SMART REMESH', icon='MOD_REMESH')
    smart.prop(context.scene, 'fishhwb_triangle_target', text='Triangle Limit')
    smart.prop(context.scene, 'fishhwb_remesh_scope', text='Scope')
    smart.prop(
        context.scene, 'fishhwb_smart_advanced', text='Advanced Options',
        icon=('TRIA_DOWN' if context.scene.fishhwb_smart_advanced
              else 'TRIA_RIGHT'), emboss=False)
    if context.scene.fishhwb_smart_advanced:
        smart.prop(context.scene, 'fishhwb_remesh_quality',
                   text='Detail Handling')
        smart.label(text='Mark vertices with FISHHWB_Protect to keep them', icon='INFO')

    lod = layout.box()
    row = lod.row()
    row.scale_y = 1.45
    row.operator(
        'fishhwb.create_lods_selected' if len(meshes) > 1 else 'fishhwb.create_lods',
        text='CREATE LODS', icon='MOD_DECIM')
    lod.prop(
        context.scene, 'fishhwb_lod_advanced', text='LOD & Collision Options',
        icon=('TRIA_DOWN' if context.scene.fishhwb_lod_advanced
              else 'TRIA_RIGHT'), emboss=False)
    if context.scene.fishhwb_lod_advanced:
        lod.prop(context.scene, 'fishhwb_lod1_percent', text='LOD1 Detail %')
        lod.prop(context.scene, 'fishhwb_lod2_percent', text='LOD2 Detail %')
        lod.prop(context.scene, 'fishhwb_apply_modifiers',
                 text='Apply Existing Modifiers')
        lod.prop(context.scene, 'fishhwb_create_collision_proxy',
                 text='Generate Collider')
        if context.scene.fishhwb_create_collision_proxy:
            lod.prop(context.scene, 'fishhwb_collision_shape', text='Collider Type')
            lod.prop(context.scene, 'fishhwb_collision_target',
                     text='Collider Triangle Limit')

    materials = layout.box()
    row = materials.row()
    row.scale_y = 1.45
    row.operator('fishhwb.merge_textures',
                 text='MERGE MATERIALS', icon='MATERIAL')
    materials.prop(
        context.scene, 'fishhwb_material_advanced',
        text='Material Options',
        icon=('TRIA_DOWN' if context.scene.fishhwb_material_advanced
              else 'TRIA_RIGHT'), emboss=False)
    if context.scene.fishhwb_material_advanced:
        materials.prop(context.scene, 'fishhwb_atlas_size',
                       text='Texture Atlas Resolution')




_addon.FISHHWB_PT_optimizer.draw = _draw_core_080
_tools42.classes = tuple(cls for cls in _tools42.classes if cls is not _tools42.FISHHWB_PT_optimizer_42)


def register():
    if bpy.app.version < (4, 2, 0):
        raise RuntimeError("Optimize Your Project for Blender requires Blender 4.2 or newer.")
    _v08.install_remesh_guard(_addon)
    _addon.register()
    try:
        _tools42.register()
        _v08.register(_addon)
        _v088.register(_addon)
        _smart.register()
    except Exception:
        try:
            try:
                _smart.unregister()
                _v088.unregister()
            except Exception:
                pass
            _v08.unregister()
            _tools42.unregister()
        finally:
            _addon.unregister()
        raise


def unregister():
    _smart.unregister()
    _v088.unregister()
    _v08.unregister()
    _tools42.unregister()
    _addon.unregister()
