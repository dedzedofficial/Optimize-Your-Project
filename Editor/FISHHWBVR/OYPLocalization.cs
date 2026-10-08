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
        Italian,
        Dutch,
        Polish,
        Turkish
    }

    internal static class OYPLocalization
    {
        const string PreferenceKey = "FISHHWB.OptimizeYourProject.Language.v0800";
        const string LegacyPreferenceKey = "FISHHWB.OptimizeYourProject.Language.v0760";

        static readonly Dictionary<string, string> English = new Dictionary<string, string>
        {
            { "project", "PROJECT" }, { "avatar", "CHARACTER / AVATAR" }, { "language", "Language" },
            { "developer_optimizer", "One-click optimization for real-time projects" },
            { "project_scope", "Project asset scope" }, { "scope_help", "Choose which Assets folder the project-wide import and cleanup actions are allowed to inspect." },
            { "scope", "Asset scope" }, { "assets_folder", "Assets folder" }, { "use_selection", "Use selection" },
            { "invalid_folder", "Choose an existing folder under Assets." }, { "avatar_root", "Character / Avatar root" },
            { "avatar_help", "Select a character or avatar root in a loaded scene." }, { "one_click", "ONE CLICK" },
            { "optimize_textures", "Optimize Textures" }, { "optimize_models", "Optimize Model Imports" },
            { "optimize_particles", "Optimize Particles" }, { "fix_materials", "Fix Material Costs" },
            { "optimize_lighting", "Optimize Lighting" }, { "disable_shadows", "Disable Realtime Shadows" },
            { "optimize_ui_raycasts", "Optimize UI Raycasts" }, { "optimize_audio", "Optimize Audio" },
            { "clean_missing_scripts", "Clean Missing Scripts" }, { "advanced", "Advanced settings" },
            { "review", "REVIEW" }, { "largest_textures", "Largest Textures" }, { "readwrite_review", "Read/Write Memory" },
            { "heavy_meshes", "Heavy Meshes" }, { "scan_project", "Scan Entire Project" }, { "danger_zone", "DANGER ZONE" },
            { "unused_assets_warning", "Unused asset deletion is permanent and cannot use Unity Undo. The scan is intentionally conservative, but runtime-only references cannot always be detected. Review both warnings before deleting anything." },
            { "delete_unused_assets", "Find and Permanently Delete Unused Assets" }, { "last_result", "Last result" },
            { "ready", "Choose an action." }, { "all", "ALL" }, { "critical", "CRITICAL" }, { "warning", "WARNING" },
            { "select", "SELECT" }, { "no_findings", "No findings in this filter." }, { "compression", "Compression" },
            { "pc", "PC / Standalone" }, { "android", "Android / Mobile" }, { "ios", "iOS" },
            { "texture_settings", "Texture settings" }, { "particle_settings", "Particle settings" }, { "model_settings", "Model settings" },
            { "cap_particles", "Cap particle count" }, { "max_particles", "Maximum particles" },
            { "cap_lifetime", "Cap constant lifetime" }, { "max_lifetime", "Maximum lifetime" },
            { "disable_trails", "Disable trails" }, { "disable_collision", "Disable collision" }, { "disable_noise", "Disable noise" },
            { "disable_particle_lights", "Disable particle lights" }, { "disable_particle_shadows", "Disable particle shadows" },
            { "disable_subemitters", "Disable sub emitters" }, { "batch_options", "Batch options" },
            { "test_import_memory", "Trial: keep only native asset-memory savings" }, { "protect_detail", "Protect selected detail" },
            { "allow_detail", "Allow optimization of selection" }, { "reset_selected_history", "Reset history for selection" },
            { "restore_import_batch", "Restore last import batch" }, { "detail_protected", "Selected texture/model assets are protected from import and UV changes." },
            { "detail_allowed", "Selection may be optimized again; manual edits remain protected by history." },
            { "history_reset", "Selected import history reset. Current settings become the next baseline." },
            { "up_to_date", "Up to date" }, { "update_available", "Update available" }, { "update_recommended", "Update recommended" },
            { "update_unknown", "Update status unknown" }, { "checking", "Checking..." }, { "check_update", "Check update" },
            { "support", "Support development" }
        };

        static Dictionary<string, string> Basic(string project, string avatar, string language, string oneClick, string textures,
            string models, string particles, string materials, string lighting, string shadows, string ui, string audio,
            string missing, string advanced, string review, string scan, string last, string ready, string support)
        {
            return new Dictionary<string, string>
            {
                { "project", project }, { "avatar", avatar }, { "language", language }, { "one_click", oneClick },
                { "optimize_textures", textures }, { "optimize_models", models }, { "optimize_particles", particles },
                { "fix_materials", materials }, { "optimize_lighting", lighting }, { "disable_shadows", shadows },
                { "optimize_ui_raycasts", ui }, { "optimize_audio", audio }, { "clean_missing_scripts", missing },
                { "advanced", advanced }, { "review", review }, { "scan_project", scan }, { "last_result", last },
                { "ready", ready }, { "support", support }
            };
        }

        static readonly Dictionary<OYPLanguage, Dictionary<string, string>> Translations = new Dictionary<OYPLanguage, Dictionary<string, string>>
        {
            { OYPLanguage.Japanese, Basic("プロジェクト", "キャラクター / アバター", "言語", "ワンクリック", "テクスチャを最適化", "モデルインポートを最適化", "パーティクルを最適化", "マテリアル負荷を修正", "ライティングを最適化", "リアルタイム影を無効化", "UI レイキャストを最適化", "オーディオを最適化", "欠落スクリプトを削除", "詳細設定", "確認", "プロジェクト全体をスキャン", "最後の結果", "操作を選択してください。", "開発を支援") },
            { OYPLanguage.SimplifiedChinese, Basic("项目", "角色 / 虚拟形象", "语言", "一键操作", "优化纹理", "优化模型导入", "优化粒子", "修复材质开销", "优化灯光", "关闭实时阴影", "优化 UI 射线检测", "优化音频", "清理缺失脚本", "高级设置", "检查", "扫描整个项目", "上次结果", "请选择一个操作。", "支持开发") },
            { OYPLanguage.TraditionalChinese, Basic("專案", "角色 / 虛擬形象", "語言", "一鍵操作", "最佳化材質貼圖", "最佳化模型匯入", "最佳化粒子", "修正材質成本", "最佳化燈光", "停用即時陰影", "最佳化 UI 射線偵測", "最佳化音訊", "清理遺失腳本", "進階設定", "檢查", "掃描整個專案", "上次結果", "請選擇一個操作。", "支持開發") },
            { OYPLanguage.Korean, Basic("프로젝트", "캐릭터 / 아바타", "언어", "원클릭", "텍스처 최적화", "모델 임포트 최적화", "파티클 최적화", "머티리얼 비용 수정", "라이팅 최적화", "실시간 그림자 비활성화", "UI 레이캐스트 최적화", "오디오 최적화", "누락 스크립트 정리", "고급 설정", "검토", "전체 프로젝트 스캔", "마지막 결과", "작업을 선택하세요.", "개발 후원") },
            { OYPLanguage.Spanish, Basic("PROYECTO", "PERSONAJE / AVATAR", "Idioma", "UN CLIC", "Optimizar texturas", "Optimizar importación de modelos", "Optimizar partículas", "Corregir coste de materiales", "Optimizar iluminación", "Desactivar sombras en tiempo real", "Optimizar raycasts de UI", "Optimizar audio", "Limpiar scripts faltantes", "Ajustes avanzados", "REVISAR", "Escanear proyecto completo", "Último resultado", "Elige una acción.", "Apoyar el desarrollo") },
            { OYPLanguage.French, Basic("PROJET", "PERSONNAGE / AVATAR", "Langue", "UN CLIC", "Optimiser les textures", "Optimiser l'import des modèles", "Optimiser les particules", "Corriger le coût des matériaux", "Optimiser l'éclairage", "Désactiver les ombres temps réel", "Optimiser les raycasts UI", "Optimiser l'audio", "Nettoyer les scripts manquants", "Paramètres avancés", "ANALYSE", "Analyser tout le projet", "Dernier résultat", "Choisissez une action.", "Soutenir le développement") },
            { OYPLanguage.German, Basic("PROJEKT", "CHARAKTER / AVATAR", "Sprache", "EIN KLICK", "Texturen optimieren", "Modellimporte optimieren", "Partikel optimieren", "Materialkosten beheben", "Beleuchtung optimieren", "Echtzeitschatten deaktivieren", "UI-Raycasts optimieren", "Audio optimieren", "Fehlende Skripte bereinigen", "Erweiterte Einstellungen", "PRÜFEN", "Gesamtes Projekt scannen", "Letztes Ergebnis", "Aktion auswählen.", "Entwicklung unterstützen") },
            { OYPLanguage.Portuguese, Basic("PROJETO", "PERSONAGEM / AVATAR", "Idioma", "UM CLIQUE", "Otimizar texturas", "Otimizar importação de modelos", "Otimizar partículas", "Corrigir custo de materiais", "Otimizar iluminação", "Desativar sombras em tempo real", "Otimizar raycasts da UI", "Otimizar áudio", "Limpar scripts ausentes", "Configurações avançadas", "REVISÃO", "Analisar projeto inteiro", "Último resultado", "Escolha uma ação.", "Apoiar o desenvolvimento") },
            { OYPLanguage.Russian, Basic("ПРОЕКТ", "ПЕРСОНАЖ / АВАТАР", "Язык", "ОДИН КЛИК", "Оптимизировать текстуры", "Оптимизировать импорт моделей", "Оптимизировать частицы", "Исправить стоимость материалов", "Оптимизировать освещение", "Отключить тени в реальном времени", "Оптимизировать UI Raycast", "Оптимизировать аудио", "Очистить отсутствующие скрипты", "Расширенные настройки", "ПРОВЕРКА", "Сканировать весь проект", "Последний результат", "Выберите действие.", "Поддержать разработку") },
            { OYPLanguage.Italian, Basic("PROGETTO", "PERSONAGGIO / AVATAR", "Lingua", "UN CLIC", "Ottimizza texture", "Ottimizza import modelli", "Ottimizza particelle", "Correggi costi materiali", "Ottimizza illuminazione", "Disattiva ombre in tempo reale", "Ottimizza raycast UI", "Ottimizza audio", "Pulisci script mancanti", "Impostazioni avanzate", "REVISIONE", "Scansiona intero progetto", "Ultimo risultato", "Scegli un'azione.", "Supporta lo sviluppo") },
            { OYPLanguage.Dutch, Basic("PROJECT", "PERSONAGE / AVATAR", "Taal", "ÉÉN KLIK", "Texturen optimaliseren", "Modelimport optimaliseren", "Deeltjes optimaliseren", "Materiaalkosten herstellen", "Belichting optimaliseren", "Realtime schaduwen uitschakelen", "UI-raycasts optimaliseren", "Audio optimaliseren", "Ontbrekende scripts opschonen", "Geavanceerde instellingen", "CONTROLEREN", "Hele project scannen", "Laatste resultaat", "Kies een actie.", "Ontwikkeling steunen") },
            { OYPLanguage.Polish, Basic("PROJEKT", "POSTAĆ / AWATAR", "Język", "JEDNO KLIKNIĘCIE", "Optymalizuj tekstury", "Optymalizuj import modeli", "Optymalizuj cząsteczki", "Napraw koszt materiałów", "Optymalizuj oświetlenie", "Wyłącz cienie czasu rzeczywistego", "Optymalizuj raycasty UI", "Optymalizuj audio", "Usuń brakujące skrypty", "Ustawienia zaawansowane", "PRZEGLĄD", "Skanuj cały projekt", "Ostatni wynik", "Wybierz działanie.", "Wesprzyj rozwój") },
            { OYPLanguage.Turkish, Basic("PROJE", "KARAKTER / AVATAR", "Dil", "TEK TIK", "Dokuları optimize et", "Model içe aktarmalarını optimize et", "Parçacıkları optimize et", "Malzeme maliyetlerini düzelt", "Aydınlatmayı optimize et", "Gerçek zamanlı gölgeleri kapat", "UI ışınlarını optimize et", "Sesi optimize et", "Eksik betikleri temizle", "Gelişmiş ayarlar", "İNCELE", "Tüm projeyi tara", "Son sonuç", "Bir işlem seçin.", "Geliştirmeyi destekle") }
        };

        internal static OYPLanguage Current
        {
            get
            {
                if (EditorPrefs.HasKey(PreferenceKey))
                {
                    int stored = EditorPrefs.GetInt(PreferenceKey, 0);
                    return System.Enum.IsDefined(typeof(OYPLanguage), stored) ? (OYPLanguage)stored : OYPLanguage.Auto;
                }
                if (EditorPrefs.HasKey(LegacyPreferenceKey))
                {
                    int legacy = EditorPrefs.GetInt(LegacyPreferenceKey, 0);
                    return System.Enum.IsDefined(typeof(OYPLanguage), legacy) ? (OYPLanguage)legacy : OYPLanguage.Auto;
                }
                return OYPLanguage.Auto;
            }
            set { EditorPrefs.SetInt(PreferenceKey, (int)value); }
        }

        internal static OYPLanguage Effective => Current == OYPLanguage.Auto ? DetectSystemLanguage() : Current;

        internal static string[] LanguageNames => new[]
        {
            "Auto (" + NativeName(DetectSystemLanguage()) + ")", "English", "日本語", "简体中文", "繁體中文", "한국어",
            "Español", "Français", "Deutsch", "Português", "Русский", "Italiano", "Nederlands", "Polski", "Türkçe"
        };

        internal static string T(string key)
        {
            OYPLanguage language = Effective;
            if (language != OYPLanguage.English && Translations.TryGetValue(language, out var table) && table.TryGetValue(key, out var translated) && !string.IsNullOrEmpty(translated))
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
                case SystemLanguage.Dutch: return OYPLanguage.Dutch;
                case SystemLanguage.Polish: return OYPLanguage.Polish;
                case SystemLanguage.Turkish: return OYPLanguage.Turkish;
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
                case OYPLanguage.Dutch: return "Nederlands";
                case OYPLanguage.Polish: return "Polski";
                case OYPLanguage.Turkish: return "Türkçe";
                default: return "English";
            }
        }
    }
}
