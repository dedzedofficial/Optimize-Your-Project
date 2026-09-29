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

        [MenuItem("FISHHWB/Optimize Your Project")]
        static void Open()
        {
            var window = GetWindow<FISHHWBVROptimizerWindow>();
            window.minSize = new Vector2(390, 560);
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

            scroll = EditorGUILayout.BeginScrollView(scroll);
            Header();
            GUILayout.Space(8);

            var next = (Page)GUILayout.Toolbar((int)page, new[] { "PROJECT", "AVATAR" }, GUILayout.Height(34));
            if (next != page)
            {
                page = next;
                issues = null;
                summary = "Choose a job and press its button.";
            }

            GUILayout.Space(10);

            if (page == Page.Project) DrawProject();
            else DrawAvatar();

            GUILayout.Space(8);
            EditorGUILayout.HelpBox(summary, MessageType.Info);
            DrawUpdateFooter();
            DrawLinksFooter();
            EditorGUILayout.EndScrollView();
        }

        void Header()
        {
            var rect = GUILayoutUtility.GetRect(1, 68, GUILayout.ExpandWidth(true));
            EditorGUI.DrawRect(
                rect,
                EditorGUIUtility.isProSkin
                    ? new Color(.075f, .14f, .16f)
                    : new Color(.78f, .88f, .87f));

            if (icon)
                GUI.DrawTexture(new Rect(rect.x + 12, rect.y + 10, 48, 48), icon, ScaleMode.ScaleToFit, true);

            var title = new GUIStyle(EditorStyles.boldLabel) { fontSize = 15 };
            var detail = new GUIStyle(EditorStyles.miniLabel);

            if (EditorGUIUtility.isProSkin)
            {
                title.normal.textColor = Color.white;
                detail.normal.textColor = new Color(.68f, .86f, .83f);
            }

            GUI.Label(new Rect(rect.x + 70, rect.y + 10, rect.width - 80, 24), "OPTIMIZE YOUR PROJECT", title);
            GUI.Label(
                new Rect(rect.x + 70, rect.y + 37, rect.width - 80, 20),
                "v" + VRUpdateChecker.CurrentVersion + "  •  ONE-CLICK OPTIMIZATION",
                detail);
        }

        void DrawProject()
        {
            EditorGUILayout.LabelField("UNITY PROJECT", EditorStyles.boldLabel);
            EditorGUILayout.LabelField(
                "Optimize project assets and the scenes currently loaded in Unity. Run only the job you need.",
                EditorStyles.wordWrappedMiniLabel);

            GUILayout.Space(6);

            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("ASSET SCOPE", EditorStyles.boldLabel);
            string chosen = EditorGUILayout.TextField("Assets folder", projectFolder);
            if (chosen != projectFolder) projectFolder = chosen;

            bool valid = projectFolder == "Assets" ||
                         projectFolder.StartsWith("Assets/", StringComparison.Ordinal) &&
                         AssetDatabase.IsValidFolder(projectFolder);

            if (!valid)
                EditorGUILayout.HelpBox("Enter an existing folder under Assets.", MessageType.Warning);
            EditorGUILayout.EndVertical();

            using (new EditorGUI.DisabledScope(!valid))
                TextureCard(null, "TEXTURES", "Resize and compress supported textures in the selected Assets folder.", projectFolder);

            ParticleCard(null);
            MeshCard(null);
            LightCard(null);

            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("PROJECT CHECK", EditorStyles.boldLabel);
            EditorGUILayout.LabelField(
                "Only use this when you want a detailed list. Normal one-click jobs stay clean and do not print every issue.",
                EditorStyles.wordWrappedMiniLabel);

            if (GUILayout.Button("SCAN ENTIRE PROJECT", GUILayout.Height(34)))
            {
                issues = VRProjectScanner.Scan(settings, null, out bool cancelled);
                summary = (cancelled ? "Partial scan: " : "Project scan complete: ") + issues.Count + " findings.";
            }

            EditorGUILayout.EndVertical();
            DrawIssues();
        }

        void DrawAvatar()
        {
            EditorGUILayout.LabelField("AVATAR", EditorStyles.boldLabel);
            EditorGUILayout.LabelField(
                "Use the same simple jobs on one selected avatar hierarchy.",
                EditorStyles.wordWrappedMiniLabel);

            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("AVATAR ROOT", EditorStyles.boldLabel);
            avatar = (GameObject)EditorGUILayout.ObjectField(avatar, typeof(GameObject), true);

            if (GUILayout.Button("USE CURRENT SELECTION"))
                avatar = Selection.activeGameObject;

            bool valid = VRAvatarWorkflow.EditableRoot(avatar);
            if (!valid)
                EditorGUILayout.HelpBox("Select an avatar root in a loaded scene.", MessageType.Info);
            EditorGUILayout.EndVertical();

            using (new EditorGUI.DisabledScope(!valid))
            {
                TextureCard(avatar, "TEXTURES", "Resize and compress textures referenced by this avatar.");
                ParticleCard(avatar);
                MeshCard(avatar);
                LightCard(avatar);
            }
        }

        void TextureCard(GameObject root, string title, string scope, string folder = "Assets")
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField(title, EditorStyles.boldLabel);
            EditorGUILayout.LabelField(scope, EditorStyles.wordWrappedMiniLabel);

            EditorGUI.BeginChangeCheck();
            settings.pc = SizeField("PC / Standalone", settings.pc);
            settings.android = SizeField("Android / Quest", settings.android);
            settings.ios = SizeField("iOS", settings.ios);

            if (EditorGUI.EndChangeCheck())
            {
                settings.Sanitize();
                settings.Save();
            }

            if (GUILayout.Button("COMPRESS & SIZE TEXTURES", GUILayout.Height(36)))
                OptimizeTextures(root, folder);

            EditorGUILayout.EndVertical();
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
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("PARTICLES", EditorStyles.boldLabel);
            EditorGUILayout.LabelField(
                root ? "Optimize particle systems under this avatar." : "Optimize particle systems in loaded scenes.",
                EditorStyles.wordWrappedMiniLabel);

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

            if (GUILayout.Button("OPTIMIZE PARTICLES", GUILayout.Height(36)))
                OptimizeParticles(root);

            EditorGUILayout.EndVertical();
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
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("MESH IMPORTS", EditorStyles.boldLabel);
            EditorGUILayout.LabelField(
                root ? "Compress imported model assets referenced by this avatar." : "Compress imported model assets used by loaded scenes.",
                EditorStyles.wordWrappedMiniLabel);

            meshLevel = (ModelImporterMeshCompression)EditorGUILayout.EnumPopup("Compression", meshLevel);

            if (GUILayout.Button("COMPRESS IMPORTED MESHES", GUILayout.Height(36)))
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

            EditorGUILayout.EndVertical();
        }

        void LightCard(GameObject root)
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("REALTIME LIGHT SHADOWS", EditorStyles.boldLabel);
            EditorGUILayout.LabelField(
                root ? "Disable realtime shadows under this avatar." : "Disable realtime shadows in loaded scenes.",
                EditorStyles.wordWrappedMiniLabel);

            if (GUILayout.Button("DISABLE REALTIME SHADOWS", GUILayout.Height(36)))
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

            EditorGUILayout.EndVertical();
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
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                EditorGUILayout.LabelField(issue.Severity + "  •  " + issue.Message, EditorStyles.wordWrappedLabel);

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

        void DrawUpdateFooter()
        {
            GUILayout.Space(12);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
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

            EditorGUILayout.EndVertical();
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
            EditorGUILayout.LabelField("FISHHWB | DED ZED", EditorStyles.centeredGreyMiniLabel);
            EditorGUILayout.BeginHorizontal();

            if (GUILayout.Button("GITHUB"))
                Application.OpenURL("https://github.com/dedzedofficial/Optimize-Your-Project");

            if (GUILayout.Button("WEBSITE"))
                Application.OpenURL("https://fishhwb.github.io/");

            if (GUILayout.Button("DISCORD"))
                Application.OpenURL("https://discord.gg/wZGxxkk4Jg");

            EditorGUILayout.EndHorizontal();
        }
    }
}
