using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal enum OYPLanguage
    {
        Auto,
        English,
        Japanese,
        SimplifiedChinese,
        TraditionalChinese,
        Korean,
        Spanish,
        French,
        German,
        Portuguese,
        Russian,
        Italian
    }

    internal static class OYPLocalization
    {
        const string PreferenceKey = "FISHHWB.OptimizeYourProject.Language.v0760";
        const string LegacyPreferenceKey = "FISHHWB.VROptimizer.Language.v074";

        static readonly Dictionary<string, string> English = new Dictionary<string, string>
        {
            { "project", "PROJECT" },
            { "avatar", "CHARACTER / AVATAR" },
            { "language", "Language" },
            { "developer_optimizer", "One-click optimization for real-time projects" },
            { "project_scope", "Project asset scope" },
            { "scope_help", "Choose which Assets folder the project-wide import and cleanup actions are allowed to inspect." },
            { "scope", "Asset scope" },
            { "assets_folder", "Assets folder" },
            { "use_selection", "Use selection" },
            { "invalid_folder", "Choose an existing folder under Assets." },
            { "avatar_root", "Character / Avatar root" },
            { "avatar_help", "Select a character or avatar root in a loaded scene." },
            { "one_click", "ONE CLICK" },
            { "quick_optimize", "QUICK OPTIMIZE" },
            { "quick_help", "Pick a safe configuration, run the bundled optimizer, or use the individual tools below for exact control." },
            { "config_balanced", "Balanced" },
            { "config_mobile", "Mobile" },
            { "config_vr", "VR" },
            { "optimize_scope", "Optimize Current Scope" },
            { "optimize_character", "Optimize Character / Avatar" },
            { "individual_tools", "Individual tools" },
            { "optimize_textures", "Optimize Textures" },
            { "optimize_models", "Optimize Model Imports" },
            { "optimize_particles", "Optimize Particles" },
            { "fix_materials", "Fix Material Costs" },
            { "optimize_lighting", "Optimize Lighting" },
            { "disable_shadows", "Disable Realtime Shadows" },
            { "optimize_ui_raycasts", "Optimize UI Raycasts" },
            { "clean_missing_scripts", "Clean Missing Scripts" },
            { "advanced", "Advanced settings" },
            { "review", "REVIEW" },
            { "largest_textures", "Largest Textures" },
            { "readwrite_review", "Read/Write Memory" },
            { "heavy_meshes", "Heavy Meshes" },
            { "scan_project", "Scan Entire Project" },
            { "danger_zone", "DANGER ZONE" },
            { "unused_assets_warning", "Unused asset deletion is permanent and cannot use Unity Undo. The scan is intentionally conservative, but runtime-only references cannot always be detected. Review both warnings before deleting anything." },
            { "delete_unused_assets", "Find and Permanently Delete Unused Assets" },
            { "last_result", "Last result" },
            { "ready", "Choose an action." },
            { "all", "ALL" },
            { "critical", "CRITICAL" },
            { "warning", "WARNING" },
            { "select", "SELECT" },
            { "no_findings", "No findings in this filter." },
            { "compression", "Compression" },
            { "pc", "PC / Standalone" },
            { "android", "Android / Mobile" },
            { "ios", "iOS" },
            { "texture_settings", "Texture settings" },
            { "particle_settings", "Particle settings" },
            { "model_settings", "Model settings" },
            { "cap_particles", "Cap particle count" },
            { "max_particles", "Maximum particles" },
            { "cap_lifetime", "Cap constant lifetime" },
            { "max_lifetime", "Maximum lifetime" },
            { "disable_trails", "Disable trails" },
            { "disable_collision", "Disable collision" },
            { "disable_noise", "Disable noise" },
            { "disable_particle_lights", "Disable particle lights" },
            { "disable_particle_shadows", "Disable particle shadows" },
            { "disable_subemitters", "Disable sub emitters" },
            { "batch_options", "Batch options" },
            { "test_import_memory", "Trial: keep only native asset-memory savings" },
            { "protect_detail", "Protect selected detail" },
            { "allow_detail", "Allow optimization of selection" },
            { "reset_selected_history", "Reset history for selection" },
            { "restore_import_batch", "Restore last import batch" },
            { "detail_protected", "Selected texture/model assets are protected from import and UV changes." },
            { "detail_allowed", "Selection may be optimized again; manual edits remain protected by history." },
            { "history_reset", "Selected import history reset. Current settings become the next baseline." },
            { "up_to_date", "Up to date" },
            { "update_available", "Update available" },
            { "update_recommended", "Update recommended" },
            { "update_unknown", "Update status unknown" },
            { "checking", "Checking..." },
            { "check_update", "Check update" },
            { "support", "Support development" }
        };

        static readonly Dictionary<OYPLanguage, Dictionary<string, string>> Translations =
            new Dictionary<OYPLanguage, Dictionary<string, string>>
        {
            { OYPLanguage.Japanese, new Dictionary<string, string>
                {
                    { "project", "プロジェクト" }, { "avatar", "キャラクター / アバター" }, { "language", "言語" },
                    { "scope", "アセット範囲" }, { "assets_folder", "Assets フォルダー" }, { "use_selection", "選択を使用" },
                    { "avatar_root", "キャラクター / アバターのルート" }, { "one_click", "ワンクリック" },
                    { "optimize_textures", "テクスチャを最適化" }, { "optimize_models", "モデルインポートを最適化" },
                    { "optimize_particles", "パーティクルを最適化" }, { "fix_materials", "マテリアル負荷を修正" },
                    { "optimize_lighting", "ライティングを最適化" }, { "disable_shadows", "リアルタイム影を無効化" },
                    { "optimize_ui_raycasts", "UI レイキャストを最適化" }, { "clean_missing_scripts", "欠落スクリプトを削除" }, { "advanced", "詳細設定" },
                    { "review", "確認" }, { "largest_textures", "最大テクスチャ" }, { "readwrite_review", "Read/Write メモリ" },
                    { "heavy_meshes", "重いメッシュ" }, { "scan_project", "プロジェクト全体をスキャン" },
                    { "last_result", "最後の結果" }, { "ready", "操作を選択してください。" }, { "support", "開発を支援" }
                }
            },
            { OYPLanguage.SimplifiedChinese, new Dictionary<string, string>
                {
                    { "project", "项目" }, { "avatar", "角色 / 虚拟形象" }, { "language", "语言" },
                    { "scope", "资源范围" }, { "assets_folder", "Assets 文件夹" }, { "use_selection", "使用选择" },
                    { "avatar_root", "角色 / 虚拟形象根节点" }, { "one_click", "一键操作" },
                    { "optimize_textures", "优化纹理" }, { "optimize_models", "优化模型导入" },
                    { "optimize_particles", "优化粒子" }, { "fix_materials", "修复材质开销" },
                    { "optimize_lighting", "优化灯光" }, { "disable_shadows", "关闭实时阴影" },
                    { "optimize_ui_raycasts", "优化 UI 射线检测" }, { "clean_missing_scripts", "清理缺失脚本" }, { "advanced", "高级设置" },
                    { "review", "检查" }, { "largest_textures", "最大纹理" }, { "readwrite_review", "读写内存" },
                    { "heavy_meshes", "高开销网格" }, { "scan_project", "扫描整个项目" },
                    { "last_result", "上次结果" }, { "ready", "请选择一个操作。" }, { "support", "支持开发" }
                }
            },
            { OYPLanguage.TraditionalChinese, new Dictionary<string, string>
                {
                    { "project", "專案" }, { "avatar", "角色 / 虛擬形象" }, { "language", "語言" },
                    { "scope", "資產範圍" }, { "assets_folder", "Assets 資料夾" }, { "use_selection", "使用選取項目" },
                    { "avatar_root", "角色 / 虛擬形象根節點" }, { "one_click", "一鍵操作" },
                    { "optimize_textures", "最佳化材質貼圖" }, { "optimize_models", "最佳化模型匯入" },
                    { "optimize_particles", "最佳化粒子" }, { "fix_materials", "修正材質成本" },
                    { "optimize_lighting", "最佳化燈光" }, { "disable_shadows", "停用即時陰影" },
                    { "optimize_ui_raycasts", "最佳化 UI 射線偵測" }, { "clean_missing_scripts", "清理遺失腳本" }, { "advanced", "進階設定" },
                    { "review", "檢查" }, { "largest_textures", "最大材質貼圖" }, { "readwrite_review", "Read/Write 記憶體" },
                    { "heavy_meshes", "高負載網格" }, { "scan_project", "掃描整個專案" },
                    { "last_result", "上次結果" }, { "ready", "請選擇一個操作。" }, { "support", "支持開發" }
                }
            },
            { OYPLanguage.Korean, new Dictionary<string, string>
                {
                    { "project", "프로젝트" }, { "avatar", "캐릭터 / 아바타" }, { "language", "언어" },
                    { "scope", "에셋 범위" }, { "assets_folder", "Assets 폴더" }, { "use_selection", "선택 사용" },
                    { "avatar_root", "캐릭터 / 아바타 루트" }, { "one_click", "원클릭" },
                    { "optimize_textures", "텍스처 최적화" }, { "optimize_models", "모델 임포트 최적화" },
                    { "optimize_particles", "파티클 최적화" }, { "fix_materials", "머티리얼 비용 수정" },
                    { "optimize_lighting", "라이팅 최적화" }, { "disable_shadows", "실시간 그림자 비활성화" },
                    { "optimize_ui_raycasts", "UI 레이캐스트 최적화" }, { "clean_missing_scripts", "누락 스크립트 정리" }, { "advanced", "고급 설정" },
                    { "review", "검토" }, { "largest_textures", "가장 큰 텍스처" }, { "readwrite_review", "Read/Write 메모리" },
                    { "heavy_meshes", "무거운 메시" }, { "scan_project", "전체 프로젝트 스캔" },
                    { "last_result", "마지막 결과" }, { "ready", "작업을 선택하세요." }, { "support", "개발 후원" }
                }
            },
            { OYPLanguage.Spanish, new Dictionary<string, string>
                {
                    { "project", "PROYECTO" }, { "avatar", "PERSONAJE / AVATAR" }, { "language", "Idioma" },
                    { "scope", "Alcance de recursos" }, { "assets_folder", "Carpeta Assets" }, { "use_selection", "Usar selección" },
                    { "avatar_root", "Raíz del personaje / avatar" }, { "one_click", "UN CLIC" },
                    { "optimize_textures", "Optimizar texturas" }, { "optimize_models", "Optimizar importación de modelos" },
                    { "optimize_particles", "Optimizar partículas" }, { "fix_materials", "Corregir coste de materiales" },
                    { "optimize_lighting", "Optimizar iluminación" }, { "disable_shadows", "Desactivar sombras en tiempo real" },
                    { "optimize_ui_raycasts", "Optimizar raycasts de UI" }, { "clean_missing_scripts", "Limpiar scripts faltantes" }, { "advanced", "Ajustes avanzados" },
                    { "review", "REVISAR" }, { "largest_textures", "Texturas más grandes" }, { "readwrite_review", "Memoria Read/Write" },
                    { "heavy_meshes", "Mallas pesadas" }, { "scan_project", "Escanear proyecto completo" },
                    { "last_result", "Último resultado" }, { "ready", "Elige una acción." }, { "support", "Apoyar el desarrollo" }
                }
            },
            { OYPLanguage.French, new Dictionary<string, string>
                {
                    { "project", "PROJET" }, { "avatar", "PERSONNAGE / AVATAR" }, { "language", "Langue" },
                    { "scope", "Portée des ressources" }, { "assets_folder", "Dossier Assets" }, { "use_selection", "Utiliser la sélection" },
                    { "avatar_root", "Racine du personnage / avatar" }, { "one_click", "UN CLIC" },
                    { "optimize_textures", "Optimiser les textures" }, { "optimize_models", "Optimiser l'import des modèles" },
                    { "optimize_particles", "Optimiser les particules" }, { "fix_materials", "Corriger le coût des matériaux" },
                    { "optimize_lighting", "Optimiser l'éclairage" }, { "disable_shadows", "Désactiver les ombres temps réel" },
                    { "optimize_ui_raycasts", "Optimiser les raycasts UI" }, { "clean_missing_scripts", "Nettoyer les scripts manquants" }, { "advanced", "Paramètres avancés" },
                    { "review", "ANALYSE" }, { "largest_textures", "Textures les plus grandes" }, { "readwrite_review", "Mémoire Read/Write" },
                    { "heavy_meshes", "Maillages lourds" }, { "scan_project", "Analyser tout le projet" },
                    { "last_result", "Dernier résultat" }, { "ready", "Choisissez une action." }, { "support", "Soutenir le développement" }
                }
            },
            { OYPLanguage.German, new Dictionary<string, string>
                {
                    { "project", "PROJEKT" }, { "avatar", "CHARAKTER / AVATAR" }, { "language", "Sprache" },
                    { "scope", "Asset-Bereich" }, { "assets_folder", "Assets-Ordner" }, { "use_selection", "Auswahl verwenden" },
                    { "avatar_root", "Charakter- / Avatar-Stamm" }, { "one_click", "EIN KLICK" },
                    { "optimize_textures", "Texturen optimieren" }, { "optimize_models", "Modellimporte optimieren" },
                    { "optimize_particles", "Partikel optimieren" }, { "fix_materials", "Materialkosten beheben" },
                    { "optimize_lighting", "Beleuchtung optimieren" }, { "disable_shadows", "Echtzeitschatten deaktivieren" },
                    { "optimize_ui_raycasts", "UI-Raycasts optimieren" }, { "clean_missing_scripts", "Fehlende Skripte bereinigen" }, { "advanced", "Erweiterte Einstellungen" },
                    { "review", "PRÜFEN" }, { "largest_textures", "Größte Texturen" }, { "readwrite_review", "Read/Write-Speicher" },
                    { "heavy_meshes", "Schwere Meshes" }, { "scan_project", "Gesamtes Projekt scannen" },
                    { "last_result", "Letztes Ergebnis" }, { "ready", "Aktion auswählen." }, { "support", "Entwicklung unterstützen" }
                }
            },
            { OYPLanguage.Portuguese, new Dictionary<string, string>
                {
                    { "project", "PROJETO" }, { "avatar", "PERSONAGEM / AVATAR" }, { "language", "Idioma" },
                    { "scope", "Escopo de assets" }, { "assets_folder", "Pasta Assets" }, { "use_selection", "Usar seleção" },
                    { "avatar_root", "Raiz do personagem / avatar" }, { "one_click", "UM CLIQUE" },
                    { "optimize_textures", "Otimizar texturas" }, { "optimize_models", "Otimizar importação de modelos" },
                    { "optimize_particles", "Otimizar partículas" }, { "fix_materials", "Corrigir custo de materiais" },
                    { "optimize_lighting", "Otimizar iluminação" }, { "disable_shadows", "Desativar sombras em tempo real" },
                    { "optimize_ui_raycasts", "Otimizar raycasts da UI" }, { "clean_missing_scripts", "Limpar scripts ausentes" }, { "advanced", "Configurações avançadas" },
                    { "review", "REVISAR" }, { "largest_textures", "Maiores texturas" }, { "readwrite_review", "Memória Read/Write" },
                    { "heavy_meshes", "Meshes pesadas" }, { "scan_project", "Escanear projeto inteiro" },
                    { "last_result", "Último resultado" }, { "ready", "Escolha uma ação." }, { "support", "Apoiar o desenvolvimento" }
                }
            },
            { OYPLanguage.Russian, new Dictionary<string, string>
                {
                    { "project", "ПРОЕКТ" }, { "avatar", "ПЕРСОНАЖ / АВАТАР" }, { "language", "Язык" },
                    { "scope", "Область ресурсов" }, { "assets_folder", "Папка Assets" }, { "use_selection", "Использовать выбранное" },
                    { "avatar_root", "Корень персонажа / аватара" }, { "one_click", "В ОДИН КЛИК" },
                    { "optimize_textures", "Оптимизировать текстуры" }, { "optimize_models", "Оптимизировать импорт моделей" },
                    { "optimize_particles", "Оптимизировать частицы" }, { "fix_materials", "Исправить стоимость материалов" },
                    { "optimize_lighting", "Оптимизировать освещение" }, { "disable_shadows", "Отключить тени реального времени" },
                    { "optimize_ui_raycasts", "Оптимизировать UI Raycast" }, { "clean_missing_scripts", "Очистить отсутствующие скрипты" }, { "advanced", "Расширенные настройки" },
                    { "review", "ПРОВЕРКА" }, { "largest_textures", "Самые большие текстуры" }, { "readwrite_review", "Память Read/Write" },
                    { "heavy_meshes", "Тяжёлые меши" }, { "scan_project", "Сканировать весь проект" },
                    { "last_result", "Последний результат" }, { "ready", "Выберите действие." }, { "support", "Поддержать разработку" }
                }
            },
            { OYPLanguage.Italian, new Dictionary<string, string>
                {
                    { "project", "PROGETTO" }, { "avatar", "PERSONAGGIO / AVATAR" }, { "language", "Lingua" },
                    { "scope", "Ambito risorse" }, { "assets_folder", "Cartella Assets" }, { "use_selection", "Usa selezione" },
                    { "avatar_root", "Radice personaggio / avatar" }, { "one_click", "UN CLIC" },
                    { "optimize_textures", "Ottimizza texture" }, { "optimize_models", "Ottimizza importazione modelli" },
                    { "optimize_particles", "Ottimizza particelle" }, { "fix_materials", "Correggi costo materiali" },
                    { "optimize_lighting", "Ottimizza illuminazione" }, { "disable_shadows", "Disattiva ombre in tempo reale" },
                    { "optimize_ui_raycasts", "Ottimizza raycast UI" }, { "clean_missing_scripts", "Pulisci script mancanti" }, { "advanced", "Impostazioni avanzate" },
                    { "review", "REVISIONE" }, { "largest_textures", "Texture più grandi" }, { "readwrite_review", "Memoria Read/Write" },
                    { "heavy_meshes", "Mesh pesanti" }, { "scan_project", "Scansiona intero progetto" },
                    { "last_result", "Ultimo risultato" }, { "ready", "Scegli un'azione." }, { "support", "Supporta lo sviluppo" }
                }
            }
        };

        internal static OYPLanguage Current
        {
            get
            {
                if (EditorPrefs.HasKey(PreferenceKey))
                {
                    int stored = EditorPrefs.GetInt(PreferenceKey, 0);
                    return Enum.IsDefined(typeof(OYPLanguage), stored) ? (OYPLanguage)stored : OYPLanguage.Auto;
                }

                if (EditorPrefs.HasKey(LegacyPreferenceKey))
                {
                    int legacy = EditorPrefs.GetInt(LegacyPreferenceKey, 0);
                    switch (legacy)
                    {
                        case 1: return OYPLanguage.Japanese;
                        case 2: return OYPLanguage.SimplifiedChinese;
                        case 3: return OYPLanguage.Korean;
                        default: return OYPLanguage.English;
                    }
                }

                return OYPLanguage.Auto;
            }
            set { EditorPrefs.SetInt(PreferenceKey, (int)value); }
        }

        internal static OYPLanguage Effective => Current == OYPLanguage.Auto ? DetectSystemLanguage() : Current;

        internal static string[] LanguageNames => new[]
        {
            "Auto (" + NativeName(DetectSystemLanguage()) + ")",
            "English",
            "日本語",
            "简体中文",
            "繁體中文",
            "한국어",
            "Español",
            "Français",
            "Deutsch",
            "Português",
            "Русский",
            "Italiano"
        };

        internal static string T(string key)
        {
            OYPLanguage language = Effective;
            if (language != OYPLanguage.English &&
                Translations.TryGetValue(language, out var table) &&
                table.TryGetValue(key, out var translated) &&
                !string.IsNullOrEmpty(translated))
                return translated;

            return English.TryGetValue(key, out var english) ? english : key;
        }

        static OYPLanguage DetectSystemLanguage()
        {
            switch (Application.systemLanguage)
            {
                case SystemLanguage.Japanese: return OYPLanguage.Japanese;
                case SystemLanguage.ChineseSimplified: return OYPLanguage.SimplifiedChinese;
                case SystemLanguage.ChineseTraditional: return OYPLanguage.TraditionalChinese;
                case SystemLanguage.Korean: return OYPLanguage.Korean;
                case SystemLanguage.Spanish: return OYPLanguage.Spanish;
                case SystemLanguage.French: return OYPLanguage.French;
                case SystemLanguage.German: return OYPLanguage.German;
                case SystemLanguage.Portuguese: return OYPLanguage.Portuguese;
                case SystemLanguage.Russian: return OYPLanguage.Russian;
                case SystemLanguage.Italian: return OYPLanguage.Italian;
                default: return OYPLanguage.English;
            }
        }

        static string NativeName(OYPLanguage language)
        {
            switch (language)
            {
                case OYPLanguage.Japanese: return "日本語";
                case OYPLanguage.SimplifiedChinese: return "简体中文";
                case OYPLanguage.TraditionalChinese: return "繁體中文";
                case OYPLanguage.Korean: return "한국어";
                case OYPLanguage.Spanish: return "Español";
                case OYPLanguage.French: return "Français";
                case OYPLanguage.German: return "Deutsch";
                case OYPLanguage.Portuguese: return "Português";
                case OYPLanguage.Russian: return "Русский";
                case OYPLanguage.Italian: return "Italiano";
                default: return "English";
            }
        }
    }
}
