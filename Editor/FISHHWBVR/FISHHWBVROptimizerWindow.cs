using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using static FISHHWB.VROptimizer.VRLocalization;

namespace FISHHWB.VROptimizer
{
    internal sealed class FISHHWBVROptimizerWindow : EditorWindow
    {
        enum Page { Project, Avatar }
        enum Filter { All, Critical, Warning }

        static readonly int[] Sizes = { 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384 };
        static readonly string[] SizeNames = { "32", "64", "128", "256", "512", "1024", "2048", "4096", "8192", "16384", "Custom..." };

        VRSettings settings;
        Page page;
        Filter filter;
        GameObject avatar;
        string projectFolder = "Assets";
        string actionSearch = "";
        Texture2D icon;
        Vector2 scroll;
        List<VRIssue> issues;
        ModelImporterMeshCompression meshLevel = ModelImporterMeshCompression.Medium;
        string summary;
        bool showParticleControls;

        GUIStyle cardStyle;
        GUIStyle cardTitleStyle;
        GUIStyle sectionTitleStyle;
        GUIStyle sectionDetailStyle;
        GUIStyle primaryButtonStyle;
        GUIStyle compactButtonStyle;

        [MenuItem("FISHHWB/Optimize Your Project")]
        static void Open()
        {
            var window = GetWindow<FISHHWBVROptimizerWindow>();
            window.minSize = new Vector2(420, 600);
            window.titleContent = new GUIContent("Optimize Your Project", window.icon);
        }

        void OnEnable()
        {
            settings = VRSettings.Load();
            icon = AssetDatabase.LoadAssetAtPath<Texture2D>(
                "Packages/com.fishhwb.vr-optimizer/Editor/FISHHWBVR/Icons/Optimize-Your-Project.png");
            titleContent = new GUIContent("Optimize Your Project", icon);
            summary = T("choose_job");
            VRUpdateChecker.CheckIfDue();
        }

        void OnGUI()
        {
            if (settings == null) settings = VRSettings.Load();
            EnsureStyles();

            scroll = EditorGUILayout.BeginScrollView(scroll);
            Header();
            GUILayout.Space(8);
            DrawLanguageAndSearch();
            GUILayout.Space(10);

            EditorGUILayout.BeginHorizontal();
            GUILayout.Space(8);
            var next = (Page)GUILayout.Toolbar(
                (int)page,
                new[] { T("project"), T("avatar") },
                GUILayout.Height(38),
                GUILayout.ExpandWidth(true));
            GUILayout.Space(8);
            EditorGUILayout.EndHorizontal();

            if (next != page)
            {
                page = next;
                issues = null;
                summary = T("choose_job");
            }

            GUILayout.Space(12);

            EditorGUILayout.BeginHorizontal();
            GUILayout.Space(10);
            EditorGUILayout.BeginVertical();

            if (page == Page.Project) DrawProject();
            else DrawAvatar();

            DrawResultCard();
            DrawSupportPanel();
            DrawUpdateFooter();
            DrawLinksFooter();

            EditorGUILayout.EndVertical();
            GUILayout.Space(10);
            EditorGUILayout.EndHorizontal();

            GUILayout.Space(8);
            EditorGUILayout.EndScrollView();
        }

        void EnsureStyles()
        {
            if (cardStyle != null) return;

            cardStyle = new GUIStyle(EditorStyles.helpBox)
            {
                padding = new RectOffset(12, 12, 10, 12),
                margin = new RectOffset(0, 0, 0, 8)
            };

            cardTitleStyle = new GUIStyle(EditorStyles.boldLabel)
            {
                fontSize = 12,
                wordWrap = true
            };

            sectionTitleStyle = new GUIStyle(EditorStyles.boldLabel)
            {
                fontSize = 16,
                wordWrap = true
            };

            sectionDetailStyle = new GUIStyle(EditorStyles.wordWrappedMiniLabel)
            {
                fontSize = 10
            };

            primaryButtonStyle = new GUIStyle(GUI.skin.button)
            {
                fontStyle = FontStyle.Bold,
                fixedHeight = 38,
                margin = new RectOffset(0, 0, 8, 0)
            };

            compactButtonStyle = new GUIStyle(GUI.skin.button)
            {
                fontStyle = FontStyle.Bold,
                fixedHeight = 26
            };
        }

        void BeginCard(string title, string description)
        {
            EditorGUILayout.BeginVertical(cardStyle);
            EditorGUILayout.LabelField(title, cardTitleStyle);
            if (!string.IsNullOrEmpty(description))
                EditorGUILayout.LabelField(description, sectionDetailStyle);
            GUILayout.Space(4);
            DrawSeparator();
        }

        static void EndCard()
        {
            EditorGUILayout.EndVertical();
        }

        static void DrawSeparator()
        {
            var rect = GUILayoutUtility.GetRect(1, 1, GUILayout.ExpandWidth(true));
            EditorGUI.DrawRect(
                rect,
                EditorGUIUtility.isProSkin
                    ? new Color(.18f, .42f, .43f, .65f)
                    : new Color(.20f, .52f, .50f, .55f));
            GUILayout.Space(5);
        }

        bool ActionButton(string label)
        {
            var previous = GUI.backgroundColor;
            GUI.backgroundColor = EditorGUIUtility.isProSkin
                ? new Color(.40f, .82f, .76f)
                : new Color(.46f, .78f, .72f);
            bool pressed = GUILayout.Button(label, primaryButtonStyle);
            GUI.backgroundColor = previous;
            return pressed;
        }

        void DrawSectionIntro(string title, string description)
        {
            EditorGUILayout.LabelField(title, sectionTitleStyle);
            EditorGUILayout.LabelField(description, sectionDetailStyle);
            GUILayout.Space(6);
        }

        void Header()
        {
            var rect = GUILayoutUtility.GetRect(1, 84, GUILayout.ExpandWidth(true));
            var background = EditorGUIUtility.isProSkin
                ? new Color(.055f, .095f, .11f)
                : new Color(.84f, .93f, .91f);
            var accent = EditorGUIUtility.isProSkin
                ? new Color(.23f, .72f, .67f)
                : new Color(.12f, .55f, .50f);

            EditorGUI.DrawRect(rect, background);
            EditorGUI.DrawRect(new Rect(rect.x, rect.yMax - 3, rect.width, 3), accent);

            if (icon)
                GUI.DrawTexture(new Rect(rect.x + 15, rect.y + 13, 56, 56), icon, ScaleMode.ScaleToFit, true);

            var title = new GUIStyle(EditorStyles.boldLabel) { fontSize = 17 };
            var detail = new GUIStyle(EditorStyles.miniLabel) { fontSize = 10 };

            if (EditorGUIUtility.isProSkin)
            {
                title.normal.textColor = Color.white;
                detail.normal.textColor = new Color(.69f, .86f, .83f);
            }

            GUI.Label(new Rect(rect.x + 82, rect.y + 14, rect.width - 94, 25), "OPTIMIZE YOUR PROJECT", title);
            GUI.Label(
                new Rect(rect.x + 82, rect.y + 42, rect.width - 94, 18),
                "v" + VRUpdateChecker.CurrentVersion + "  •  EN / 日本語 / 简体中文 / 한국어",
                detail);
        }

        void DrawProject()
        {
            DrawSectionIntro(T("project"), T("project_intro"));

            BeginCard(T("asset_scope"), T("asset_scope_desc"));
            string chosen = EditorGUILayout.TextField(T("assets_folder"), projectFolder);
            if (chosen != projectFolder) projectFolder = chosen;

            if (GUILayout.Button(T("use_selection")))
                projectFolder = VRProjectInsights.FolderFromSelection(projectFolder);

            bool valid = projectFolder == "Assets" ||
                         projectFolder.StartsWith("Assets/", StringComparison.Ordinal) &&
                         AssetDatabase.IsValidFolder(projectFolder);

            if (!valid)
                EditorGUILayout.HelpBox(T("invalid_folder"), MessageType.Warning);
            EndCard();

            if (MatchesAction("texture memory"))
            {
                using (new EditorGUI.DisabledScope(!valid))
                    TextureCard(null, T("textures"), T("textures_desc_project"), projectFolder);
            }

            if (MatchesAction("particle effects"))
                ParticleCard(null);

            if (MatchesAction("mesh model compression"))
                MeshCard(null);

            if (MatchesAction("light shadow"))
                LightCard(null);

            if (MatchesAction("memory texture mesh heavy review"))
            {
                using (new EditorGUI.DisabledScope(!valid))
                    InsightsCard(null, projectFolder);
            }

            if (MatchesAction("scan diagnostic project check"))
            {
                BeginCard(T("scan"), T("scan_desc"));
                if (ActionButton(T("scan_button")))
                {
                    issues = VRProjectScanner.Scan(settings, null, out bool cancelled);
                    summary = (cancelled ? "Partial scan: " : "Project scan complete: ") + issues.Count + " findings.";
                }
                EndCard();
            }

            DrawIssues();
        }

        void DrawAvatar()
        {
            DrawSectionIntro(T("avatar"), T("avatar_intro"));

            BeginCard(T("avatar_root"), T("avatar_root_desc"));
            avatar = (GameObject)EditorGUILayout.ObjectField(avatar, typeof(GameObject), true);

            if (GUILayout.Button(T("use_selection")))
                avatar = Selection.activeGameObject;

            bool valid = VRAvatarWorkflow.EditableRoot(avatar);
            if (!valid)
                EditorGUILayout.HelpBox(T("avatar_help"), MessageType.Info);
            EndCard();

            using (new EditorGUI.DisabledScope(!valid))
            {
                if (MatchesAction("texture memory"))
                    TextureCard(avatar, T("textures"), T("textures_desc_avatar"));
                if (MatchesAction("particle effects"))
                    ParticleCard(avatar);
                if (MatchesAction("mesh model compression"))
                    MeshCard(avatar);
                if (MatchesAction("light shadow"))
                    LightCard(avatar);
                if (MatchesAction("mesh heavy review"))
                    InsightsCard(avatar, "Assets");
            }
        }

        void TextureCard(GameObject root, string title, string scope, string folder = "Assets")
        {
            BeginCard(title, scope);

            EditorGUI.BeginChangeCheck();
            settings.pc = SizeField(T("pc"), settings.pc);
            settings.android = SizeField(T("android"), settings.android);
            settings.ios = SizeField(T("ios"), settings.ios);

            if (EditorGUI.EndChangeCheck())
            {
                settings.Sanitize();
                settings.Save();
            }

            if (ActionButton(T("compress_textures")))
                OptimizeTextures(root, folder);

            EndCard();
        }

        static int SizeField(string label, int value)
        {
            int index = Array.IndexOf(Sizes, value);
            int selected = EditorGUILayout.Popup(label, index < 0 ? Sizes.Length : index, SizeNames);

            if (selected < Sizes.Length)
                return Sizes[selected];

            int typed = EditorGUILayout.IntField("Custom " + label, value);
            return Mathf.Clamp(Mathf.ClosestPowerOfTwo(Mathf.Max(32, typed)), 32, 16384);
        }

        void OptimizeTextures(GameObject root, string folder)
        {
            settings.Sanitize();

            var textures = VRAvatarWorkflow.CollectTextures(root, settings, folder, out int unsupported);

            var compression = VRTextureCompression.Collect(root, folder, out bool scanCancelled);
            if (scanCancelled)
            {
                summary = new VRActionSummary { Cancelled = true, Skipped = textures.Count, Unsupported = unsupported }.Format("Textures") + "\nNo changes applied.";
                return;
            }

            var byPath = new Dictionary<string, List<VRCompressionChange>>(StringComparer.Ordinal);
            foreach (var item in compression)
            {
                if (!byPath.TryGetValue(item.Path, out var list))
                {
                    list = new List<VRCompressionChange>();
                    byPath.Add(item.Path, list);
                }
                list.Add(item);
            }

            if (textures.Count == 0)
            {
                summary = new VRActionSummary { Unsupported = unsupported }.Format("Textures") + "\nNo supported textures found in this scope.";
                return;
            }

            if (!EditorUtility.DisplayDialog(
                "Optimize textures",
                "Optimize " + textures.Count + " supported textures? Existing explicit formats and stricter size caps are preserved.",
                "Optimize",
                "Cancel"))
            {
                summary = new VRActionSummary { Cancelled = true, Skipped = textures.Count, Unsupported = unsupported }.Format("Textures");
                return;
            }

            var result = VRActionSummary.Run("Textures", textures, item => item.Path, item =>
            {
                var importer = AssetImporter.GetAtPath(item.Path) as TextureImporter;
                if (!importer || importer.textureShape != TextureImporterShape.Texture2D ||
                    (importer.textureType != TextureImporterType.Default && importer.textureType != TextureImporterType.NormalMap))
                    return VRActionOutcome.Unsupported;
                byPath.TryGetValue(item.Path, out var entries);
                return VRTextureOptimizer.OptimizeWithCompression(item.Path, settings, entries)
                    ? VRActionOutcome.Changed : VRActionOutcome.Unchanged;
            }, unsupported);
            summary = result.Format("Textures");
        }

        void ParticleCard(GameObject root)
        {
            BeginCard(
                T("particles"),
                root ? T("particles_avatar") : T("particles_project"));

            EditorGUI.BeginChangeCheck();
            settings.capParticles = EditorGUILayout.Toggle(T("cap_particles"), settings.capParticles);

            if (settings.capParticles)
                settings.maxParticles = EditorGUILayout.IntField(T("max_particles"), settings.maxParticles);

            showParticleControls = EditorGUILayout.Foldout(showParticleControls, T("more_particles"), true);
            if (showParticleControls)
            {
                settings.capLifetime = EditorGUILayout.Toggle(T("cap_lifetime"), settings.capLifetime);
                if (settings.capLifetime)
                    settings.maxLifetime = EditorGUILayout.FloatField(T("max_lifetime"), settings.maxLifetime);

                settings.disableTrails = EditorGUILayout.Toggle(T("disable_trails"), settings.disableTrails);
                settings.disableCollision = EditorGUILayout.Toggle(T("disable_collision"), settings.disableCollision);
                settings.disableNoise = EditorGUILayout.Toggle(T("disable_noise"), settings.disableNoise);
                settings.disableLights = EditorGUILayout.Toggle(T("disable_particle_lights"), settings.disableLights);
                settings.disableShadows = EditorGUILayout.Toggle(T("disable_particle_shadows"), settings.disableShadows);
                settings.disableSubEmitters = EditorGUILayout.Toggle(T("disable_subemitters"), settings.disableSubEmitters);
            }

            if (EditorGUI.EndChangeCheck())
            {
                settings.Sanitize();
                settings.Save();
            }

            if (ActionButton(T("optimize_particles")))
                OptimizeParticles(root);

            EndCard();
        }

        void OptimizeParticles(GameObject root)
        {
            var particles = new List<ParticleSystem>(
                root
                    ? (IEnumerable<ParticleSystem>)root.GetComponentsInChildren<ParticleSystem>(true)
                    : VRProjectScanner.SceneObjects<ParticleSystem>());

            Undo.IncrementCurrentGroup();
            int group = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName("Optimize Particles");
            try
            {
                var result = VRActionSummary.Run("Particles", particles,
                    item => item ? item.name : "Missing particle system", item =>
                    {
                        if (!item) return VRActionOutcome.Skipped;
                        return VRParticleOptimizer.Optimize(item, settings)
                            ? VRActionOutcome.Changed : VRActionOutcome.Unchanged;
                    });
                summary = result.Format("Particles") + "\nUse Undo if needed.";
            }
            finally { Undo.CollapseUndoOperations(group); }
        }

        void MeshCard(GameObject root)
        {
            BeginCard(
                T("mesh_imports"),
                root ? T("mesh_avatar") : T("mesh_project"));

            meshLevel = (ModelImporterMeshCompression)EditorGUILayout.EnumPopup(T("compression"), meshLevel);

            if (ActionButton(T("compress_meshes")))
            {
                var meshes = VRMeshCompression.Collect(root, out int unsupported);
                int pending = 0;
                foreach (var mesh in meshes)
                    if (mesh.Current != meshLevel) pending++;

                if (pending == 0)
                    summary = new VRActionSummary { Unchanged = meshes.Count, Unsupported = unsupported }.Format("Imported meshes");
                else if (!EditorUtility.DisplayDialog("Compress meshes",
                    "Reimport " + pending + " model assets using " + meshLevel + " compression?", "Compress", "Cancel"))
                    summary = new VRActionSummary { Cancelled = true, Skipped = meshes.Count, Unsupported = unsupported }.Format("Imported meshes");
                else
                {
                    var result = VRActionSummary.Run("Imported meshes", meshes, item => item.Path, item =>
                    {
                        var importer = AssetImporter.GetAtPath(item.Path) as ModelImporter;
                        if (!importer) return VRActionOutcome.Unsupported;
                        if (importer.meshCompression == meshLevel) return VRActionOutcome.Unchanged;
                        importer.meshCompression = meshLevel;
                        importer.SaveAndReimport();
                        return VRActionOutcome.Changed;
                    }, unsupported);
                    summary = result.Format("Imported meshes");
                }
            }

            EndCard();
        }

        void LightCard(GameObject root)
        {
            BeginCard(
                T("lights"),
                root ? T("lights_avatar") : T("lights_project"));

            if (ActionButton(T("disable_shadows")))
            {
                var lights = new List<Light>(root
                    ? (IEnumerable<Light>)root.GetComponentsInChildren<Light>(true)
                    : VRProjectScanner.SceneObjects<Light>());
                int pending = 0;
                foreach (var light in lights)
                    if (light && light.enabled && light.lightmapBakeType == LightmapBakeType.Realtime && light.shadows != LightShadows.None)
                        pending++;

                if (pending > 0 && !EditorUtility.DisplayDialog("Disable realtime shadows",
                    "Disable shadows on " + pending + " realtime lights? You can use Unity Undo to revert.", "Disable", "Cancel"))
                    summary = new VRActionSummary { Cancelled = true, Skipped = lights.Count }.Format("Realtime shadows");
                else
                {
                    Undo.IncrementCurrentGroup();
                    int group = Undo.GetCurrentGroup();
                    Undo.SetCurrentGroupName("Disable Realtime Shadows");
                    try
                    {
                        var result = VRActionSummary.Run("Realtime shadows", lights,
                            item => item ? item.name : "Missing light", item =>
                            {
                                if (!item || !item.enabled) return VRActionOutcome.Skipped;
                                if (item.lightmapBakeType != LightmapBakeType.Realtime) return VRActionOutcome.Unsupported;
                                return VRLightOptimizer.Optimize(item, settings)
                                    ? VRActionOutcome.Changed : VRActionOutcome.Unchanged;
                            });
                        summary = result.Format("Realtime shadows") + "\nUse Undo if needed.";
                    }
                    finally { Undo.CollapseUndoOperations(group); }
                }
            }

            EndCard();
        }

        void InsightsCard(GameObject root, string folder)
        {
            BeginCard(T("insights"), T("insights_desc"));

            if (!root && GUILayout.Button(T("largest_textures"), compactButtonStyle))
            {
                issues = VRProjectInsights.LargestTextures(folder);
                summary = "Largest texture review: " + issues.Count + " candidates.";
            }

            if (!root && GUILayout.Button(T("readwrite_review"), compactButtonStyle))
            {
                issues = VRProjectInsights.ReadWriteReview(folder);
                summary = "Read/Write review: " + issues.Count + " candidates.";
            }

            if (GUILayout.Button(T("heavy_meshes"), compactButtonStyle))
            {
                issues = VRProjectInsights.HeavyMeshes(root);
                summary = "Heavy mesh review: " + issues.Count + " candidates.";
            }

            EndCard();
        }

        void DrawLanguageAndSearch()
        {
            EditorGUILayout.BeginHorizontal();
            GUILayout.Space(10);
            EditorGUILayout.BeginVertical(cardStyle);

            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField(T("language"), GUILayout.Width(78));
            int current = (int)VRLocalization.Current;
            int next = EditorGUILayout.Popup(current, VRLocalization.LanguageNames);
            if (next != current)
            {
                VRLocalization.Current = (VRLanguage)next;
                summary = T("choose_job");
                Repaint();
            }
            EditorGUILayout.EndHorizontal();

            actionSearch = EditorGUILayout.TextField(T("search"), actionSearch);
            if (string.IsNullOrWhiteSpace(actionSearch))
                EditorGUILayout.LabelField(T("search_hint"), sectionDetailStyle);

            EditorGUILayout.EndVertical();
            GUILayout.Space(10);
            EditorGUILayout.EndHorizontal();
        }

        bool MatchesAction(string keywords)
        {
            if (string.IsNullOrWhiteSpace(actionSearch)) return true;
            return keywords.IndexOf(actionSearch.Trim(), StringComparison.OrdinalIgnoreCase) >= 0;
        }

        void DrawIssues()
        {
            if (issues == null) return;

            GUILayout.Space(6);
            EditorGUILayout.LabelField(T("scan_results") + "  •  " + issues.Count, EditorStyles.boldLabel);
            filter = (Filter)GUILayout.Toolbar((int)filter, new[] { T("all"), T("critical"), T("warning") });

            int count = 0;
            foreach (var issue in issues)
            {
                if (filter == Filter.Critical && issue.Severity != VRSeverity.Critical ||
                    filter == Filter.Warning && issue.Severity != VRSeverity.Warning)
                    continue;

                count++;
                EditorGUILayout.BeginVertical(cardStyle);
                EditorGUILayout.BeginHorizontal();
                var severityDot = new GUIStyle(EditorStyles.boldLabel) { fontSize = 13 };
                severityDot.normal.textColor = issue.Severity == VRSeverity.Critical
                    ? new Color(.92f, .24f, .22f)
                    : new Color(1f, .58f, .12f);
                GUILayout.Label("●", severityDot, GUILayout.Width(17));
                EditorGUILayout.LabelField(issue.Message, EditorStyles.wordWrappedLabel);
                EditorGUILayout.EndHorizontal();

                if (!string.IsNullOrEmpty(issue.AssetPath))
                    EditorGUILayout.LabelField(issue.AssetPath, EditorStyles.miniLabel);

                using (new EditorGUI.DisabledScope(!issue.Target))
                {
                    if (GUILayout.Button(T("select"), GUILayout.Width(100)))
                    {
                        Selection.activeObject = issue.Target;
                        EditorGUIUtility.PingObject(issue.Target);
                    }
                }

                EditorGUILayout.EndVertical();
            }

            if (count == 0)
                EditorGUILayout.LabelField(T("no_findings"), EditorStyles.miniLabel);
        }

        void DrawResultCard()
        {
            BeginCard(T("last_result"), T("last_result_desc"));
            EditorGUILayout.LabelField(summary ?? T("choose_job"), EditorStyles.wordWrappedLabel);
            EndCard();
        }

        void DrawSupportPanel()
        {
            BeginCard(T("support"), T("support_desc"));

            EditorGUILayout.LabelField(T("support_body"), EditorStyles.wordWrappedMiniLabel);

            var previous = GUI.backgroundColor;
            GUI.backgroundColor = EditorGUIUtility.isProSkin
                ? new Color(.74f, .48f, .82f)
                : new Color(.72f, .50f, .78f);

            if (GUILayout.Button(T("support_button"), primaryButtonStyle))
                Application.OpenURL("https://www.patreon.com/cw/DedZed");

            GUI.backgroundColor = previous;
            EndCard();
        }

        void DrawUpdateFooter()
        {
            BeginCard(T("version"), T("version_desc"));
            EditorGUILayout.BeginHorizontal();

            var health = VRUpdateChecker.Health;
            var dot = new GUIStyle(EditorStyles.boldLabel) { fontSize = 16 };
            dot.normal.textColor = StatusColor(health);

            GUILayout.Label("●", dot, GUILayout.Width(18));
            GUILayout.Label("v" + VRUpdateChecker.CurrentVersion, EditorStyles.boldLabel, GUILayout.Width(72));

            string stateText;
            switch (health)
            {
                case VRUpdateHealth.Current:
                    stateText = T("up_to_date");
                    break;
                case VRUpdateHealth.UpdateAvailable:
                    stateText = T("update_available");
                    break;
                case VRUpdateHealth.FarBehind:
                    stateText = T("update_recommended");
                    break;
                default:
                    stateText = VRUpdateChecker.Checking ? T("checking") : T("update_unknown");
                    break;
            }

            GUILayout.Label(stateText, EditorStyles.miniLabel);
            GUILayout.FlexibleSpace();

            using (new EditorGUI.DisabledScope(VRUpdateChecker.Checking || VRUpdateChecker.Installing))
            {
                if (VRUpdateChecker.HasUpdate)
                {
                    string label = VRUpdateChecker.CanUpdateDirectly
                        ? "UPDATE TO " + VRUpdateChecker.LatestTag
                        : "UPDATE INFO";

                    if (GUILayout.Button(label, GUILayout.MinWidth(112)))
                        VRUpdateChecker.Update();
                }
                else
                {
                    if (GUILayout.Button(VRUpdateChecker.Checking ? T("checking").ToUpperInvariant() : T("check_update"), GUILayout.MinWidth(100)))
                        VRUpdateChecker.Check(true);
                }
            }

            EditorGUILayout.EndHorizontal();

            if (!string.IsNullOrEmpty(VRUpdateChecker.Message) &&
                (health == VRUpdateHealth.Unknown || VRUpdateChecker.Installing))
                EditorGUILayout.LabelField(VRUpdateChecker.Message, EditorStyles.wordWrappedMiniLabel);

            EndCard();
        }

        static Color StatusColor(VRUpdateHealth health)
        {
            switch (health)
            {
                case VRUpdateHealth.Current:
                    return new Color(.25f, .82f, .38f);
                case VRUpdateHealth.UpdateAvailable:
                    return new Color(1f, .58f, .12f);
                case VRUpdateHealth.FarBehind:
                    return new Color(.92f, .24f, .22f);
                default:
                    return new Color(.55f, .55f, .55f);
            }
        }

        void DrawLinksFooter()
        {
            GUILayout.Space(2);
            EditorGUILayout.LabelField("FISHHWB | DED ZED  •  BUILT TO HELP DEVELOPERS CREATE WITH LESS BUSYWORK", EditorStyles.centeredGreyMiniLabel);
            GUILayout.Space(3);

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("GITHUB", compactButtonStyle))
                Application.OpenURL("https://github.com/dedzedofficial/Optimize-Your-Project");
            if (GUILayout.Button("WEBSITE", compactButtonStyle))
                Application.OpenURL("https://fishhwb.github.io/");
            if (GUILayout.Button("DISCORD", compactButtonStyle))
                Application.OpenURL("https://discord.gg/wZGxxkk4Jg");
            EditorGUILayout.EndHorizontal();
        }
    }
}
