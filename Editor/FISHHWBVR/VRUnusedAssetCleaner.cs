using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRUnusedAssetCleaner
    {
        internal static string DeleteUnused(string folder)
        {
            if (!ValidFolder(folder))
                return "Unused asset cleanup: choose an existing folder under Assets first.";

            var candidates = FindUnused(folder, out int protectedDynamic, out int unsupported);
            if (candidates.Count == 0)
                return "Unused asset cleanup: no conservative deletion candidates found. " +
                       protectedDynamic + " dynamic-use assets protected, " + unsupported + " unsupported asset types ignored.";

            string preview = BuildPreview(candidates, 12);
            if (!EditorUtility.DisplayDialog(
                "Review unused asset cleanup",
                "Found " + candidates.Count + " conservatively unreferenced asset(s) under:\n" + folder +
                "\n\n" + preview +
                "\n\nImportant: Unity cannot prove references created at runtime from strings, reflection, custom loaders or external code. " +
                "Resources, StreamingAssets, Editor, Plugins, Gizmos, Addressable-related paths, labelled assets and AssetBundle assets are protected automatically.\n\n" +
                "Continue to the permanent-delete warning?",
                "Continue",
                "Cancel"))
                return "Unused asset cleanup cancelled. Nothing was deleted.";

            if (!EditorUtility.DisplayDialog(
                "PERMANENT DELETE - no Unity Undo",
                "Delete " + candidates.Count + " asset file(s) permanently from the project?\n\n" +
                "THIS CANNOT BE UNDONE WITH UNITY UNDO. Use source control or a backup if you may need these files later.\n\n" +
                "Only press Permanent Delete if you reviewed the candidates and understand that runtime-only references cannot always be detected.",
                "Permanent Delete",
                "Cancel"))
                return "Unused asset cleanup cancelled at the final warning. Nothing was deleted.";

            int deleted = 0;
            int failed = 0;
            AssetDatabase.StartAssetEditing();
            try
            {
                foreach (var path in candidates)
                {
                    try
                    {
                        if (AssetDatabase.DeleteAsset(path)) deleted++;
                        else failed++;
                    }
                    catch (Exception error)
                    {
                        failed++;
                        Debug.LogWarning("Optimize Your Project could not delete " + path + ": " + error.Message);
                    }
                }
            }
            finally
            {
                AssetDatabase.StopAssetEditing();
                AssetDatabase.Refresh();
            }

            return "Unused asset cleanup complete: " + deleted + " permanently deleted, " + failed +
                   " failed. This action does not use Unity Undo.";
        }

        internal static List<string> FindUnused(string folder, out int protectedDynamic, out int unsupported)
        {
            protectedDynamic = 0;
            unsupported = 0;
            var candidates = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

            foreach (var guid in AssetDatabase.FindAssets(string.Empty, new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (string.IsNullOrEmpty(path) || AssetDatabase.IsValidFolder(path) || !path.StartsWith("Assets/", StringComparison.Ordinal))
                    continue;

                if (ProtectedDynamicPath(path) || HasExternalUsageMarker(path))
                {
                    protectedDynamic++;
                    continue;
                }

                var asset = AssetDatabase.LoadMainAssetAtPath(path);
                if (!SafeCandidateType(asset))
                {
                    unsupported++;
                    continue;
                }

                candidates.Add(path);
            }

            if (candidates.Count == 0)
                return new List<string>();

            var referenced = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var owner in AssetDatabase.GetAllAssetPaths())
            {
                if (string.IsNullOrEmpty(owner) || !owner.StartsWith("Assets/", StringComparison.Ordinal) || AssetDatabase.IsValidFolder(owner))
                    continue;

                foreach (var dependency in AssetDatabase.GetDependencies(owner, false))
                {
                    if (!string.Equals(owner, dependency, StringComparison.OrdinalIgnoreCase) && candidates.Contains(dependency))
                        referenced.Add(dependency);
                }
            }

            candidates.ExceptWith(referenced);
            var result = new List<string>(candidates);
            result.Sort(StringComparer.OrdinalIgnoreCase);
            return result;
        }

        static bool SafeCandidateType(UnityEngine.Object asset)
        {
            return asset is Texture || asset is Material || asset is AudioClip ||
                   asset is AnimationClip || asset is PhysicMaterial || asset is PhysicsMaterial2D;
        }

        static bool HasExternalUsageMarker(string path)
        {
            var importer = AssetImporter.GetAtPath(path);
            if (importer != null && !string.IsNullOrEmpty(importer.assetBundleName))
                return true;

            var asset = AssetDatabase.LoadMainAssetAtPath(path);
            return asset != null && AssetDatabase.GetLabels(asset).Length > 0;
        }

        static bool ProtectedDynamicPath(string path)
        {
            string normalized = path.Replace('\\', '/');
            return Segment(normalized, "Resources") ||
                   Segment(normalized, "StreamingAssets") ||
                   Segment(normalized, "Editor") ||
                   Segment(normalized, "Plugins") ||
                   Segment(normalized, "Gizmos") ||
                   Segment(normalized, "AddressableAssetsData") ||
                   normalized.IndexOf("/Addressables/", StringComparison.OrdinalIgnoreCase) >= 0 ||
                   normalized.IndexOf("/Editor Default Resources/", StringComparison.OrdinalIgnoreCase) >= 0;
        }

        static bool Segment(string path, string segment)
        {
            return path.StartsWith("Assets/" + segment + "/", StringComparison.OrdinalIgnoreCase) ||
                   path.IndexOf("/" + segment + "/", StringComparison.OrdinalIgnoreCase) >= 0;
        }

        static bool ValidFolder(string folder)
        {
            return folder == "Assets" ||
                   !string.IsNullOrEmpty(folder) && folder.StartsWith("Assets/", StringComparison.Ordinal) && AssetDatabase.IsValidFolder(folder);
        }

        static string BuildPreview(List<string> paths, int maximum)
        {
            var lines = new List<string>();
            int count = Mathf.Min(maximum, paths.Count);
            for (int i = 0; i < count; i++)
                lines.Add("• " + paths[i]);
            if (paths.Count > count)
                lines.Add("• ...and " + (paths.Count - count) + " more");
            return string.Join("\n", lines);
        }
    }
}
