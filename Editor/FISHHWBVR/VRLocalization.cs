using System;
using System.Collections.Generic;
using UnityEditor;

namespace FISHHWB.VROptimizer
{
    internal enum VRLanguage
    {
        English,
        Japanese,
        SimplifiedChinese,
        Korean
    }

    internal static class VRLocalization
    {
        const string PreferenceKey = "FISHHWB.VROptimizer.Language.v074";

        static readonly Dictionary<string, string[]> Strings = new Dictionary<string, string[]>
        {
            { "language", new[] { "Language", "言語", "语言", "언어" } },
            { "english", new[] { "English", "英語", "英语", "영어" } },
            { "japanese", new[] { "Japanese", "日本語", "日语", "일본어" } },
            { "chinese", new[] { "Chinese (Simplified)", "中国語（簡体字）", "简体中文", "중국어(간체)" } },
            { "korean", new[] { "Korean", "韓国語", "韩语", "한국어" } },
            { "project", new[] { "PROJECT", "プロジェクト", "项目", "프로젝트" } },
            { "avatar", new[] { "CHARACTER / AVATAR", "キャラクター / アバター", "角色 / 虚拟形象", "캐릭터 / 아바타" } },
            { "search", new[] { "Find an action", "アクションを検索", "查找操作", "작업 찾기" } },
            { "search_hint", new[] { "Type texture, mesh, material, particles, lights, memory or scan.", "texture、mesh、material、particles、lights、memory、scan などを入力します。", "输入 texture、mesh、material、particles、lights、memory 或 scan。", "texture, mesh, material, particles, lights, memory 또는 scan을 입력하세요." } },
            { "project_intro", new[] { "Fast optimization for assets and loaded scenes. Search for a task or run the focused buttons below.", "アセットと読み込み済みシーンを高速に最適化します。タスクを検索するか、下のボタンを実行してください。", "快速优化资源和已加载场景。搜索任务或使用下面的专用按钮。", "에셋과 로드된 씬을 빠르게 최적화합니다. 작업을 검색하거나 아래 버튼을 실행하세요." } },
            { "avatar_intro", new[] { "Optimize one character hierarchy without changing the rest of the loaded scene.", "読み込み済みシーンの他の部分を変更せず、1つのキャラクター階層を最適化します。", "仅优化一个角色层级，不更改已加载场景的其余部分。", "로드된 씬의 다른 부분을 바꾸지 않고 하나의 캐릭터 계층만 최적화합니다." } },
            { "asset_scope", new[] { "ASSET SCOPE", "アセット範囲", "资源范围", "에셋 범위" } },
            { "asset_scope_desc", new[] { "Choose which Assets folder texture and memory review jobs should inspect.", "テクスチャとメモリ確認の対象となる Assets フォルダーを選びます。", "选择纹理和内存检查要扫描的 Assets 文件夹。", "텍스처 및 메모리 검토가 확인할 Assets 폴더를 선택하세요." } },
            { "assets_folder", new[] { "Assets folder", "Assets フォルダー", "Assets 文件夹", "Assets 폴더" } },
            { "use_selection", new[] { "USE CURRENT SELECTION", "現在の選択を使用", "使用当前选择", "현재 선택 사용" } },
            { "invalid_folder", new[] { "Enter an existing folder under Assets.", "Assets 配下の既存フォルダーを入力してください。", "请输入 Assets 下已有的文件夹。", "Assets 아래의 기존 폴더를 입력하세요." } },
            { "textures", new[] { "TEXTURES", "テクスチャ", "纹理", "텍스처" } },
            { "textures_desc_project", new[] { "Resize and compress supported textures in the selected Assets folder.", "選択した Assets フォルダー内の対応テクスチャをリサイズして圧縮します。", "调整并压缩所选 Assets 文件夹中的受支持纹理。", "선택한 Assets 폴더의 지원되는 텍스처 크기를 조정하고 압축합니다." } },
            { "textures_desc_avatar", new[] { "Resize and compress textures referenced by this character hierarchy.", "このキャラクター階層が参照するテクスチャをリサイズして圧縮します。", "调整并压缩此角色层级引用的纹理。", "이 캐릭터 계층이 참조하는 텍스처 크기를 조정하고 압축합니다." } },
            { "compress_textures", new[] { "COMPRESS & SIZE TEXTURES", "テクスチャを圧縮・サイズ調整", "压缩并调整纹理尺寸", "텍스처 압축 및 크기 조정" } },
            { "fix_texture_imports", new[] { "FIX TEXTURE IMPORT SETTINGS", "テクスチャインポート設定を修正", "修复纹理导入设置", "텍스처 임포트 설정 수정" } },
            { "particles", new[] { "PARTICLES", "パーティクル", "粒子", "파티클" } },
            { "particles_project", new[] { "Apply the selected limits to particle systems in loaded scenes.", "読み込み済みシーンのパーティクルシステムに選択した制限を適用します。", "将所选限制应用到已加载场景中的粒子系统。", "로드된 씬의 파티클 시스템에 선택한 제한을 적용합니다." } },
            { "particles_avatar", new[] { "Apply the selected limits to particle systems under this character hierarchy.", "このキャラクター階層内のパーティクルシステムに選択した制限を適用します。", "将所选限制应用到此角色层级下的粒子系统。", "이 캐릭터 계층 아래의 파티클 시스템에 선택한 제한을 적용합니다." } },
            { "optimize_particles", new[] { "OPTIMIZE PARTICLES", "パーティクルを最適化", "优化粒子", "파티클 최적화" } },
            { "mesh_imports", new[] { "MESH IMPORTS", "メッシュインポート", "网格导入", "메시 임포트" } },
            { "mesh_project", new[] { "Apply Unity mesh compression to imported models used by loaded scenes.", "読み込み済みシーンで使用されるインポートモデルに Unity のメッシュ圧縮を適用します。", "对已加载场景使用的导入模型应用 Unity 网格压缩。", "로드된 씬에서 사용하는 임포트 모델에 Unity 메시 압축을 적용합니다." } },
            { "mesh_avatar", new[] { "Apply Unity mesh compression to imported models referenced by this character hierarchy.", "このキャラクター階層が参照するインポートモデルに Unity のメッシュ圧縮を適用します。", "对此角色层级引用的导入模型应用 Unity 网格压缩。", "이 캐릭터 계층이 참조하는 임포트 모델에 Unity 메시 압축을 적용합니다." } },
            { "compress_meshes", new[] { "COMPRESS IMPORTED MESHES", "インポートメッシュを圧縮", "压缩导入网格", "임포트 메시 압축" } },
            { "materials", new[] { "MATERIALS & DRAW COST", "マテリアルと描画コスト", "材质与绘制开销", "머티리얼 및 드로우 비용" } },
            { "materials_project", new[] { "Automatically fix exact duplicate material references and safe material-slot cost issues in loaded scenes.", "完全一致する重複マテリアル参照と安全に修正できるマテリアルスロット問題を読み込み済みシーンで自動修正します。", "自动修复已加载场景中完全重复的材质引用和可安全处理的材质槽问题。", "로드된 씬에서 완전히 동일한 중복 머티리얼 참조와 안전하게 처리할 수 있는 머티리얼 슬롯 문제를 자동 수정합니다." } },
            { "materials_avatar", new[] { "Automatically fix exact duplicate material references and safe material-slot issues under this character hierarchy.", "このキャラクター階層内で完全一致する重複マテリアル参照と安全に修正できるスロット問題を自動修正します。", "自动修复此角色层级下完全重复的材质引用和可安全处理的材质槽问题。", "이 캐릭터 계층 아래에서 완전히 동일한 중복 머티리얼 참조와 안전하게 처리할 수 있는 슬롯 문제를 자동 수정합니다." } },
            { "duplicate_materials", new[] { "FIX DUPLICATE MATERIAL REFERENCES", "重複マテリアル参照を修正", "修复重复材质引用", "중복 머티리얼 참조 수정" } },
            { "unused_material_slots", new[] { "CLEAN UNUSED MATERIAL SLOTS", "未使用マテリアルスロットを整理", "清理未使用材质槽", "미사용 머티리얼 슬롯 정리" } },
            { "expensive_materials", new[] { "FIX SAFE MATERIAL COST ISSUES", "安全に修正できるマテリアル負荷を修正", "修复可安全处理的材质开销问题", "안전하게 처리 가능한 머티리얼 비용 문제 수정" } },
            { "lights", new[] { "REALTIME LIGHT SHADOWS", "リアルタイムライトの影", "实时灯光阴影", "실시간 라이트 그림자" } },
            { "lights_project", new[] { "Quickly disable realtime shadows in loaded scenes.", "読み込み済みシーンのリアルタイム影をすばやく無効化します。", "快速关闭已加载场景中的实时阴影。", "로드된 씬의 실시간 그림자를 빠르게 비활성화합니다." } },
            { "lights_avatar", new[] { "Quickly disable realtime shadows under this character hierarchy.", "このキャラクター階層内のリアルタイム影をすばやく無効化します。", "快速关闭此角色层级下的实时阴影。", "이 캐릭터 계층 아래의 실시간 그림자를 빠르게 비활성화합니다." } },
            { "disable_shadows", new[] { "DISABLE REALTIME SHADOWS", "リアルタイム影を無効化", "关闭实时阴影", "실시간 그림자 비활성화" } },
            { "insights", new[] { "PROJECT INSIGHTS", "プロジェクト分析", "项目分析", "프로젝트 인사이트" } },
            { "insights_desc", new[] { "Review memory-heavy assets and apply safe importer fixes where available.", "メモリ負荷の高いアセットを確認し、安全なインポーター修正が可能な場合は適用します。", "检查内存开销较大的资源，并在安全可行时应用导入修复。", "메모리 비용이 큰 에셋을 검토하고 안전한 경우 임포터 수정 사항을 적용합니다." } },
            { "largest_textures", new[] { "SHOW LARGEST TEXTURES", "最大テクスチャを表示", "显示最大纹理", "가장 큰 텍스처 표시" } },
            { "readwrite_review", new[] { "REVIEW READ/WRITE MEMORY", "Read/Write メモリを確認", "检查读写内存", "Read/Write 메모리 검토" } },
            { "heavy_meshes", new[] { "SHOW HEAVY MESHES", "重いメッシュを表示", "显示高开销网格", "무거운 메시 표시" } },
            { "oversized_meshes", new[] { "FIX OVERSIZED MESH IMPORTS", "大きすぎるメッシュのインポートを修正", "修复过大网格导入设置", "과도하게 큰 메시 임포트 수정" } },
            { "scan", new[] { "PROJECT CHECK", "プロジェクトチェック", "项目检查", "프로젝트 검사" } },
            { "scan_desc", new[] { "Run the heavier diagnostic pass when you want a full list of findings and direct links.", "完全な検出結果と直接リンクが必要なときに、詳細診断を実行します。", "需要完整问题列表和直接链接时运行更深入的诊断。", "전체 발견 목록과 바로가기가 필요할 때 더 무거운 진단을 실행합니다." } },
            { "scan_button", new[] { "SCAN ENTIRE PROJECT", "プロジェクト全体をスキャン", "扫描整个项目", "전체 프로젝트 스캔" } },
            { "avatar_root", new[] { "CHARACTER / AVATAR ROOT", "キャラクター / アバターのルート", "角色 / 虚拟形象根节点", "캐릭터 / 아바타 루트" } },
            { "avatar_root_desc", new[] { "Select the root object you want these one-click jobs to target.", "ワンクリック処理の対象となるルートオブジェクトを選択します。", "选择这些一键操作要处理的根对象。", "원클릭 작업이 대상으로 삼을 루트 오브젝트를 선택하세요." } },
            { "avatar_help", new[] { "Select a character or avatar root in a loaded scene.", "読み込み済みシーン内のキャラクターまたはアバターのルートを選択してください。", "请选择已加载场景中的角色或虚拟形象根节点。", "로드된 씬에서 캐릭터 또는 아바타 루트를 선택하세요." } },
            { "last_result", new[] { "LAST RESULT", "最後の結果", "上次结果", "마지막 결과" } },
            { "last_result_desc", new[] { "A short summary of the most recent action.", "直前の操作の簡単な概要です。", "最近一次操作的简短摘要。", "가장 최근 작업의 간단한 요약입니다." } },
            { "support", new[] { "FREE FOR DEVELOPERS", "開発者向け無料ツール", "面向开发者免费", "개발자 무료 도구" } },
            { "support_desc", new[] { "Optimize Your Project is free to use and is built to remove repetitive optimization work.", "Optimize Your Project は無料で利用でき、反復的な最適化作業を減らすために作られています。", "Optimize Your Project 可免费使用，旨在减少重复的优化工作。", "Optimize Your Project는 무료로 사용할 수 있으며 반복적인 최적화 작업을 줄이기 위해 만들어졌습니다." } },
            { "support_body", new[] { "Optional Patreon support funds testing, documentation, new one-click tools and future integrations. The project stays free either way.", "任意の Patreon 支援は、テスト、ドキュメント、新しいワンクリックツール、将来の統合開発に使われます。支援の有無にかかわらず無料です。", "可选的 Patreon 支持将用于测试、文档、新的一键工具和未来集成。无论是否支持，本项目都会保持免费。", "선택적인 Patreon 후원은 테스트, 문서, 새로운 원클릭 도구와 향후 통합 개발에 사용됩니다. 후원 여부와 관계없이 무료로 유지됩니다." } },
            { "support_button", new[] { "SUPPORT DEVELOPMENT ON PATREON", "PATREON で開発を支援", "在 PATREON 支持开发", "PATREON에서 개발 후원" } },
            { "version", new[] { "VERSION", "バージョン", "版本", "버전" } },
            { "version_desc", new[] { "Keep the tool current without leaving this window.", "このウィンドウから離れずに最新版を確認できます。", "无需离开此窗口即可保持工具最新。", "이 창을 벗어나지 않고 도구를 최신 상태로 유지하세요." } },
            { "up_to_date", new[] { "Up to date", "最新です", "已是最新", "최신 상태" } },
            { "update_available", new[] { "Update available", "更新があります", "有可用更新", "업데이트 가능" } },
            { "update_recommended", new[] { "Update recommended", "更新を推奨", "建议更新", "업데이트 권장" } },
            { "update_unknown", new[] { "Update status unknown", "更新状態は不明", "更新状态未知", "업데이트 상태 알 수 없음" } },
            { "checking", new[] { "Checking...", "確認中...", "检查中...", "확인 중..." } },
            { "check_update", new[] { "CHECK UPDATE", "更新を確認", "检查更新", "업데이트 확인" } },
            { "scan_results", new[] { "PROJECT SCAN RESULTS", "プロジェクトスキャン結果", "项目扫描结果", "프로젝트 스캔 결과" } },
            { "select", new[] { "SELECT", "選択", "选择", "선택" } },
            { "no_findings", new[] { "No findings in this filter.", "このフィルターには結果がありません。", "此筛选器中没有发现。", "이 필터에는 발견 항목이 없습니다." } },
            { "all", new[] { "ALL", "すべて", "全部", "전체" } },
            { "critical", new[] { "CRITICAL", "重大", "严重", "치명적" } },
            { "warning", new[] { "WARNING", "警告", "警告", "경고" } },
            { "choose_job", new[] { "Choose a job and press its button.", "処理を選んでボタンを押してください。", "选择一项操作并按下按钮。", "작업을 선택하고 버튼을 누르세요." } },
            { "compression", new[] { "Compression", "圧縮", "压缩", "압축" } },
            { "pc", new[] { "PC / Standalone", "PC / スタンドアロン", "PC / 独立平台", "PC / 스탠드얼론" } },
            { "android", new[] { "Android / Mobile", "Android / モバイル", "Android / 移动端", "Android / 모바일" } },
            { "ios", new[] { "iOS", "iOS", "iOS", "iOS" } },
            { "cap_particles", new[] { "Cap particle count", "パーティクル数を制限", "限制粒子数量", "파티클 수 제한" } },
            { "max_particles", new[] { "Maximum particles", "最大パーティクル数", "最大粒子数", "최대 파티클 수" } },
            { "more_particles", new[] { "More particle controls", "追加のパーティクル設定", "更多粒子控制", "추가 파티클 제어" } },
            { "cap_lifetime", new[] { "Cap constant lifetime", "一定ライフタイムを制限", "限制固定生命周期", "고정 수명 제한" } },
            { "max_lifetime", new[] { "Maximum lifetime", "最大ライフタイム", "最大生命周期", "최대 수명" } },
            { "disable_trails", new[] { "Disable trails", "トレイルを無効化", "关闭拖尾", "트레일 비활성화" } },
            { "disable_collision", new[] { "Disable collision", "コリジョンを無効化", "关闭碰撞", "충돌 비활성화" } },
            { "disable_noise", new[] { "Disable noise", "ノイズを無効化", "关闭噪声", "노이즈 비활성화" } },
            { "disable_particle_lights", new[] { "Disable particle lights", "パーティクルライトを無効化", "关闭粒子灯光", "파티클 라이트 비활성화" } },
            { "disable_particle_shadows", new[] { "Disable shadows", "影を無効化", "关闭阴影", "그림자 비활성화" } },
            { "disable_subemitters", new[] { "Disable sub emitters", "サブエミッターを無効化", "关闭子发射器", "서브 이미터 비활성화" } }
        };

        internal static VRLanguage Current
        {
            get
            {
                int value = EditorPrefs.GetInt(PreferenceKey, 0);
                return Enum.IsDefined(typeof(VRLanguage), value) ? (VRLanguage)value : VRLanguage.English;
            }
            set { EditorPrefs.SetInt(PreferenceKey, (int)value); }
        }

        internal static string[] LanguageNames => new[]
        {
            Strings["english"][(int)Current],
            Strings["japanese"][(int)Current],
            Strings["chinese"][(int)Current],
            Strings["korean"][(int)Current]
        };

        internal static string T(string key)
        {
            if (!Strings.TryGetValue(key, out var values) || values == null || values.Length < 4)
                return key;
            int index = (int)Current;
            string value = values[index];
            return string.IsNullOrEmpty(value) ? values[0] : value;
        }
    }
}
