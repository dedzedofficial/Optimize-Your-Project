using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class FISHHWBVROptimizerWindow : EditorWindow
    {
        static readonly int[] Sizes = { 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384 };
        static readonly string[] SizeNames = { "32", "64", "128", "256", "512", "1024", "2048", "4096", "8192", "16384", "Custom..." };
        VRSettings settings;
        List<VRIssue> results = new List<VRIssue>();
        Vector2 scroll;
        GameObject avatar;
        List<VRTextureChange> preview;
        bool avatarTextures = true;
        bool showParticleOptions;
        string summary = "Ready. Choose an action below to begin.";

        [MenuItem("FISHHWB/VR Optimizer")]
        static void Open() { GetWindow<FISHHWBVROptimizerWindow>("VR Optimizer").minSize = new Vector2(440, 520); }
        void OnEnable() { settings = VRSettings.Load(); }

        static void Header(string heading, string subtitle)
        {
            var rect = GUILayoutUtility.GetRect(1, 66, GUILayout.ExpandWidth(true));
            EditorGUI.DrawRect(rect, EditorGUIUtility.isProSkin ? new Color(.13f, .23f, .29f) : new Color(.78f, .87f, .9f));
            var title = new GUIStyle(EditorStyles.boldLabel) { fontSize = 18, alignment = TextAnchor.MiddleCenter };
            var small = new GUIStyle(EditorStyles.miniLabel) { alignment = TextAnchor.MiddleCenter };
            if (EditorGUIUtility.isProSkin) { title.normal.textColor = Color.white; small.normal.textColor = new Color(.8f, .9f, .95f); }
            GUI.Label(new Rect(rect.x, rect.y + 8, rect.width, 28), heading, title);
            GUI.Label(new Rect(rect.x, rect.y + 37, rect.width, 19), subtitle, small);
        }

        static int SizeField(string label, int value)
        {
            int index = Array.IndexOf(Sizes, value);
            int selected = EditorGUILayout.Popup(label, index < 0 ? Sizes.Length : index, SizeNames);
            if (selected < Sizes.Length) return Sizes[selected];
            int typed = EditorGUILayout.IntField("Custom " + label, value);
            return Mathf.Clamp(Mathf.ClosestPowerOfTwo(Mathf.Max(32, typed)), 32, 16384);
        }

        void OnGUI()
        {
            if (settings == null) settings = VRSettings.Load();
            scroll = EditorGUILayout.BeginScrollView(scroll);
            Header("FISHHWB VR OPTIMIZER", "v0.6.5  •  Free tools for VR creators");
            GUILayout.Space(10);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("AVATAR", EditorStyles.boldLabel);
            var selectedAvatar = (GameObject)EditorGUILayout.ObjectField("Scene avatar root", avatar, typeof(GameObject), true);
            if (GUILayout.Button("USE CURRENT SELECTION")) selectedAvatar = Selection.activeGameObject;
            if (selectedAvatar != avatar) { avatar = selectedAvatar; preview = null; }
            using (new EditorGUI.DisabledScope(!VRAvatarWorkflow.EditableRoot(avatar)))
            {
                if (GUILayout.Button("CHECK AVATAR"))
                {
                    results = VRAvatarWorkflow.Check(avatar, out string overview);
                    summary = overview;
                }
                if (GUILayout.Button("OPTIMIZE AVATAR PARTICLES")) OptimizeAvatarParticles();
            }
            if (avatar && !VRAvatarWorkflow.EditableRoot(avatar))
                EditorGUILayout.HelpBox("Select an avatar root in a loaded scene. Prefab assets must be opened in a scene before editing.", MessageType.Warning);
            EditorGUILayout.EndVertical();
            EditorGUI.BeginChangeCheck();
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("TEXTURES", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Set maximum imported size for each platform.", EditorStyles.wordWrappedMiniLabel);
            var preset = (VRTexturePreset)EditorGUILayout.EnumPopup("Preset", settings.texturePreset);
            if (preset != settings.texturePreset) settings.SetTexturePreset(preset);
            EditorGUI.BeginChangeCheck();
            settings.pc = SizeField("PC / Standalone", settings.pc);
            settings.android = SizeField("Android / Quest", settings.android);
            settings.ios = SizeField("iOS", settings.ios);
            if (EditorGUI.EndChangeCheck()) settings.texturePreset = VRTexturePreset.Custom;
            GUILayout.Space(4);
            bool nextAvatarTextures = EditorGUILayout.ToggleLeft("Only textures used by selected avatar", avatarTextures);
            if (nextAvatarTextures != avatarTextures) { avatarTextures = nextAvatarTextures; preview = null; }
            if (GUILayout.Button("PREVIEW TEXTURE CHANGES", GUILayout.Height(34)))
            {
                settings.Sanitize();
                if (avatarTextures && !VRAvatarWorkflow.EditableRoot(avatar))
                    summary = "Select a scene avatar root, or untick avatar-only scope.";
                else
                {
                    preview = VRAvatarWorkflow.CollectTextures(avatarTextures ? avatar : null, settings);
                    summary = "Preview: " + preview.Count + " supported textures. Review the effective caps below.";
                }
            }
            DrawPreview();
            EditorGUILayout.EndVertical();

            GUILayout.Space(6);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("PARTICLES", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Optimize particle systems in loaded scenes. Supports Undo.", EditorStyles.wordWrappedMiniLabel);
            var particlePreset = (VRParticlePreset)EditorGUILayout.EnumPopup("Preset", settings.particlePreset);
            if (particlePreset != settings.particlePreset) settings.SetParticlePreset(particlePreset);
            showParticleOptions = EditorGUILayout.Foldout(showParticleOptions, "Particle controls", true);
            if (showParticleOptions)
            {
                EditorGUI.indentLevel++;
                EditorGUI.BeginChangeCheck();
                settings.capParticles = EditorGUILayout.Toggle("Cap Particle Count", settings.capParticles);
                if (settings.capParticles) settings.maxParticles = EditorGUILayout.IntField("Maximum Particles", settings.maxParticles);
                settings.capLifetime = EditorGUILayout.Toggle("Cap Constant Lifetime", settings.capLifetime);
                if (settings.capLifetime) settings.maxLifetime = EditorGUILayout.FloatField("Maximum Lifetime", settings.maxLifetime);
                settings.disableTrails = EditorGUILayout.Toggle("Disable Trails", settings.disableTrails);
                settings.disableCollision = EditorGUILayout.Toggle("Disable Collision", settings.disableCollision);
                settings.disableNoise = EditorGUILayout.Toggle("Disable Noise", settings.disableNoise);
                settings.disableLights = EditorGUILayout.Toggle("Disable Particle Lights", settings.disableLights);
                settings.disableShadows = EditorGUILayout.Toggle("Disable Shadows", settings.disableShadows);
                settings.disableSubEmitters = EditorGUILayout.Toggle("Disable Sub Emitters", settings.disableSubEmitters);
                if (EditorGUI.EndChangeCheck()) settings.particlePreset = VRParticlePreset.Custom;
                EditorGUI.indentLevel--;
            }
            GUILayout.Space(4);
            if (GUILayout.Button("OPTIMIZE PARTICLES", GUILayout.Height(34))) OptimizeParticles();
            EditorGUILayout.EndVertical();

            GUILayout.Space(6);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("SCENE CHECKS", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Checks lights and meshes in currently loaded Hierarchy scenes.", EditorStyles.wordWrappedMiniLabel);
            if (GUILayout.Button("OPTIMIZE LIGHTS (SCAN HIERARCHY)", GUILayout.Height(30))) Scan(VRCategory.Light);
            if (GUILayout.Button("CHECK SCENE MESHES", GUILayout.Height(30))) Scan(VRCategory.Mesh);
            EditorGUILayout.EndVertical();

            GUILayout.Space(6);
            EditorGUILayout.BeginVertical(EditorStyles.helpBox);
            EditorGUILayout.LabelField("PROJECT SCAN", EditorStyles.boldLabel);
            EditorGUILayout.LabelField("Project textures and particle prefabs; lights, meshes and particles in loaded scenes.", EditorStyles.wordWrappedMiniLabel);
            if (GUILayout.Button("SCAN FOR PROBLEMS", GUILayout.Height(34))) Scan(null);
            EditorGUILayout.EndVertical();
            if (EditorGUI.EndChangeCheck()) { settings.Sanitize(); settings.Save(); preview = null; }
            GUILayout.Space(8);
            EditorGUILayout.HelpBox(summary, MessageType.Info);
            DrawResults();
            GUILayout.Space(12);
            EditorGUILayout.LabelField("FISHHWB | DED ZED  •  This package is free", EditorStyles.centeredGreyMiniLabel);
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("WEBSITE")) Application.OpenURL("https://fishhwb.github.io/");
            if (GUILayout.Button("DISCORD")) Application.OpenURL("https://discord.gg/wZGxxkk4Jg");
            if (GUILayout.Button("PATREON")) Application.OpenURL("https://www.patreon.com/cw/DedZed");
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.EndScrollView();
        }

        void DrawPreview()
        {
            if (preview == null) return;
            EditorGUILayout.LabelField("TEXTURE PREVIEW (current → proposed PC / Android / iOS)", EditorStyles.boldLabel);
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("INCLUDE ALL")) foreach (var item in preview) item.Include = true;
            if (GUILayout.Button("EXCLUDE ALL")) foreach (var item in preview) item.Include = false;
            EditorGUILayout.EndHorizontal();
            foreach (var item in preview)
            {
                item.Include = EditorGUILayout.ToggleLeft(item.Path + (item.Changed ? "" : " (unchanged)"), item.Include);
                EditorGUILayout.LabelField("    " + item.Before[0] + " → " + item.After[0] + " / " + item.Before[1] + " → " + item.After[1] + " / " + item.Before[2] + " → " + item.After[2], EditorStyles.miniLabel);
            }
            if (GUILayout.Button("APPLY SELECTED", GUILayout.Height(32)))
            {
                int changed = 0, excluded = 0, unchanged = 0, failed = 0;
                bool cancelled = false;
                try
                {
                    for (int i = 0; i < preview.Count; i++)
                    {
                        if (EditorUtility.DisplayCancelableProgressBar("Apply Texture Changes", preview[i].Path, (float)i / preview.Count)) { cancelled = true; break; }
                        var item = preview[i];
                        if (!item.Include) { excluded++; continue; }
                        if (!item.Changed) { unchanged++; continue; }
                        try { if (VRTextureOptimizer.Optimize(item.Path, settings)) changed++; else unchanged++; }
                        catch (Exception error) { failed++; Debug.LogError("VR Optimizer: " + item.Path + " — " + error); }
                    }
                }
                finally { EditorUtility.ClearProgressBar(); }
                summary = (cancelled ? "Cancelled. " : "Complete. ") + "Changed: " + changed + ", unchanged: " + unchanged + ", excluded: " + excluded + ", failed: " + failed + ". Rescan to verify.";
                preview = null;
            }
        }

        void OptimizeAvatarParticles()
        {
            if (!VRAvatarWorkflow.EditableRoot(avatar)) return;
            var particles = avatar.GetComponentsInChildren<ParticleSystem>(true);
            int changed = 0;
            int group = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName("Optimize Avatar Particles");
            foreach (var particle in particles)
                if (VRParticleOptimizer.Optimize(particle, settings)) changed++;
            Undo.CollapseUndoOperations(group);
            summary = "Avatar particles: " + particles.Length + " found, " + changed + " changed, " + (particles.Length - changed) + " already at preset. Save the scene when satisfied; Undo restores changes.";
        }

        void DrawResults()
        {
            if (results.Count == 0) return;
            int critical = 0, warning = 0, info = 0;
            foreach (var issue in results)
                if (issue.Severity == VRSeverity.Critical) critical++;
                else if (issue.Severity == VRSeverity.Warning) warning++;
                else info++;
            EditorGUILayout.LabelField("RESULTS  •  " + critical + " critical   " + warning + " warnings   " + info + " info", EditorStyles.boldLabel);
            foreach (var issue in results)
            {
                EditorGUILayout.BeginVertical(EditorStyles.helpBox);
                EditorGUILayout.LabelField(issue.Severity + "  •  " + issue.Category, EditorStyles.boldLabel);
                EditorGUILayout.LabelField(issue.Message, EditorStyles.wordWrappedLabel);
                if (!string.IsNullOrEmpty(issue.AssetPath)) EditorGUILayout.LabelField(issue.AssetPath, EditorStyles.miniLabel);
                EditorGUILayout.BeginHorizontal();
                using (new EditorGUI.DisabledScope(!issue.Target))
                    if (GUILayout.Button("SELECT", GUILayout.Width(90))) { Selection.activeObject = issue.Target; EditorGUIUtility.PingObject(issue.Target); }
                if (issue.CanOptimize && (issue.Category == VRCategory.Texture || string.IsNullOrEmpty(issue.AssetPath)) &&
                    GUILayout.Button(issue.Category == VRCategory.Light ? "REVIEW & OPTIMIZE" : "OPTIMIZE", GUILayout.Width(150))) OptimizeIssue(issue);
                EditorGUILayout.EndHorizontal();
                EditorGUILayout.EndVertical();
            }
        }

        void Scan(VRCategory? category)
        {
            results = VRProjectScanner.Scan(settings, category, out bool cancelled);
            summary = (cancelled ? "Scan cancelled. Partial results: " : "Scan complete. Issues: ") + results.Count;
        }
        void OptimizeTextures()
        {
            var guids = AssetDatabase.FindAssets("t:Texture", new[] { "Assets" });
            int scanned = 0, changed = 0;
            bool cancelled = false;
            try
            {
                for (int i = 0; i < guids.Length; i++)
                {
                    if (EditorUtility.DisplayCancelableProgressBar("Optimize Textures", (i + 1) + "/" + guids.Length, (float)i / guids.Length)) { cancelled = true; break; }
                    var path = AssetDatabase.GUIDToAssetPath(guids[i]);
                    if (!(AssetImporter.GetAtPath(path) is TextureImporter)) continue;
                    scanned++;
                    if (VRTextureOptimizer.Optimize(path, settings)) changed++;
                }
            }
            finally { EditorUtility.ClearProgressBar(); }
            summary = (cancelled ? "Cancelled. Partial results: " : "TEXTURE OPTIMIZATION COMPLETE. ") +
                "Scanned: " + scanned + ", changed: " + changed + ", already optimized: " + (scanned - changed) +
                ". Caps PC/Android/iOS: " + settings.pc + "/" + settings.android + "/" + settings.ios + ".";
        }
        void OptimizeParticles()
        {
            int scanned = 0, changed = 0;
            bool cancelled = false;
            try
            {
                var particles = new List<ParticleSystem>(VRProjectScanner.SceneObjects<ParticleSystem>());
                for (int i = 0; i < particles.Count; i++)
                {
                    if (EditorUtility.DisplayCancelableProgressBar("Optimize Particles", (i + 1) + "/" + particles.Count, particles.Count == 0 ? 1 : (float)i / particles.Count)) { cancelled = true; break; }
                    scanned++;
                    if (VRParticleOptimizer.Optimize(particles[i], settings)) changed++;
                }
            }
            finally { EditorUtility.ClearProgressBar(); }
            summary = (cancelled ? "Cancelled. Partial results: " : "PARTICLE OPTIMIZATION COMPLETE. ") + "Loaded scene systems scanned: " + scanned + ", changed: " + changed + ". Save scenes to persist; use Undo to revert.";
        }
        void OptimizeIssue(VRIssue issue)
        {
            bool changed = false;
            if (issue.Category == VRCategory.Texture && !string.IsNullOrEmpty(issue.AssetPath)) changed = VRTextureOptimizer.Optimize(issue.AssetPath, settings);
            else if (issue.Category == VRCategory.Particle && issue.Target is ParticleSystem p && string.IsNullOrEmpty(issue.AssetPath)) changed = VRParticleOptimizer.Optimize(p, settings);
            else if (issue.Category == VRCategory.Light && string.IsNullOrEmpty(issue.AssetPath) && issue.Target is Light light &&
                     EditorUtility.DisplayDialog("Optimize " + light.name, "Disable shadows on this light? You can undo the change.", "Optimize", "Cancel"))
                changed = VRLightOptimizer.Optimize(light, settings);
            summary = changed ? "Optimized selected item. Scan again to update results." : "No settings changed.";
        }
    }
}
