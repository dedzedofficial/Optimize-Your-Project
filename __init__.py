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
    primary.label(text=_addon.tr(context, "primary_actions"), icon="TOOL_SETTINGS")

    remesh = primary.box()
    remesh.prop(context.scene, "fishhwb_triangle_target", text=_addon.tr(context, "triangle_target"), slider=True)
    row = remesh.row()
    row.scale_y = 1.5
    row.operator("fishhwb.one_click_remesh", text=_addon.tr(context, "remesh_action"), icon="MOD_REMESH")

    lod = primary.box()
    lod.prop(context.scene, "fishhwb_apply_modifiers", text=_addon.tr(context, "apply_modifiers"))
    lod.prop(context.scene, "fishhwb_create_collision_proxy", text=_addon.tr(context, "collision_proxy"))
    row = lod.row()
    row.scale_y = 1.5
    row.operator(
        "fishhwb.create_lods_selected" if len(selected_meshes) > 1 else "fishhwb.create_lods",
        text=_addon.tr(context, "lod_action"), icon="MOD_DECIM",
    )

    row = primary.row()
    row.scale_y = 1.45
    row.operator("fishhwb.clean_mesh", text=_addon.tr(context, "clean_mesh"), icon="BRUSH_DATA")

    row = primary.row()
    row.scale_y = 1.35
    row.operator("fishhwb.generate_lightmap_uv", text=_addon.tr(context, "lightmap_uv"), icon="UV")

    row = primary.row()
    row.scale_y = 1.35
    row.operator("fishhwb.link_identical_mesh_data", text=_addon.tr(context, "link_mesh_data"), icon="LINKED")

    row = primary.row()
    row.scale_y = 1.35
    row.operator("fishhwb.strip_collider_render_data", text=_addon.tr(context, "strip_collider"), icon="TRASH")

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
    # Patch Remesh before Blender registers the operator class so validation is part of the registered operator.
    _v08.install_remesh_guard(_addon)
    _addon.register()
    try:
        _tools42.register()
        _v08.register(_addon)
    except Exception:
        try:
            _v08.unregister()
            _tools42.unregister()
        finally:
            _addon.unregister()
        raise


def unregister():
    _v08.unregister()
    _tools42.unregister()
    _addon.unregister()
