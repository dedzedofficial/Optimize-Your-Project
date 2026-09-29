using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class FISHHWBVROptimizerWindow : EditorWindow
    {
        enum Page { World, Avatar, Project, Updates }
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
        string summary = "Choose a job and press its action button.";
        bool showParticleControls;

        [MenuItem("FISHHWB/Optimize Your Project")]
        static void Open()
        {
            var window = GetWindow<FISHHWBVROptimizerWindow>();
            window.minSize = new Vector2(350, 520);
            window.titleContent = new GUIContent("Optimize Your Project", window.icon);
        }
        void OnEnable()
        {
            settings = VRSettings.Load();
            icon = AssetDatabase.LoadAssetAtPath<Texture2D>("Packages/com.fishhwb.vr-optimizer/Editor/FISHHWBVR/Icons/VR-Optimizer.png");
            titleContent = new GUIContent("Optimize Your Project", icon);
            VRUpdateChecker.CheckIfDue();
        }

        void OnGUI()
        {
            if (settings == null) settings = VRSettings.Load();
            scroll = EditorGUILayout.BeginScrollView(scroll);
            Header();
            GUILayout.Space(8);
            var next = (Page)GUILayout.Toolbar((int)page, new[] { "WORLD", "AVATAR", "PROJECT", "UPDATES" }, GUILayout.Height(36));
            if (next != page) { page = next; issues = null; summary = "Choose a job and press its action button."; }
            GUILayout.Space(10);
            if (page == Page.Updates) DrawUpdates();
            else if (page == Page.Project) DrawProject();
            else DrawScenePage();
            if (page != Page.Updates) EditorGUILayout.HelpBox(summary, MessageType.Info);
            Footer();
            EditorGUILayout.EndScrollView();
        }

        void Header()
        {
            var rect = GUILayoutUtility.GetRect(1, 74, GUILayout.ExpandWidth(true));
            EditorGUI.DrawRect(rect, EditorGUIUtility.isProSkin ? new Color(.08f, .19f, .22f) : new Color(.72f, .88f, .87f));
            if (icon) GUI.DrawTexture(new Rect(rect.x + 13, rect.y + 12, 50, 50), icon, ScaleMode.ScaleToFit, true);
            var title = new GUIStyle(EditorStyles.boldLabel) { fontSize = 15 };
            var detail = new GUIStyle(EditorStyles.miniLabel);
            if (EditorGUIUtility.isProSkin) { title.normal.textColor = Color.white; detail.normal.textColor = new Color(.65f, .88f, .85f); }
            GUI.Label(new Rect(rect.x + 72, rect.y + 11, rect.width - 80, 25), "OPTIMIZE YOUR PROJECT", title);
            GUI.Label(new Rect(rect.x + 72, rect.y + 39, rect.width - 80, 20), "v" + VRUpdateChecker.CurrentVersion + (VRUpdateChecker.HasUpdate ? "  •  UPDATE AVAILABLE" : "  •  ONE CLICK JOBS"), detail);
        }

        void DrawScenePage()
        {
            bool isAvatar = page == Page.Avatar;
            if (isAvatar)
            {
                EditorGUILayout.LabelField("AVATAR ROOT", EditorStyles.boldLabel);
                avatar = (GameObject)EditorGUILayout.ObjectField(avatar, typeof(GameObject), true);
                if (GUILayout.Button("USE CURRENT SELECTION")) avatar = Selection.activeGameObject;
                if (!VRAvatarWorkflow.EditableRoot(avatar))
                    EditorGUILayout.HelpBox("Select an avatar root in a loaded scene.", MessageType.Info);
            }
            else EditorGUILayout.LabelField("LOADED WORLD SCENES", EditorStyles.boldLabel);
            using (new EditorGUI.DisabledScope(isAvatar && !VRAvatarWorkflow.EditableRoot(avatar)))
            {
                TextureCard(isAvatar ? avatar : null, "TEXTURES", isAvatar ? "Textures used by this avatar" : "Project textures under Assets");
                ParticleCard(isAvatar ? avatar : null);
                MeshCard(isAvatar ? avatar : null);
                LightCard(isAvatar ? avatar : null);
            }
        }

        void DrawProject()
        {
            EditorGUILayout.LabelField("PROJECT TEXTURES", EditorStyles.boldLabel);
            string chosen = EditorGUILayout.TextField("Assets folder", projectFolder);
            if (chosen != projectFolder) projectFolder = chosen;
            bool valid = projectFolder == "Assets" || projectFolder.StartsWith("Assets/", StringComparison.Ordinal) && AssetDatabase.IsValidFolder(projectFolder);
            if (!valid) EditorGUILayout.HelpBox("Enter an existing folder under Assets.", MessageType.Warning);
            using (new EditorGUI.DisabledScope(!valid))
                TextureCard(null, "COMPRESS & SIZE", "Optimise supported textures in this folder", projectFolder);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("PROJECT DIAGNOSTICS", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Scan assets and loaded scenes to view warnings and issues.", EditorStyles.wordWrappedMiniLabel);
            if (GUILayout.Button("SCAN ENTIRE PROJECT", GUILayout.Height(36)))
            {
                issues = VRProjectScanner.Scan(settings, null, out bool cancelled);
                summary = (cancelled ? "Partial scan: " : "Project scan complete: ") + issues.Count + " findings.";
            }
            EditorGUILayout.EndVertical();
            DrawIssues();
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
            if (EditorGUI.EndChangeCheck()) { settings.Sanitize(); settings.Save(); }
            EditorGUILayout.LabelField("Applies maximum size caps and automatic platform compression to eligible uncompressed imports.", EditorStyles.wordWrappedMiniLabel);
            if (GUILayout.Button("COMPRESS & SIZE TEXTURES", GUILayout.Height(36))) OptimizeTextures(root, folder);
            EditorGUILayout.EndVertical();
        }

        static int SizeField(string label, int value)
        {
            int index = Array.IndexOf(Sizes, value);
            int selected = EditorGUILayout.Popup(label, index < 0 ? Sizes.Length : index, SizeNames);
            if (selected < Sizes.Length) return Sizes[selected];
            int typed = EditorGUILayout.IntField("Custom " + label, value);
            return Mathf.Clamp(Mathf.ClosestPowerOfTwo(Mathf.Max(32, typed)), 32, 16384);
        }

        void OptimizeTextures(GameObject root, string folder)
        {
            settings.Sanitize();
            var textures = VRAvatarWorkflow.CollectTextures(root, settings);
            if (!root && folder != "Assets") textures.RemoveAll(item => !item.Path.StartsWith(folder + "/", StringComparison.Ordinal));
            var compression = VRTextureCompression.Collect(root, folder, out bool scanCancelled);
            if (scanCancelled) { summary = "Texture collection cancelled. No changes applied."; return; }
            var byPath = new Dictionary<string, List<VRCompressionChange>>(StringComparer.Ordinal);
            foreach (var item in compression)
            {
                if (!byPath.TryGetValue(item.Path, out var list)) { list = new List<VRCompressionChange>(); byPath.Add(item.Path, list); }
                list.Add(item);
            }
            if (!EditorUtility.DisplayDialog("Optimize textures", "Apply the chosen size caps and automatic compression to " + textures.Count + " supported textures? Existing explicit compression formats and stricter size caps are preserved. Review the result in your target build; importer changes are restored through version control.", "Optimize", "Cancel")) return;
            int changed = 0, unchanged = 0, failed = 0;
            bool cancelled = false;
            try
            {
                for (int i = 0; i < textures.Count; i++)
                {
                    string path = textures[i].Path;
                    if (EditorUtility.DisplayCancelableProgressBar("Optimize Textures", path, textures.Count == 0 ? 1 : (float)i / textures.Count)) { cancelled = true; break; }
                    try
                    {
                        byPath.TryGetValue(path, out var entries);
                        bool didChange = VRTextureOptimizer.OptimizeWithCompression(path, settings, entries);
                        if (didChange) changed++; else unchanged++;
                    }
                    catch (Exception error) { failed++; Debug.LogError("VR Optimizer: " + path + " — " + error); }
                }
            }
            finally { EditorUtility.ClearProgressBar(); }
            summary = (cancelled ? "Cancelled. Partial results: " : "Done. ") + changed + " textures changed, " + unchanged + " unchanged, " + failed + " failed.";
        }

        void ParticleCard(GameObject root)
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("PARTICLES", EditorStyles.boldLabel);
            EditorGUI.BeginChangeCheck();
            settings.capParticles = EditorGUILayout.Toggle("Cap particle count", settings.capParticles);
            if (settings.capParticles) settings.maxParticles = EditorGUILayout.IntField("Maximum particles", settings.maxParticles);
            showParticleControls = EditorGUILayout.Foldout(showParticleControls, "More particle controls", true);
            if (showParticleControls)
            {
                settings.capLifetime = EditorGUILayout.Toggle("Cap constant lifetime", settings.capLifetime);
                if (settings.capLifetime) settings.maxLifetime = EditorGUILayout.FloatField("Maximum lifetime", settings.maxLifetime);
                settings.disableTrails = EditorGUILayout.Toggle("Disable trails", settings.disableTrails);
                settings.disableCollision = EditorGUILayout.Toggle("Disable collision", settings.disableCollision);
                settings.disableNoise = EditorGUILayout.Toggle("Disable noise", settings.disableNoise);
                settings.disableLights = EditorGUILayout.Toggle("Disable particle lights", settings.disableLights);
                settings.disableShadows = EditorGUILayout.Toggle("Disable shadows", settings.disableShadows);
                settings.disableSubEmitters = EditorGUILayout.Toggle("Disable sub emitters", settings.disableSubEmitters);
            }
            if (EditorGUI.EndChangeCheck()) { settings.Sanitize(); settings.Save(); }
            if (GUILayout.Button("OPTIMIZE PARTICLES", GUILayout.Height(36))) OptimizeParticles(root);
            EditorGUILayout.EndVertical();
        }

        void OptimizeParticles(GameObject root)
        {
            var particles = new List<ParticleSystem>(root ? (IEnumerable<ParticleSystem>)root.GetComponentsInChildren<ParticleSystem>(true) : VRProjectScanner.SceneObjects<ParticleSystem>());
            int changed = 0, group = Undo.GetCurrentGroup();
            bool cancelled = false;
            Undo.SetCurrentGroupName("Optimize Particles");
            try
            {
                for (int i = 0; i < particles.Count; i++)
                {
                    if (EditorUtility.DisplayCancelableProgressBar("Optimize Particles", particles[i].name, particles.Count == 0 ? 1 : (float)i / particles.Count)) { cancelled = true; break; }
                    if (VRParticleOptimizer.Optimize(particles[i], settings)) changed++;
                }
            }
            finally { EditorUtility.ClearProgressBar(); Undo.CollapseUndoOperations(group); }
            summary = (cancelled ? "Cancelled. " : "Done. ") + changed + " of " + particles.Count + " particle systems changed. Use Undo if needed.";
        }

        void MeshCard(GameObject root)
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("MESHES", EditorStyles.boldLabel);
            meshLevel = (ModelImporterMeshCompression)EditorGUILayout.EnumPopup("Compression", meshLevel);
            if (GUILayout.Button("COMPRESS IMPORTED MESHES", GUILayout.Height(36)))
            {
                var meshes = VRMeshCompression.Collect(root);
                int pending = 0;
                foreach (var mesh in meshes) if (mesh.Current != meshLevel) pending++;
                if (pending == 0) summary = "Imported meshes already match this compression level.";
                else if (EditorUtility.DisplayDialog("Compress meshes", "Reimport " + pending + " model assets using " + meshLevel + " compression? Inspect vertex detail afterward. Restore importer settings through version control if needed.", "Compress", "Cancel"))
                {
                    int changed = 0, failed = 0;
                    try
                    {
                        for (int i = 0; i < meshes.Count; i++)
                        {
                            var item = meshes[i];
                            if (item.Current == meshLevel) continue;
                            if (EditorUtility.DisplayCancelableProgressBar("Compress Meshes", item.Path, (float)i / meshes.Count)) break;
                            try { var importer = AssetImporter.GetAtPath(item.Path) as ModelImporter; if (importer == null) continue; importer.meshCompression = meshLevel; importer.SaveAndReimport(); changed++; }
                            catch (Exception error) { failed++; Debug.LogError("VR Optimizer: " + item.Path + " — " + error); }
                        }
                    }
                    finally { EditorUtility.ClearProgressBar(); }
                    summary = changed + " imported meshes changed; " + failed + " failed.";
                }
            }
            EditorGUILayout.EndVertical();
        }

        void LightCard(GameObject root)
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("LIGHT SHADOWS", EditorStyles.boldLabel);
            if (GUILayout.Button("DISABLE REALTIME SHADOWS", GUILayout.Height(36)))
            {
                var lights = root ? (IEnumerable<Light>)root.GetComponentsInChildren<Light>(true) : VRProjectScanner.SceneObjects<Light>();
                var pending = new List<Light>();
                foreach (var light in lights) if (light && light.enabled && light.lightmapBakeType == LightmapBakeType.Realtime && light.shadows != LightShadows.None) pending.Add(light);
                if (pending.Count == 0) summary = "No enabled realtime shadows found in this scope.";
                else if (EditorUtility.DisplayDialog("Disable realtime shadows", "Disable shadows on " + pending.Count + " realtime lights? You can use Unity Undo to revert.", "Disable", "Cancel"))
                {
                    int group = Undo.GetCurrentGroup();
                    foreach (var light in pending) VRLightOptimizer.Optimize(light, settings);
                    Undo.CollapseUndoOperations(group);
                    summary = "Disabled shadows on " + pending.Count + " lights. Use Undo if needed.";
                }
            }
            EditorGUILayout.EndVertical();
        }

        void DrawIssues()
        {
            if (issues == null) return;
            EditorGUILayout.LabelField("PROJECT SCAN RESULTS  •  " + issues.Count, EditorStyles.boldLabel);
            filter = (Filter)GUILayout.Toolbar((int)filter, new[] { "ALL", "CRITICAL", "WARNING" });
            int count = 0;
            foreach (var issue in issues)
            {
                if (filter == Filter.Critical && issue.Severity != VRSeverity.Critical ||
                    filter == Filter.Warning && issue.Severity != VRSeverity.Warning) continue;
                count++;
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                EditorGUILayout.LabelField(issue.Severity + "  •  " + issue.Message, EditorStyles.wordWrappedLabel);
                if (!string.IsNullOrEmpty(issue.AssetPath)) EditorGUILayout.LabelField(issue.AssetPath, EditorStyles.miniLabel);
                using (new EditorGUI.DisabledScope(!issue.Target))
                    if (GUILayout.Button("SELECT", GUILayout.Width(90))) { Selection.activeObject = issue.Target; EditorGUIUtility.PingObject(issue.Target); }
                EditorGUILayout.EndVertical();
            }
            if (count == 0) EditorGUILayout.LabelField("No findings in this filter.", EditorStyles.miniLabel);
        }

        void DrawUpdates()
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("PACKAGE UPDATES", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Installed version", "v" + VRUpdateChecker.CurrentVersion);
            EditorGUILayout.LabelField("Install source", VRUpdateChecker.SourceLabel);
            EditorGUILayout.HelpBox(VRUpdateChecker.HasUpdate ? "Update available: " + VRUpdateChecker.LatestTag :
                VRUpdateChecker.Checking ? "Checking GitHub..." :
                string.IsNullOrEmpty(VRUpdateChecker.Message) ? "Check GitHub for the latest release." : VRUpdateChecker.Message, MessageType.Info);
            using (new EditorGUI.DisabledScope(VRUpdateChecker.Checking || VRUpdateChecker.Installing))
                if (GUILayout.Button("CHECK FOR UPDATES", GUILayout.Height(36))) VRUpdateChecker.Check(true);
            if (VRUpdateChecker.HasUpdate)
            {
                if (GUILayout.Button("VIEW RELEASE NOTES")) VRUpdateChecker.ViewRelease();
                if (GUILayout.Button(VRUpdateChecker.CanUpdateDirectly ? "UPDATE IN UNITY" : "HOW TO UPDATE", GUILayout.Height(36))) VRUpdateChecker.Update();
            }
            else if (GUILayout.Button("VIEW GITHUB RELEASES")) Application.OpenURL("https://github.com/dedzedofficial/Optimize-Your-Project/releases");
            EditorGUILayout.EndVertical();
        }

        void Footer()
        {
            GUILayout.Space(12);
            EditorGUILayout.LabelField("FISHHWB | DED ZED  •  FREE UNITY EDITOR TOOL", EditorStyles.centeredGreyMiniLabel);
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("WEBSITE")) Application.OpenURL("https://fishhwb.github.io/");
            if (GUILayout.Button("DISCORD")) Application.OpenURL("https://discord.gg/wZGxxkk4Jg");
            if (GUILayout.Button("PATREON")) Application.OpenURL("https://www.patreon.com/cw/DedZed");
            EditorGUILayout.EndHorizontal();
        }
    }
}
