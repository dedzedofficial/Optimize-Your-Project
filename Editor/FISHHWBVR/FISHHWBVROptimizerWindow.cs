using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class FISHHWBVROptimizerWindow : EditorWindow
    {
        enum Page { World, Avatar, Project, Updates }
        enum Area { None, Textures, Particles, Lights, Meshes, Materials, Compression }
        enum Filter { All, Critical, Warning }
        static readonly int[] Sizes = { 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384 };
        static readonly string[] SizeNames = { "32", "64", "128", "256", "512", "1024", "2048", "4096", "8192", "16384", "Custom..." };
        VRSettings settings;
        Page page;
        Area area;
        Filter filter;
        GameObject avatar;
        List<VRIssue> results = new List<VRIssue>();
        List<VRTextureChange> texturePreview;
        List<VRMeshCompressionEntry> meshPreview;
        ModelImporterMeshCompression meshLevel = ModelImporterMeshCompression.Medium;
        Vector2 scroll;
        List<VRCompressionChange> compressionPreview;
        string projectFolder = "Assets";
        bool showIssues = true;
        int compressionPage;
        Texture2D icon;
        bool showParticleControls;
        string summary = "Choose World, Avatar or Project, then select a job.";

        [MenuItem("FISHHWB/VR Optimizer")]
        static void Open()
        {
            var window = GetWindow<FISHHWBVROptimizerWindow>();
            window.minSize = new Vector2(350, 520);
            window.titleContent = new GUIContent("VR Optimizer", window.icon);
        }
        void OnEnable()
        {
            settings = VRSettings.Load();
            icon = AssetDatabase.LoadAssetAtPath<Texture2D>("Packages/com.fishhwb.vr-optimizer/Editor/FISHHWBVR/Icons/VR-Optimizer.png");
            titleContent = new GUIContent("VR Optimizer", icon);
            VRUpdateChecker.CheckIfDue();
        }

        void OnGUI()
        {
            if (settings == null) settings = VRSettings.Load();
            scroll = EditorGUILayout.BeginScrollView(scroll);
            DrawHeader();
            GUILayout.Space(10);
            var nextPage = (Page)GUILayout.Toolbar((int)page, new[] { "WORLD", "AVATAR", "PROJECT", "UPDATES" }, GUILayout.Height(36));
            if (nextPage != page) { page = nextPage; ResetView(); }
            GUILayout.Space(9);
            if (page == Page.Updates)
            {
                DrawUpdatesPage();
                DrawFooter();
                EditorGUILayout.EndScrollView();
                return;
            }
            if (page == Page.Avatar)
            {
                var selected = (GameObject)EditorGUILayout.ObjectField("Scene avatar root", avatar, typeof(GameObject), true);
                if (GUILayout.Button("USE CURRENT SELECTION")) selected = Selection.activeGameObject;
                if (selected != avatar) { avatar = selected; ResetView(); }
                if (!VRAvatarWorkflow.EditableRoot(avatar))
                    EditorGUILayout.HelpBox("Select an avatar root in a loaded scene. Prefab assets must be opened in a scene before editing.", MessageType.Info);
            }
            else if (page == Page.World)
                EditorGUILayout.HelpBox("World: loaded scenes. Texture caps cover project assets.", MessageType.None);
            else
            {
                var nextFolder = EditorGUILayout.TextField("Assets folder", projectFolder);
                if (nextFolder != projectFolder) { projectFolder = nextFolder; compressionPreview = null; }
                if (!AssetDatabase.IsValidFolder(projectFolder) ||
                    projectFolder != "Assets" && !projectFolder.StartsWith("Assets/", StringComparison.Ordinal))
                    EditorGUILayout.HelpBox("Enter an existing folder under Assets.", MessageType.Warning);
            }

            GUILayout.Space(6);
            EditorGUILayout.LabelField("01  CHOOSE A JOB", EditorStyles.boldLabel);
            if (page == Page.Project)
                AreaButton(Area.Compression, "TEXTURE COMPRESSION");
            else
            {
                EditorGUILayout.BeginHorizontal();
                AreaButton(Area.Textures, "TEXTURES");
                AreaButton(Area.Particles, "PARTICLES");
                AreaButton(Area.Lights, "LIGHTS");
                EditorGUILayout.EndHorizontal();
                EditorGUILayout.BeginHorizontal();
                AreaButton(Area.Meshes, "MESHES");
                if (page == Page.Avatar) AreaButton(Area.Materials, "MATERIALS");
                EditorGUILayout.EndHorizontal();
                AreaButton(Area.Compression, "COMPRESSION CLEANUP");
            }
            GUILayout.Space(6);
            if (area != Area.None)
            {
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                EditorGUILayout.LabelField("02  " + area.ToString().ToUpperInvariant(), EditorStyles.boldLabel);
                DrawArea();
                EditorGUILayout.EndVertical();
            }
            GUILayout.Space(8);
            EditorGUILayout.HelpBox(summary, MessageType.Info);
            DrawResults();
            DrawFooter();
            EditorGUILayout.EndScrollView();
        }

        static bool JobButton(string label, bool active)
        {
            var previous = GUI.backgroundColor;
            if (active) GUI.backgroundColor = new Color(.36f, .84f, .77f);
            bool pressed = GUILayout.Button(label, GUILayout.Height(36));
            GUI.backgroundColor = previous;
            return pressed;
        }

        void DrawFooter()
        {
            GUILayout.Space(12);
            EditorGUILayout.LabelField("FISHHWB | DED ZED  •  FREE UNITY EDITOR TOOL", EditorStyles.centeredGreyMiniLabel);
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("WEBSITE")) Application.OpenURL("https://fishhwb.github.io/");
            if (GUILayout.Button("DISCORD")) Application.OpenURL("https://discord.gg/wZGxxkk4Jg");
            if (GUILayout.Button("PATREON")) Application.OpenURL("https://www.patreon.com/cw/DedZed");
            EditorGUILayout.EndHorizontal();
        }

        void DrawUpdatesPage()
        {
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("PACKAGE UPDATES", new GUIStyle(EditorStyles.boldLabel) { fontSize = 16 });
            EditorGUILayout.LabelField("Installed version", "v" + VRUpdateChecker.CurrentVersion);
            EditorGUILayout.LabelField("Install source", VRUpdateChecker.SourceLabel);
            GUILayout.Space(7);
            if (VRUpdateChecker.HasUpdate)
                EditorGUILayout.HelpBox("A newer release is available: " + VRUpdateChecker.LatestTag, MessageType.Info);
            else
                EditorGUILayout.HelpBox(VRUpdateChecker.Checking ? "Checking GitHub..." :
                    string.IsNullOrEmpty(VRUpdateChecker.Message) ? "Check GitHub for the latest published release." : VRUpdateChecker.Message, MessageType.None);
            using (new EditorGUI.DisabledScope(VRUpdateChecker.Checking || VRUpdateChecker.Installing))
                if (GUILayout.Button("CHECK FOR UPDATES", GUILayout.Height(36))) VRUpdateChecker.Check(true);
            if (VRUpdateChecker.HasUpdate)
            {
                if (GUILayout.Button("VIEW RELEASE NOTES", GUILayout.Height(30))) VRUpdateChecker.ViewRelease();
                using (new EditorGUI.DisabledScope(VRUpdateChecker.Installing))
                    if (GUILayout.Button(VRUpdateChecker.CanUpdateDirectly ? "UPDATE IN UNITY" : "HOW TO UPDATE", GUILayout.Height(36))) VRUpdateChecker.Update();
            }
            else if (GUILayout.Button("VIEW GITHUB RELEASES")) Application.OpenURL("https://github.com/dedzedofficial/VR-Optimizer/releases");
            GUILayout.Space(6);
            EditorGUILayout.LabelField("Git installations update through Unity Package Manager. VCC and embedded packages use their own installation source.", EditorStyles.wordWrappedMiniLabel);
            EditorGUILayout.EndVertical();
        }

        void ResetView()
        {
            area = Area.None;
            results.Clear();
            texturePreview = null;
            meshPreview = null;
            compressionPreview = null;
            compressionPage = 0;
            summary = "Choose a job to inspect.";
        }

        void AreaButton(Area target, string label)
        {
            using (new EditorGUI.DisabledScope(page == Page.Avatar && !VRAvatarWorkflow.EditableRoot(avatar) ||
                page == Page.Project && (!AssetDatabase.IsValidFolder(projectFolder) ||
                    projectFolder != "Assets" && !projectFolder.StartsWith("Assets/", StringComparison.Ordinal))))
                if (JobButton(label, target == area))
                {
                    area = target;
                    texturePreview = null;
                    meshPreview = null;
                    compressionPreview = null;
                    compressionPage = 0;
                    if (target == Area.Compression) summary = "Scan uncompressed texture imports in the selected scope.";
                    else ScanArea();
                }
        }

        void ScanArea()
        {
            results.Clear();
            if (area == Area.Compression) return;
            if (page == Page.Avatar)
            {
                if (!VRAvatarWorkflow.EditableRoot(avatar)) return;
                var all = VRAvatarWorkflow.Check(avatar, out string overview);
                foreach (var issue in all) if (Matches(issue.Category)) results.Add(issue);
                if (area == Area.Meshes)
                    foreach (var skin in avatar.GetComponentsInChildren<SkinnedMeshRenderer>(true))
                        if (skin.sharedMesh) results.Add(new VRIssue(VRSeverity.Info, VRCategory.Mesh,
                            skin.name + ": " + skin.sharedMesh.vertexCount + " vertices", skin));
                if (area == Area.Lights)
                    foreach (var light in avatar.GetComponentsInChildren<Light>(true))
                        if (light.enabled && light.shadows != LightShadows.None)
                            results.Add(new VRIssue(VRSeverity.Warning, VRCategory.Light, light.name + ": shadows enabled", light, null, true));
                summary = overview + " | " + area + " findings: " + results.Count;
            }
            else if (area == Area.Materials) return;
            else
            {
                VRCategory category = area == Area.Textures ? VRCategory.Texture : area == Area.Particles ? VRCategory.Particle : area == Area.Lights ? VRCategory.Light : VRCategory.Mesh;
                results = VRProjectScanner.Scan(settings, category, out bool cancelled);
                if (area == Area.Particles) results.RemoveAll(issue => !string.IsNullOrEmpty(issue.AssetPath));
                summary = (cancelled ? "Scan cancelled. Partial " : "Scan complete. ") + area + " findings: " + results.Count;
            }
        }

        bool Matches(VRCategory category)
        {
            return area == Area.Textures && category == VRCategory.Texture ||
                   area == Area.Particles && category == VRCategory.Particle ||
                   area == Area.Lights && category == VRCategory.Light ||
                   area == Area.Meshes && category == VRCategory.Mesh ||
                   area == Area.Materials && category == VRCategory.Material;
        }

        void DrawArea()
        {
            if (area == Area.Compression) DrawCompression();
            else if (area == Area.Textures)
            {
                EditorGUI.BeginChangeCheck();
                settings.pc = SizeField("PC / Standalone", settings.pc);
                settings.android = SizeField("Android / Quest", settings.android);
                settings.ios = SizeField("iOS", settings.ios);
                if (EditorGUI.EndChangeCheck()) { settings.Sanitize(); settings.Save(); texturePreview = null; }
                if (GUILayout.Button("PREVIEW TEXTURE CHANGES", GUILayout.Height(30)))
                {
                    texturePreview = VRAvatarWorkflow.CollectTextures(page == Page.Avatar ? avatar : null, settings);
                    summary = texturePreview.Count + " textures in preview. World scope includes supported textures under Assets.";
                }
                DrawTexturePreview();
            }
            else if (area == Area.Particles)
            {
                showParticleControls = EditorGUILayout.Foldout(showParticleControls, "Particle controls", true);
                if (showParticleControls)
                {
                    EditorGUI.BeginChangeCheck();
                    settings.capParticles = EditorGUILayout.Toggle("Cap particle count", settings.capParticles);
                    if (settings.capParticles) settings.maxParticles = EditorGUILayout.IntField("Maximum particles", settings.maxParticles);
                    settings.capLifetime = EditorGUILayout.Toggle("Cap constant lifetime", settings.capLifetime);
                    if (settings.capLifetime) settings.maxLifetime = EditorGUILayout.FloatField("Maximum lifetime", settings.maxLifetime);
                    settings.disableTrails = EditorGUILayout.Toggle("Disable trails", settings.disableTrails);
                    settings.disableCollision = EditorGUILayout.Toggle("Disable collision", settings.disableCollision);
                    settings.disableNoise = EditorGUILayout.Toggle("Disable noise", settings.disableNoise);
                    settings.disableLights = EditorGUILayout.Toggle("Disable particle lights", settings.disableLights);
                    settings.disableShadows = EditorGUILayout.Toggle("Disable shadows", settings.disableShadows);
                    settings.disableSubEmitters = EditorGUILayout.Toggle("Disable sub emitters", settings.disableSubEmitters);
                    if (EditorGUI.EndChangeCheck()) { settings.Sanitize(); settings.Save(); }
                }
                if (GUILayout.Button(page == Page.Avatar ? "OPTIMIZE AVATAR PARTICLES" : "OPTIMIZE SCENE PARTICLES", GUILayout.Height(30))) OptimizeParticles();
            }
            else if (area == Area.Meshes)
            {
                EditorGUILayout.HelpBox("Mesh compression can reduce built asset size but may change vertex precision. Review each model and check its appearance after applying.", MessageType.None);
                meshLevel = (ModelImporterMeshCompression)EditorGUILayout.EnumPopup("Compression level", meshLevel);
                if (GUILayout.Button("PREVIEW MESH COMPRESSION", GUILayout.Height(30)))
                {
                    meshPreview = VRMeshCompression.Collect(page == Page.Avatar ? avatar : null);
                    summary = meshPreview.Count + " imported models used in this scope.";
                }
                DrawMeshPreview();
            }
            else EditorGUILayout.LabelField("Review the issues below and select an object to inspect it.", EditorStyles.wordWrappedMiniLabel);
            if (area != Area.Compression && GUILayout.Button("REFRESH " + area.ToString().ToUpperInvariant() + " ISSUES")) ScanArea();
        }

        void DrawHeader()
        {
            var rect = GUILayoutUtility.GetRect(1, 74, GUILayout.ExpandWidth(true));
            EditorGUI.DrawRect(rect, EditorGUIUtility.isProSkin ? new Color(.08f, .19f, .22f) : new Color(.72f, .88f, .87f));
            if (icon) GUI.DrawTexture(new Rect(rect.x + 13, rect.y + 12, 50, 50), icon, ScaleMode.ScaleToFit, true);
            var title = new GUIStyle(EditorStyles.boldLabel) { fontSize = 15 };
            var subtitle = new GUIStyle(EditorStyles.miniLabel);
            if (EditorGUIUtility.isProSkin)
            {
                title.normal.textColor = Color.white;
                subtitle.normal.textColor = new Color(.65f, .88f, .85f);
            }
            GUI.Label(new Rect(rect.x + 72, rect.y + 12, rect.width - 80, 23), "FISHHWB VR OPTIMIZER", title);
            GUI.Label(new Rect(rect.x + 72, rect.y + 38, rect.width - 80, 22), "v" + VRUpdateChecker.CurrentVersion + "  •  " + (VRUpdateChecker.HasUpdate ? "UPDATE AVAILABLE" : "UNITY EDITOR TOOLS"), subtitle);
        }

        void DrawCompression()
        {
            EditorGUILayout.HelpBox("Find uncompressed automatic texture imports. Preview each platform before changing it to Unity's automatic compressed format. Explicitly chosen formats are skipped.", MessageType.None);
            if (GUILayout.Button("SCAN UNCOMPRESSED TEXTURES", GUILayout.Height(32)))
            {
                compressionPreview = VRTextureCompression.Collect(page == Page.Avatar ? avatar : null,
                    page == Page.Project ? projectFolder : "Assets", out bool cancelled);
                compressionPage = 0;
                summary = (cancelled ? "Scan cancelled. Partial results: " : "Scan complete: ") + compressionPreview.Count + " platform settings to review.";
            }
            if (compressionPreview == null) return;
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("INCLUDE ALL")) foreach (var item in compressionPreview) item.Include = true;
            if (GUILayout.Button("EXCLUDE ALL")) foreach (var item in compressionPreview) item.Include = false;
            EditorGUILayout.EndHorizontal();
            int selected = 0;
            foreach (var item in compressionPreview) if (item.Include) selected++;
            const int pageSize = 30;
            int pages = Mathf.Max(1, (compressionPreview.Count + pageSize - 1) / pageSize);
            compressionPage = Mathf.Clamp(compressionPage, 0, pages - 1);
            EditorGUILayout.BeginHorizontal();
            using (new EditorGUI.DisabledScope(compressionPage == 0))
                if (GUILayout.Button("PREVIOUS", GUILayout.Width(100))) compressionPage--;
            GUILayout.FlexibleSpace();
            EditorGUILayout.LabelField("Page " + (compressionPage + 1) + " / " + pages, GUILayout.Width(100));
            using (new EditorGUI.DisabledScope(compressionPage >= pages - 1))
                if (GUILayout.Button("NEXT", GUILayout.Width(100))) compressionPage++;
            EditorGUILayout.EndHorizontal();
            for (int i = compressionPage * pageSize; i < Mathf.Min(compressionPreview.Count, (compressionPage + 1) * pageSize); i++)
            {
                var item = compressionPreview[i];
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                item.Include = EditorGUILayout.ToggleLeft(item.Path, item.Include);
                EditorGUILayout.LabelField(item.Platform + "  •  Uncompressed → Automatic compressed  •  max " + item.BeforeSize, EditorStyles.miniLabel);
                EditorGUILayout.EndVertical();
            }
            selected = 0;
            foreach (var item in compressionPreview) if (item.Include) selected++;
            EditorGUILayout.LabelField(selected + " of " + compressionPreview.Count + " platform settings selected", EditorStyles.miniLabel);
            if (selected == 0) return;
            if (GUILayout.Button("APPLY SELECTED COMPRESSION", GUILayout.Height(34)) &&
                EditorUtility.DisplayDialog("Apply texture compression?", "Reimport selected textures using automatic platform compression. Inspect alpha, masks, gradients and normal maps afterward. Restore importer settings through version control if needed.", "Apply", "Cancel"))
                ApplyCompression();
        }

        void ApplyCompression()
        {
            var grouped = new SortedDictionary<string, List<VRCompressionChange>>(StringComparer.Ordinal);
            foreach (var item in compressionPreview)
            {
                if (!item.Include) continue;
                if (!grouped.TryGetValue(item.Path, out var items)) { items = new List<VRCompressionChange>(); grouped.Add(item.Path, items); }
                items.Add(item);
            }
            int changed = 0, unchanged = 0, failed = 0, processed = 0;
            bool cancelled = false;
            try
            {
                foreach (var pair in grouped)
                {
                    if (EditorUtility.DisplayCancelableProgressBar("Compress Textures", pair.Key, grouped.Count == 0 ? 1 : (float)processed / grouped.Count)) { cancelled = true; break; }
                    processed++;
                    try
                    {
                        if (VRTextureCompression.Apply(pair.Key, pair.Value, out string formats))
                        { changed++; Debug.Log("VR Optimizer: " + pair.Key + " → " + formats); }
                        else unchanged++;
                    }
                    catch (Exception error) { failed++; Debug.LogError("VR Optimizer: " + pair.Key + " — " + error); }
                }
            }
            finally { EditorUtility.ClearProgressBar(); }
            summary = (cancelled ? "Cancelled. " : "Complete. ") + "Textures changed: " + changed + ", unchanged: " + unchanged + ", failed: " + failed + ". Rescan to verify; resolved formats are in Console.";
            compressionPreview = null;
        }

        static int SizeField(string label, int value)
        {
            int index = Array.IndexOf(Sizes, value);
            int selected = EditorGUILayout.Popup(label, index < 0 ? Sizes.Length : index, SizeNames);
            if (selected < Sizes.Length) return Sizes[selected];
            int typed = EditorGUILayout.IntField("Custom " + label, value);
            return Mathf.Clamp(Mathf.ClosestPowerOfTwo(Mathf.Max(32, typed)), 32, 16384);
        }

        void DrawTexturePreview()
        {
            if (texturePreview == null) return;
            EditorGUILayout.LabelField("Current → proposed PC / Android / iOS", EditorStyles.miniBoldLabel);
            foreach (var item in texturePreview)
            {
                item.Include = EditorGUILayout.ToggleLeft(item.Path + (item.Changed ? "" : " (unchanged)"), item.Include);
                EditorGUILayout.LabelField("    " + item.Before[0] + " → " + item.After[0] + " / " + item.Before[1] + " → " + item.After[1] + " / " + item.Before[2] + " → " + item.After[2], EditorStyles.miniLabel);
            }
            if (GUILayout.Button("APPLY SELECTED TEXTURES", GUILayout.Height(30)))
            {
                int changed = 0, unchanged = 0, excluded = 0, failed = 0;
                bool cancelled = false;
                try
                {
                    for (int i = 0; i < texturePreview.Count; i++)
                    {
                        var item = texturePreview[i];
                        if (EditorUtility.DisplayCancelableProgressBar("Apply Texture Changes", item.Path, (float)i / texturePreview.Count)) { cancelled = true; break; }
                        if (!item.Include) { excluded++; continue; }
                        if (!item.Changed) { unchanged++; continue; }
                        try { if (VRTextureOptimizer.Optimize(item.Path, settings)) changed++; else unchanged++; }
                        catch (Exception error) { failed++; Debug.LogError("VR Optimizer: " + item.Path + " — " + error); }
                    }
                }
                finally { EditorUtility.ClearProgressBar(); }
                summary = (cancelled ? "Cancelled. " : "Complete. ") + "Changed " + changed + ", unchanged " + unchanged + ", excluded " + excluded + ", failed " + failed + ".";
                texturePreview = null;
                var report = summary;
                ScanArea();
                summary = report;
            }
        }

        void DrawMeshPreview()
        {
            if (meshPreview == null) return;
            foreach (var item in meshPreview)
                item.Include = EditorGUILayout.ToggleLeft(item.Path + "   " + item.Current + " → " + meshLevel + "   (" + item.Renderers + " renderers)", item.Include);
            if (meshLevel == ModelImporterMeshCompression.Off) return;
            if (GUILayout.Button("APPLY SELECTED MODEL IMPORTS", GUILayout.Height(30)) &&
                EditorUtility.DisplayDialog("Apply mesh compression?", "The selected models will be reimported. Compression may cause visible vertex or UV changes. Review your scene after applying; restore importer settings through version control if needed.", "Apply", "Cancel"))
            {
                int changed = 0, skipped = 0, failed = 0;
                bool cancelled = false;
                try
                {
                    for (int i = 0; i < meshPreview.Count; i++)
                    {
                        var item = meshPreview[i];
                        if (EditorUtility.DisplayCancelableProgressBar("Apply Mesh Compression", item.Path, (float)i / meshPreview.Count)) { cancelled = true; break; }
                        if (!item.Include || item.Current == meshLevel) { skipped++; continue; }
                        try
                        {
                            var importer = AssetImporter.GetAtPath(item.Path) as ModelImporter;
                            if (!importer) { skipped++; continue; }
                            importer.meshCompression = meshLevel;
                            importer.SaveAndReimport();
                            changed++;
                        }
                        catch (Exception error) { failed++; Debug.LogError("VR Optimizer: " + item.Path + " — " + error); }
                    }
                }
                finally { EditorUtility.ClearProgressBar(); }
                summary = (cancelled ? "Cancelled. " : "Complete. ") + "Models changed " + changed + ", skipped " + skipped + ", failed " + failed + ". Inspect appearance in the target build.";
                meshPreview = null;
            }
        }

        void OptimizeParticles()
        {
            var particles = new List<ParticleSystem>(page == Page.Avatar ? (IEnumerable<ParticleSystem>)avatar.GetComponentsInChildren<ParticleSystem>(true) : VRProjectScanner.SceneObjects<ParticleSystem>());
            int changed = 0, failed = 0;
            bool cancelled = false;
            int group = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName("Optimize Particles");
            try
            {
                for (int i = 0; i < particles.Count; i++)
                {
                    if (EditorUtility.DisplayCancelableProgressBar("Optimize Particles", particles[i].name, (float)i / particles.Count)) { cancelled = true; break; }
                    try { if (VRParticleOptimizer.Optimize(particles[i], settings)) changed++; }
                    catch (Exception error) { failed++; Debug.LogError("VR Optimizer: " + particles[i].name + " — " + error); }
                }
            }
            finally { EditorUtility.ClearProgressBar(); Undo.CollapseUndoOperations(group); }
            summary = (cancelled ? "Cancelled. " : "Complete. ") + "Particles found " + particles.Count + ", changed " + changed + ", failed " + failed + ". Use Undo to revert; save scenes when satisfied.";
            var report = summary;
            ScanArea();
            summary = report;
        }

        void DrawResults()
        {
            if (area == Area.None || area == Area.Compression) return;
            showIssues = EditorGUILayout.Foldout(showIssues, "ISSUES  •  " + results.Count + " found", true);
            if (!showIssues) return;
            filter = (Filter)GUILayout.Toolbar((int)filter, new[] { "ALL", "CRITICAL", "WARNING" });
            int visible = 0;
            foreach (var issue in results)
            {
                if (filter == Filter.Critical && issue.Severity != VRSeverity.Critical ||
                    filter == Filter.Warning && issue.Severity != VRSeverity.Warning) continue;
                visible++;
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                EditorGUILayout.LabelField(issue.Severity + "  •  " + issue.Message, EditorStyles.wordWrappedLabel);
                if (!string.IsNullOrEmpty(issue.AssetPath)) EditorGUILayout.LabelField(issue.AssetPath, EditorStyles.miniLabel);
                using (new EditorGUI.DisabledScope(!issue.Target))
                    if (GUILayout.Button("SELECT", GUILayout.Width(90))) { Selection.activeObject = issue.Target; EditorGUIUtility.PingObject(issue.Target); }
                if (issue.Category == VRCategory.Light && issue.Target is Light light && string.IsNullOrEmpty(issue.AssetPath) && light.shadows != LightShadows.None &&
                    GUILayout.Button("REVIEW SHADOWS", GUILayout.Width(150)) &&
                    EditorUtility.DisplayDialog("Disable shadows?", "Disable shadows on " + light.name + "? This change supports Undo.", "Disable", "Cancel"))
                {
                    VRLightOptimizer.Optimize(light, settings);
                    ScanArea();
                    EditorGUILayout.EndVertical();
                    break;
                }
                EditorGUILayout.EndVertical();
            }
            if (visible == 0) EditorGUILayout.LabelField("No " + filter.ToString().ToLowerInvariant() + " findings in this area.", EditorStyles.wordWrappedMiniLabel);
        }
    }
}
