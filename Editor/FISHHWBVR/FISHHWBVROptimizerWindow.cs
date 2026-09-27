using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class FISHHWBVROptimizerWindow : EditorWindow
    {
        VRSettings settings;
        List<VRIssue> results = new List<VRIssue>();
        Vector2 scroll;
        string summary = "Ready. Scans include imported assets and currently loaded scenes.";

        [MenuItem("FISHHWB/VR Optimizer")]
        static void Open() { GetWindow<FISHHWBVROptimizerWindow>("VR Optimizer").minSize = new Vector2(480, 560); }
        void OnEnable() { settings = VRSettings.Load(); }

        void OnGUI()
        {
            if (settings == null) settings = VRSettings.Load();
            scroll = EditorGUILayout.BeginScrollView(scroll);
            GUILayout.Space(10);
            var title = new GUIStyle(EditorStyles.boldLabel) { fontSize = 19, alignment = TextAnchor.MiddleCenter };
            GUILayout.Label("FISHHWB VR OPTIMIZER", title);
            GUILayout.Label("v0.6.3", new GUIStyle(EditorStyles.centeredGreyMiniLabel));
            GUILayout.Space(12);
            EditorGUI.BeginChangeCheck();
            settings.target = (VRTarget)EditorGUILayout.EnumPopup("Target Platform", settings.target);
            var preset = (VRTexturePreset)EditorGUILayout.EnumPopup("Texture Preset", settings.texturePreset);
            if (preset != settings.texturePreset) settings.SetTexturePreset(preset);
            EditorGUILayout.LabelField("Platform maximum sizes", EditorStyles.boldLabel);
            EditorGUI.BeginChangeCheck();
            settings.pc = EditorGUILayout.IntField("PC / Standalone", settings.pc);
            settings.android = EditorGUILayout.IntField("Android / Quest", settings.android);
            settings.ios = EditorGUILayout.IntField("iOS", settings.ios);
            if (EditorGUI.EndChangeCheck()) settings.texturePreset = VRTexturePreset.Custom;
            settings.overridePC = EditorGUILayout.Toggle("Override PC", settings.overridePC);
            settings.overrideAndroid = EditorGUILayout.Toggle("Override Android", settings.overrideAndroid);
            settings.overrideIOS = EditorGUILayout.Toggle("Override iOS", settings.overrideIOS);
            settings.compression = EditorGUILayout.Toggle("Compress", settings.compression);
            settings.quality = EditorGUILayout.IntSlider("Compression Quality", settings.quality, 0, 100);
            settings.crunch = EditorGUILayout.Toggle("Crunch (supported types)", settings.crunch);
            settings.changeMipmaps = EditorGUILayout.Toggle("Change Color Mipmaps", settings.changeMipmaps);
            if (settings.changeMipmaps) settings.mipmaps = EditorGUILayout.Toggle("Generate Mipmaps", settings.mipmaps);
            settings.changeFilter = EditorGUILayout.Toggle("Change Filter Mode", settings.changeFilter);
            if (settings.changeFilter) settings.filter = (FilterMode)EditorGUILayout.EnumPopup("Filter Mode", settings.filter);
            settings.changeAniso = EditorGUILayout.Toggle("Change Anisotropy", settings.changeAniso);
            if (settings.changeAniso) settings.aniso = EditorGUILayout.IntSlider("Anisotropy", settings.aniso, 0, 16);
            GUILayout.Space(8);
            var particlePreset = (VRParticlePreset)EditorGUILayout.EnumPopup("Particle Preset", settings.particlePreset);
            if (particlePreset != settings.particlePreset) settings.SetParticlePreset(particlePreset);
            EditorGUI.BeginChangeCheck();
            settings.capParticles = EditorGUILayout.Toggle("Cap Particle Count", settings.capParticles);
            if (settings.capParticles) settings.maxParticles = EditorGUILayout.IntField("Maximum Particles", settings.maxParticles);
            settings.capLifetime = EditorGUILayout.Toggle("Cap Constant Lifetime", settings.capLifetime);
            if (settings.capLifetime) settings.maxLifetime = EditorGUILayout.FloatField("Maximum Lifetime", settings.maxLifetime);
            settings.disableTrails = EditorGUILayout.Toggle("Disable Trails", settings.disableTrails);
            settings.disableCollision = EditorGUILayout.Toggle("Disable Collision", settings.disableCollision);
            settings.disableNoise = EditorGUILayout.Toggle("Disable Noise", settings.disableNoise);
            settings.disableLights = EditorGUILayout.Toggle("Disable Particle Lights", settings.disableLights);
            settings.disableShadows = EditorGUILayout.Toggle("Disable Particle Shadows", settings.disableShadows);
            settings.disableSubEmitters = EditorGUILayout.Toggle("Disable Sub Emitters", settings.disableSubEmitters);
            if (EditorGUI.EndChangeCheck()) settings.particlePreset = VRParticlePreset.Custom;
            GUILayout.Space(8);
            settings.capLightRange = EditorGUILayout.Toggle("Cap Confirmed Light Range", settings.capLightRange);
            if (settings.capLightRange) settings.maxLightRange = EditorGUILayout.FloatField("Maximum Light Range", settings.maxLightRange);
            if (EditorGUI.EndChangeCheck()) { settings.Sanitize(); settings.Save(); }

            GUILayout.Space(12);
            if (GUILayout.Button("OPTIMIZE TEXTURES", GUILayout.Height(32))) OptimizeTextures();
            if (GUILayout.Button("OPTIMIZE PARTICLES", GUILayout.Height(32))) OptimizeParticles();
            if (GUILayout.Button("OPTIMIZE LIGHTS (AUDIT)", GUILayout.Height(32))) Scan(VRCategory.Light);
            if (GUILayout.Button("SCAN FOR PROBLEMS", GUILayout.Height(32))) Scan(null);
            if (GUILayout.Button("CHECK MESHES", GUILayout.Height(32))) Scan(VRCategory.Mesh);
            EditorGUILayout.HelpBox(summary, MessageType.Info);
            if (results.Count > 0)
            {
                int critical = 0, warning = 0, info = 0;
                foreach (var issue in results) { if (issue.Severity == VRSeverity.Critical) critical++; else if (issue.Severity == VRSeverity.Warning) warning++; else info++; }
                EditorGUILayout.LabelField("RESULTS  |  Critical: " + critical + "   Warnings: " + warning + "   Info: " + info, EditorStyles.boldLabel);
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
            GUILayout.Space(12);
            EditorGUILayout.LabelField("FISHHWB | DED ZED     •     This package is free.", EditorStyles.centeredGreyMiniLabel);
            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button("WEBSITE")) Application.OpenURL("https://fishhwb.github.io/");
            if (GUILayout.Button("DISCORD")) Application.OpenURL("https://discord.gg/wZGxxkk4Jg");
            if (GUILayout.Button("PATREON")) Application.OpenURL("https://www.patreon.com/cw/DedZed");
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.EndScrollView();
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
            // Scene objects and the current Prefab Stage support the normal Unity Undo workflow.
            // Prefab assets elsewhere are reported by the scanner and edited in Prefab Mode.
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
            summary = (cancelled ? "Cancelled. Partial results: " : "PARTICLE OPTIMIZATION COMPLETE. ") + "Loaded scene systems scanned: " + scanned + ", changed: " + changed + ". Save scenes to persist; use Undo to revert. Open prefab assets in Prefab Mode to edit safely.";
        }
        void OptimizeIssue(VRIssue issue)
        {
            bool changed = false;
            if (issue.Category == VRCategory.Texture && !string.IsNullOrEmpty(issue.AssetPath)) changed = VRTextureOptimizer.Optimize(issue.AssetPath, settings);
            else if (issue.Category == VRCategory.Particle && issue.Target is ParticleSystem p && string.IsNullOrEmpty(issue.AssetPath)) changed = VRParticleOptimizer.Optimize(p, settings);
            else if (issue.Category == VRCategory.Light && string.IsNullOrEmpty(issue.AssetPath) && issue.Target is Light light &&
                     EditorUtility.DisplayDialog("Optimize " + light.name, "Disable shadows on this light" + (settings.capLightRange ? " and cap its range" : "") + "? You can undo the change.", "Optimize", "Cancel"))
                changed = VRLightOptimizer.Optimize(light, settings);
            summary = changed ? "Optimized selected item. Scan again to update results." : "No settings changed. For prefab particles, open the prefab in Prefab Mode first.";
        }
    }
}
