using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FISHHWB.VROptimizer
{
    internal static class VRUnusedAssetCleaner
    {
        internal static string ExportDryRunReport(string folder)
        {
            if (!ValidFolder(folder))
                return "Unused asset report: choose an existing folder under Assets first.";

            var candidates = FindUnused(folder, out int protectedAssets, out int unsupported);
            string filename = EditorUtility.SaveFilePanel(
                "Export unused asset dry-run report", "", "OptimizeYourProject-UnusedAssets.csv", "csv");
            if (string.IsNullOrEmpty(filename))
                return "Unused asset report cancelled. No assets were modified.";

            try
            {
                using (var writer = new StreamWriter(filename, false, System.Text.Encoding.UTF8))
                {
                    writer.WriteLine("Status,Asset Path");
                    foreach (string path in candidates)
                        writer.WriteLine("\"Candidate\",\"" + path.Replace("\"", "\"\"") + "\"");
                    writer.WriteLine("\"Protected assets (dynamic or user)\",\"" + protectedAssets + "\"");
                    writer.WriteLine("\"Unsupported asset types\",\"" + unsupported + "\"");
                    writer.WriteLine("\"Caution\",\"Runtime-only references cannot always be detected\"");
                }
                return "Unused asset dry-run report exported: " + candidates.Count +
                       " candidates; " + protectedAssets + " protected assets; " +
                       unsupported + " unsupported. Nothing deleted. File: " + filename;
            }
            catch (Exception error)
            {
                Debug.LogWarning("Optimize Your Project report export failed: " + error);
                return "Unused asset report export failed: " + error.Message;
            }
        }

        internal static string DeleteUnused(string folder)
        {
            if (!ValidFolder(folder))
                return "Unused asset cleanup: choose an existing folder under Assets first.";

            // Unsaved scene references are absent from serialized dependency scans.
            if (HasUnsavedOpenScenes())
                return "Unused asset cleanup stopped: save or discard changes in open scenes first. Nothing was deleted.";

            var candidates = FindUnused(folder, out int protectedAssets, out int unsupported);
            if (candidates.Count == 0)
                return "Unused asset cleanup: no conservative deletion candidates found. " +
                       protectedAssets + " protected assets, " + unsupported + " unsupported asset types ignored.";

            var reviewedIdentities = CandidateIdentities(candidates);
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

            // Re-check immediately before permanent deletion. The folder or dependency
            // graph may have changed while the two confirmation dialogs were open.
            if (HasUnsavedOpenScenes())
                return "Unused asset cleanup stopped: open scenes now have unsaved changes. Nothing was deleted.";
            var refreshed = FindUnused(folder, out _, out _);
            if (!CandidateSetUnchanged(candidates, refreshed) || !CandidateIdentitiesUnchanged(reviewedIdentities))
                return "Unused asset cleanup stopped: the candidate list changed during review. Run it again. Nothing was deleted.";

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

        internal static List<string> FindUnused(string folder, out int protectedAssets, out int unsupported)
        {
            protectedAssets = 0;
            unsupported = 0;
            var candidates = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

            foreach (var guid in AssetDatabase.FindAssets(string.Empty, new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (string.IsNullOrEmpty(path) || AssetDatabase.IsValidFolder(path) || !path.StartsWith("Assets/", StringComparison.Ordinal))
                    continue;

                if (ProtectedDynamicPath(path) || HasExternalUsageMarker(path) || VRImportHistory.instance.Protected(path))
                {
                    protectedAssets++;
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
                // Serialized package assets can also depend on assets in this project.
                if (string.IsNullOrEmpty(owner) ||
                    !(owner.StartsWith("Assets/", StringComparison.Ordinal) ||
                      owner.StartsWith("Packages/", StringComparison.Ordinal)) ||
                    AssetDatabase.IsValidFolder(owner))
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

        internal static bool CandidateSetUnchanged(IList<string> reviewed, IList<string> current)
        {
            if (reviewed == null || current == null || reviewed.Count != current.Count)
                return false;
            var previous = new HashSet<string>(reviewed, StringComparer.OrdinalIgnoreCase);
            return previous.Count == reviewed.Count && previous.SetEquals(current);
        }

        internal static Dictionary<string, string> CandidateIdentities(IList<string> candidates)
        {
            var identities = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
            foreach (string path in candidates)
                identities[path] = AssetDatabase.AssetPathToGUID(path);
            return identities;
        }

        internal static bool CandidateIdentitiesUnchanged(IDictionary<string, string> reviewed)
        {
            if (reviewed == null) return false;
            foreach (var item in reviewed)
                if (string.IsNullOrEmpty(item.Value) ||
                    !string.Equals(item.Value, AssetDatabase.AssetPathToGUID(item.Key), StringComparison.Ordinal))
                    return false;
            return true;
        }

        static bool HasUnsavedOpenScenes()
        {
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                var scene = SceneManager.GetSceneAt(i);
                if (scene.IsValid() && scene.isDirty)
                    return true;
            }
            return false;
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
