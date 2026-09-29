using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

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
        Texture2D icon;
        Vector2 scroll;
        List<VRIssue> issues;
        ModelImporterMeshCompression meshLevel = ModelImporterMeshCompression.Medium;
        string summary = "Choose a job and press its button.";
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
            VRUpdateChecker.CheckIfDue();
        }

        void OnGUI()
        {
            if (settings == null) settings = VRSettings.Load();
            EnsureStyles();

            scroll = EditorGUILayout.BeginScrollView(scroll);
            Header();
            GUILayout.Space(10);

            EditorGUILayout.BeginHorizontal();
            GUILayout.Space(8);
            var next = (Page)GUILayout.Toolbar(
                (int)page,
                new[] { "PROJECT", "CHARACTER / AVATAR" },
                GUILayout.Height(38),
                GUILayout.ExpandWidth(true));
            GUILayout.Space(8);
            EditorGUILayout.EndHorizontal();

            if (next != page)
            {
                page = next;
                issues = null;
                summary = "Choose a job and press its button.";
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
                "Free developer tools • one-click optimization • v" + VRUpdateChecker.CurrentVersion,
                detail);
        }

        void DrawProject()
        {
            DrawSectionIntro(
                "PROJECT",
                "Fast, focused optimization for assets and loaded scenes. Pick a job, run it, and keep moving.");

            BeginCard("ASSET SCOPE", "Choose which Assets folder texture jobs should work inside.");
            string chosen = EditorGUILayout.TextField("Assets folder", projectFolder);
            if (chosen != projectFolder) projectFolder = chosen;

            bool valid = projectFolder == "Assets" ||
                         projectFolder.StartsWith("Assets/", StringComparison.Ordinal) &&
                         AssetDatabase.IsValidFolder(projectFolder);

            if (!valid)
                EditorGUILayout.HelpBox("Enter an existing folder under Assets.", MessageType.Warning);
            EndCard();

            using (new EditorGUI.DisabledScope(!valid))
                TextureCard(null, "TEXTURES", "Resize and compress supported textures in the selected Assets folder.", projectFolder);

            ParticleCard(null);
            MeshCard(null);
            LightCard(null);

            BeginCard(
                "PROJECT CHECK",
                "Need more detail? Run a full scan only when you want a list of findings and direct links to problem assets.");

            if (ActionButton("SCAN ENTIRE PROJECT"))
            {
                issues = VRProjectScanner.Scan(settings, null, out bool cancelled);
                summary = (cancelled ? "Partial scan: " : "Project scan complete: ") + issues.Count + " findings.";
            }

            EndCard();
            DrawIssues();
        }

        void DrawAvatar()
        {
            DrawSectionIntro(
                "CHARACTER / AVATAR",
                "Optimize one character hierarchy without changing the rest of your loaded scene.");

            BeginCard("CHARACTER / AVATAR ROOT", "Select the root object you want these one-click jobs to target.");
            avatar = (GameObject)EditorGUILayout.ObjectField(avatar, typeof(GameObject), true);

            if (GUILayout.Button("USE CURRENT SELECTION"))
                avatar = Selection.activeGameObject;

            bool valid = VRAvatarWorkflow.EditableRoot(avatar);
            if (!valid)
                EditorGUILayout.HelpBox("Select a character or avatar root in a loaded scene.", MessageType.Info);
            EndCard();

            using (new EditorGUI.DisabledScope(!valid))
            {
                TextureCard(avatar, "TEXTURES", "Resize and compress textures referenced by this character hierarchy.");
                ParticleCard(avatar);
                MeshCard(avatar);
                LightCard(avatar);
            }
        }

        void TextureCard(GameObject root, string title, string scope, string folder = "Assets")
        {
            BeginCard(title, scope);

            EditorGUI.BeginChangeCheck();
            settings.pc = SizeField("PC / Standalone", settings.pc);
            settings.android = SizeField("Android / Mobile", settings.android);
            settings.ios = SizeField("iOS", settings.ios);

            if (EditorGUI.EndChangeCheck())
            {
                settings.Sanitize();
                settings.Save();
            }

            if (ActionButton("COMPRESS & SIZE TEXTURES"))
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

            var textures = VRAvatarWorkflow.CollectTextures(root, settings);
            if (!root && folder != "Assets")
                textures.RemoveAll(item => !item.Path.StartsWith(folder + "/", StringComparison.Ordinal));

            var compression = VRTextureCompression.Collect(root, folder, out bool scanCancelled);
            if (scanCancelled)
            {
                summary = "Texture collection cancelled. No changes applied.";
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
                summary = "No supported textures found in this scope.";
                return;
            }

            if (!EditorUtility.DisplayDialog(
                "Optimize textures",
                "Optimize " + textures.Count + " supported textures? Existing explicit formats and stricter size caps are preserved.",
                "Optimize",
                "Cancel"))
                return;

            int changed = 0;
            int unchanged = 0;
            int failed = 0;
            bool cancelled = false;

            try
            {
                for (int i = 0; i < textures.Count; i++)
                {
                    string path = textures[i].Path;
                    if (EditorUtility.DisplayCancelableProgressBar(
                        "Optimize Textures",
                        path,
                        textures.Count == 0 ? 1 : (float)i / textures.Count))
                    {
                        cancelled = true;
                        break;
                    }

                    try
                    {
                        byPath.TryGetValue(path, out var entries);
                        bool didChange = VRTextureOptimizer.OptimizeWithCompression(path, settings, entries);
                        if (didChange) changed++;
                        else unchanged++;
                    }
                    catch (Exception error)
                    {
                        failed++;
                        Debug.LogError("Optimize Your Project: " + path + " — " + error);
                    }
                }
            }
            finally
            {
                EditorUtility.ClearProgressBar();
            }

            summary = (cancelled ? "Cancelled. Partial results: " : "Done. ") +
                      changed + " textures changed, " + unchanged + " unchanged, " + failed + " failed.";
        }

        void ParticleCard(GameObject root)
        {
            BeginCard(
                "PARTICLES",
                root ? "Apply the selected limits to particle systems under this character hierarchy." : "Apply the selected limits to particle systems in loaded scenes.");

            EditorGUI.BeginChangeCheck();
            settings.capParticles = EditorGUILayout.Toggle("Cap particle count", settings.capParticles);

            if (settings.capParticles)
                settings.maxParticles = EditorGUILayout.IntField("Maximum particles", settings.maxParticles);

            showParticleControls = EditorGUILayout.Foldout(showParticleControls, "More particle controls", true);
            if (showParticleControls)
            {
                settings.capLifetime = EditorGUILayout.Toggle("Cap constant lifetime", settings.capLifetime);
                if (settings.capLifetime)
                    settings.maxLifetime = EditorGUILayout.FloatField("Maximum lifetime", settings.maxLifetime);

                settings.disableTrails = EditorGUILayout.Toggle("Disable trails", settings.disableTrails);
                settings.disableCollision = EditorGUILayout.Toggle("Disable collision", settings.disableCollision);
                settings.disableNoise = EditorGUILayout.Toggle("Disable noise", settings.disableNoise);
                settings.disableLights = EditorGUILayout.Toggle("Disable particle lights", settings.disableLights);
                settings.disableShadows = EditorGUILayout.Toggle("Disable shadows", settings.disableShadows);
                settings.disableSubEmitters = EditorGUILayout.Toggle("Disable sub emitters", settings.disableSubEmitters);
            }

            if (EditorGUI.EndChangeCheck())
            {
                settings.Sanitize();
                settings.Save();
            }

            if (ActionButton("OPTIMIZE PARTICLES"))
                OptimizeParticles(root);

            EndCard();
        }

        void OptimizeParticles(GameObject root)
        {
            var particles = new List<ParticleSystem>(
                root
                    ? (IEnumerable<ParticleSystem>)root.GetComponentsInChildren<ParticleSystem>(true)
                    : VRProjectScanner.SceneObjects<ParticleSystem>());

            if (particles.Count == 0)
            {
                summary = "No particle systems found in this scope.";
                return;
            }

            int changed = 0;
            int group = Undo.GetCurrentGroup();
            bool cancelled = false;
            Undo.SetCurrentGroupName("Optimize Particles");

            try
            {
                for (int i = 0; i < particles.Count; i++)
                {
                    if (EditorUtility.DisplayCancelableProgressBar(
                        "Optimize Particles",
                        particles[i].name,
                        (float)i / particles.Count))
                    {
                        cancelled = true;
                        break;
                    }

                    if (VRParticleOptimizer.Optimize(particles[i], settings))
                        changed++;
                }
            }
            finally
            {
                EditorUtility.ClearProgressBar();
                Undo.CollapseUndoOperations(group);
            }

            summary = (cancelled ? "Cancelled. " : "Done. ") +
                      changed + " of " + particles.Count + " particle systems changed. Use Undo if needed.";
        }

        void MeshCard(GameObject root)
        {
            BeginCard(
                "MESH IMPORTS",
                root ? "Apply Unity mesh compression to imported models referenced by this character hierarchy." : "Apply Unity mesh compression to imported models used by loaded scenes.");

            meshLevel = (ModelImporterMeshCompression)EditorGUILayout.EnumPopup("Compression", meshLevel);

            if (ActionButton("COMPRESS IMPORTED MESHES"))
            {
                var meshes = VRMeshCompression.Collect(root);
                int pending = 0;

                foreach (var mesh in meshes)
                    if (mesh.Current != meshLevel) pending++;

                if (pending == 0)
                {
                    summary = "Imported meshes already match this compression level.";
                }
                else if (EditorUtility.DisplayDialog(
                    "Compress meshes",
                    "Reimport " + pending + " model assets using " + meshLevel + " compression?",
                    "Compress",
                    "Cancel"))
                {
                    int changed = 0;
                    int failed = 0;

                    try
                    {
                        for (int i = 0; i < meshes.Count; i++)
                        {
                            var item = meshes[i];
                            if (item.Current == meshLevel) continue;

                            if (EditorUtility.DisplayCancelableProgressBar(
                                "Compress Meshes",
                                item.Path,
                                meshes.Count == 0 ? 1 : (float)i / meshes.Count))
                                break;

                            try
                            {
                                var importer = AssetImporter.GetAtPath(item.Path) as ModelImporter;
                                if (importer == null) continue;

                                importer.meshCompression = meshLevel;
                                importer.SaveAndReimport();
                                changed++;
                            }
                            catch (Exception error)
                            {
                                failed++;
                                Debug.LogError("Optimize Your Project: " + item.Path + " — " + error);
                            }
                        }
                    }
                    finally
                    {
                        EditorUtility.ClearProgressBar();
                    }

                    summary = changed + " imported meshes changed; " + failed + " failed.";
                }
            }

            EndCard();
        }

        void LightCard(GameObject root)
        {
            BeginCard(
                "REALTIME LIGHT SHADOWS",
                root ? "Quickly disable realtime shadows under this character hierarchy." : "Quickly disable realtime shadows in loaded scenes.");

            if (ActionButton("DISABLE REALTIME SHADOWS"))
            {
                var lights = root
                    ? (IEnumerable<Light>)root.GetComponentsInChildren<Light>(true)
                    : VRProjectScanner.SceneObjects<Light>();

                var pending = new List<Light>();
                foreach (var light in lights)
                {
                    if (light &&
                        light.enabled &&
                        light.lightmapBakeType == LightmapBakeType.Realtime &&
                        light.shadows != LightShadows.None)
                        pending.Add(light);
                }

                if (pending.Count == 0)
                {
                    summary = "No enabled realtime shadows found in this scope.";
                }
                else if (EditorUtility.DisplayDialog(
                    "Disable realtime shadows",
                    "Disable shadows on " + pending.Count + " realtime lights? You can use Unity Undo to revert.",
                    "Disable",
                    "Cancel"))
                {
                    int group = Undo.GetCurrentGroup();
                    Undo.SetCurrentGroupName("Disable Realtime Shadows");

                    foreach (var light in pending)
                        VRLightOptimizer.Optimize(light, settings);

                    Undo.CollapseUndoOperations(group);
                    summary = "Disabled shadows on " + pending.Count + " lights. Use Undo if needed.";
                }
            }

            EndCard();
        }

        void DrawIssues()
        {
            if (issues == null) return;

            GUILayout.Space(6);
            EditorGUILayout.LabelField("PROJECT SCAN RESULTS  •  " + issues.Count, EditorStyles.boldLabel);
            filter = (Filter)GUILayout.Toolbar((int)filter, new[] { "ALL", "CRITICAL", "WARNING" });

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
                    if (GUILayout.Button("SELECT", GUILayout.Width(90)))
                    {
                        Selection.activeObject = issue.Target;
                        EditorGUIUtility.PingObject(issue.Target);
                    }
                }

                EditorGUILayout.EndVertical();
            }

            if (count == 0)
                EditorGUILayout.LabelField("No findings in this filter.", EditorStyles.miniLabel);
        }

        void DrawResultCard()
        {
            BeginCard("LAST RESULT", "A short summary of the most recent action.");
            EditorGUILayout.LabelField(summary, EditorStyles.wordWrappedLabel);
            EndCard();
        }

        void DrawSupportPanel()
        {
            BeginCard(
                "FREE FOR DEVELOPERS",
                "Optimize Your Project is free to use. It exists to remove repetitive work, make development easier, and help newer creators learn without a paywall.");

            EditorGUILayout.LabelField(
                "If the tool saves you time and you want to help it grow, optional Patreon support helps fund testing, documentation, new one-click tools, and future engine support. The project stays free either way.",
                EditorStyles.wordWrappedMiniLabel);

            var previous = GUI.backgroundColor;
            GUI.backgroundColor = EditorGUIUtility.isProSkin
                ? new Color(.74f, .48f, .82f)
                : new Color(.72f, .50f, .78f);

            if (GUILayout.Button("SUPPORT DEVELOPMENT ON PATREON", primaryButtonStyle))
                Application.OpenURL("https://www.patreon.com/cw/DedZed");

            GUI.backgroundColor = previous;
            EndCard();
        }

        void DrawUpdateFooter()
        {
            BeginCard("VERSION", "Keep the tool current without leaving this window.");
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
                    stateText = "Up to date";
                    break;
                case VRUpdateHealth.UpdateAvailable:
                    stateText = "Update available";
                    break;
                case VRUpdateHealth.FarBehind:
                    stateText = "Update recommended";
                    break;
                default:
                    stateText = VRUpdateChecker.Checking ? "Checking..." : "Update status unknown";
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
                    if (GUILayout.Button(VRUpdateChecker.Checking ? "CHECKING..." : "CHECK UPDATE", GUILayout.MinWidth(100)))
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
