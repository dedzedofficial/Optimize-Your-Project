using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FISHHWB.VROptimizer
{
    internal interface IVRScanner { void ScanAsset(string path, VRSettings settings, List<VRIssue> issues); void ScanScene(VRSettings settings, List<VRIssue> issues); }

    internal static class VRProjectScanner
    {
        static readonly IVRScanner[] Modules = { new VRTextureScanner(), new VRParticleScanner(), new VRLightScanner(), new VRMeshScanner() };
        public static List<VRIssue> Scan(VRSettings settings, VRCategory? only, out bool cancelled)
        {
            settings.Sanitize();
            var issues = new List<VRIssue>();
            cancelled = false;
            var paths = new List<string>();
            if (only != VRCategory.Light && only != VRCategory.Mesh)
            foreach (var guid in AssetDatabase.FindAssets("t:Texture t:Prefab"))
            {
                var path = AssetDatabase.GUIDToAssetPath(guid);
                if (path.StartsWith("Assets/", StringComparison.Ordinal) && !paths.Contains(path)) paths.Add(path);
            }
            try
            {
                for (int i = 0; i < paths.Count; i++)
                {
                    if (EditorUtility.DisplayCancelableProgressBar("FISHHWB VR Optimizer", "Scanning assets " + (i + 1) + "/" + paths.Count, paths.Count == 0 ? 1 : (float)i / paths.Count)) { cancelled = true; break; }
                    foreach (var module in Modules) if (!only.HasValue || Matches(module, only.Value)) module.ScanAsset(paths[i], settings, issues);
                }
                if (!cancelled)
                    foreach (var module in Modules) if (!only.HasValue || Matches(module, only.Value)) module.ScanScene(settings, issues);
            }
            finally { EditorUtility.ClearProgressBar(); }
            return issues;
        }
        static bool Matches(IVRScanner module, VRCategory category)
        {
            return category == VRCategory.Texture && module is VRTextureScanner ||
                   category == VRCategory.Particle && module is VRParticleScanner ||
                   category == VRCategory.Light && module is VRLightScanner ||
                   category == VRCategory.Mesh && module is VRMeshScanner;
        }
        internal static IEnumerable<T> SceneObjects<T>() where T : Component
        {
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                var scene = SceneManager.GetSceneAt(i);
                if (!scene.isLoaded) continue;
                foreach (var root in scene.GetRootGameObjects())
                    foreach (var component in root.GetComponentsInChildren<T>(true)) yield return component;
            }
        }
        internal static IEnumerable<T> PrefabObjects<T>(string path) where T : Component
        {
            if (!path.EndsWith(".prefab", StringComparison.OrdinalIgnoreCase)) yield break;
            var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
            if (prefab) foreach (var component in prefab.GetComponentsInChildren<T>(true)) yield return component;
        }
    }
}
