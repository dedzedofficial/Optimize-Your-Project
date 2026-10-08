# SPDX-License-Identifier: GPL-3.0-or-later
"""Blender 4.2+ extension entry point for Optimize Your Project."""

import textwrap
import bpy

from .Blender import vr_optimizer_blender as _addon
from .Blender.vr_optimizer_blender import tools_42 as _tools42
from .Blender.vr_optimizer_blender import v08_tools as _v08

bl_info = dict(_addon.bl_info)
bl_info.update({
    "version": (0, 8, 0),
    "blender": (4, 2, 0),
    "description": "One-click Remesh, LOD, Clean Mesh, lightmap and static-mesh optimization tools",
})
_addon.bl_info.update(bl_info)

# Keep Blender language parity with Unity: 14 manually selectable languages.
_addon.LANGUAGE_ITEMS = (
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
_set_translation('subtitle', {code: 'Blender v0.8.0' for code, _, _ in _addon.LANGUAGE_ITEMS})
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
_set_translation('last_result', {
    'EN': 'LAST RESULT', 'JA': '最後の結果', 'ZH': '上次结果', 'ZT': '上次結果', 'KO': '마지막 결과',
    'ES': 'ÚLTIMO RESULTADO', 'FR': 'DERNIER RÉSULTAT', 'DE': 'LETZTES ERGEBNIS', 'PT': 'ÚLTIMO RESULTADO',
    'RU': 'ПОСЛЕДНИЙ РЕЗУЛЬТАТ', 'IT': 'ULTIMO RISULTATO', 'NL': 'LAATSTE RESULTAAT', 'PL': 'OSTATNI WYNIK', 'TR': 'SON SONUÇ',
})


def _wrapped(layout, text, context, icon=None):
    width = max(28, int(context.region.width / (7 * max(context.preferences.system.ui_scale, 0.5))))
    lines = textwrap.wrap(text, width=width) or [text]
    for index, line in enumerate(lines):
        if icon and index == 0:
            layout.label(text=line, icon=icon)
        else:
            layout.label(text=line)


def _draw_core_080(self, context):
    layout = self.layout
    layout.use_property_split = False
    layout.use_property_decorate = False

    brand = layout.box()
    if _addon._brand_preview and "logo" in _addon._brand_preview:
        brand.template_icon(icon_value=_addon._brand_preview["logo"].icon_id, scale=2.2)
    brand.label(text=_addon.tr(context, "title"))
    brand.label(text=_addon.tr(context, "subtitle"))
    brand.prop(context.scene, "fishhwb_language", text=_addon.tr(context, "language"))

    obj = context.active_object
    selected_meshes = [item for item in context.selected_objects if item.type == "MESH"]

    selected = layout.box()
    selected.label(text=_addon.tr(context, "selection"), icon="MESH_DATA")
    if obj and obj.type == "MESH":
        selected.label(text=obj.name)
        stats = selected.row(align=True)
        stats.label(text=f"Triangles: {_addon.triangle_count(obj.data):,}")
        stats.label(text=f"Vertices: {len(obj.data.vertices):,}")
        selected.prop(obj, "fishhwb_protect_detail", text=_addon.tr(context, "protect_detail"))
        if obj.get("fishhwb_remesh_history") or obj.get("fishhwb_lod_history"):
            selected.operator("fishhwb.reset_optimization_history", text=_addon.tr(context, "reset_history"), icon="FILE_REFRESH")
        if len(selected_meshes) > 1:
            selected.label(text=f"{len(selected_meshes)} mesh objects selected")
    else:
        _wrapped(selected, _addon.tr(context, "select_mesh"), context, "INFO")

    primary = layout.box()
    primary.label(text="PRIMARY ACTIONS", icon="TOOL_SETTINGS")

    remesh = primary.box()
    remesh.prop(context.scene, "fishhwb_triangle_target", text=_addon.tr(context, "triangle_target"), slider=True)
    row = remesh.row()
    row.scale_y = 1.5
    row.operator("fishhwb.one_click_remesh", text="REMESH TO TRIANGLE TARGET", icon="MOD_REMESH")

    lod = primary.box()
    lod.prop(context.scene, "fishhwb_apply_modifiers", text=_addon.tr(context, "apply_modifiers"))
    lod.prop(context.scene, "fishhwb_create_collision_proxy", text=_addon.tr(context, "collision_proxy"))
    row = lod.row()
    row.scale_y = 1.5
    row.operator(
        "fishhwb.create_lods_selected" if len(selected_meshes) > 1 else "fishhwb.create_lods",
        text="CREATE LOD0 / LOD1 / LOD2", icon="MOD_DECIM",
    )

    row = primary.row()
    row.scale_y = 1.45
    row.operator("fishhwb.clean_mesh", text="CLEAN MESH", icon="BRUSH_DATA")

    row = primary.row()
    row.scale_y = 1.35
    row.operator("fishhwb.generate_lightmap_uv", text="GENERATE LIGHTMAP UV", icon="UV")

    row = primary.row()
    row.scale_y = 1.35
    row.operator("fishhwb.link_identical_mesh_data", text="LINK IDENTICAL MESH DATA", icon="LINKED")

    row = primary.row()
    row.scale_y = 1.35
    row.operator("fishhwb.strip_collider_render_data", text="STRIP COLLIDER RENDER DATA", icon="TRASH")

    if context.scene.fishhwb_last_result:
        result = layout.box()
        result.label(text=_addon.tr(context, "last_result"), icon="INFO")
        for line in context.scene.fishhwb_last_result.splitlines():
            _wrapped(result, line, context)


_addon.FISHHWB_PT_optimizer.draw = _draw_core_080
_tools42.classes = tuple(cls for cls in _tools42.classes if cls is not _tools42.FISHHWB_PT_optimizer_42)


def register():
    if bpy.app.version < (4, 2, 0):
        raise RuntimeError("Optimize Your Project for Blender requires Blender 4.2 or newer.")
    _addon.register()
    try:
        _tools42.register()
        _v08.register(_addon)
    except Exception:
        try:
            _tools42.unregister()
        finally:
            _addon.unregister()
        raise


def unregister():
    _v08.unregister()
    _tools42.unregister()
    _addon.unregister()
