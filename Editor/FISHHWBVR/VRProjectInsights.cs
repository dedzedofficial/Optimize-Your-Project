using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRProjectInsights
    {
        internal static List<VRIssue> LargestTextures(string folder, int limit = 20)
        {
            var rows = new List<Tuple<long, Texture, string>>();
            foreach (var guid in AssetDatabase.FindAssets("t:Texture", new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (string.IsNullOrEmpty(path) || !path.StartsWith("Assets/", StringComparison.Ordinal))
                    continue;
                var texture = AssetDatabase.LoadAssetAtPath<Texture>(path);
                if (!texture) continue;
                rows.Add(Tuple.Create((long)texture.width * texture.height, texture, path));
            }

            rows.Sort((a, b) => b.Item1.CompareTo(a.Item1));
            var issues = new List<VRIssue>();
            int count = Mathf.Min(limit, rows.Count);
            for (int i = 0; i < count; i++)
            {
                var row = rows[i];
                issues.Add(new VRIssue(
                    i < 5 ? VRSeverity.Warning : VRSeverity.Info,
                    VRCategory.Texture,
                    row.Item2.name + ": " + row.Item2.width + " x " + row.Item2.height + " source texture",
                    row.Item2,
                    row.Item3,
                    true));
            }
            return issues;
        }

        internal static List<VRIssue> ReadWriteReview(string folder)
        {
            var issues = new List<VRIssue>();

            foreach (var guid in AssetDatabase.FindAssets("t:Texture", new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null || !importer.isReadable) continue;
                var texture = AssetDatabase.LoadAssetAtPath<Texture>(path);
                issues.Add(new VRIssue(
                    VRSeverity.Warning,
                    VRCategory.Texture,
                    (texture ? texture.name : path) + ": Read/Write enabled. Review runtime CPU access before disabling it.",
                    texture,
                    path,
                    true));
            }

            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var importer = AssetImporter.GetAtPath(path) as ModelImporter;
                if (importer == null || !importer.isReadable) continue;
                var asset = AssetDatabase.LoadMainAssetAtPath(path);
                issues.Add(new VRIssue(
                    VRSeverity.Warning,
                    VRCategory.Mesh,
                    asset.name + ": model Read/Write enabled. Review scripts, non-uniform scaling and runtime mesh access before disabling it.",
                    asset,
                    path,
                    true));
            }

            return issues;
        }

        internal static List<VRIssue> HeavyMeshes(GameObject root, int triangleThreshold = 100000)
        {
            var issues = new List<VRIssue>();
            var seen = new HashSet<Mesh>();

            if (root)
            {
                foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
                    Add(filter.sharedMesh, filter.gameObject);
                foreach (var skin in root.GetComponentsInChildren<SkinnedMeshRenderer>(true))
                    Add(skin.sharedMesh, skin.gameObject);
            }
            else
            {
                foreach (var filter in VRProjectScanner.SceneObjects<MeshFilter>())
                    Add(filter.sharedMesh, filter.gameObject);
                foreach (var skin in VRProjectScanner.SceneObjects<SkinnedMeshRenderer>())
                    Add(skin.sharedMesh, skin.gameObject);
            }

            issues.Sort((a, b) => string.CompareOrdinal(a.Message, b.Message));
            return issues;

            void Add(Mesh mesh, GameObject owner)
            {
                if (!mesh || !owner || !seen.Add(mesh)) return;
                int triangles = 0;
                for (int i = 0; i < mesh.subMeshCount; i++)
                    if (mesh.GetTopology(i) == MeshTopology.Triangles)
                        triangles += (int)(mesh.GetIndexCount(i) / 3);
                if (triangles < triangleThreshold) return;

                issues.Add(new VRIssue(
                    triangles >= triangleThreshold * 2 ? VRSeverity.Critical : VRSeverity.Warning,
                    VRCategory.Mesh,
                    owner.name + " / " + mesh.name + ": " + triangles.ToString("N0") + " triangles, " + mesh.vertexCount.ToString("N0") + " vertices",
                    owner));
            }
        }

        internal static string FolderFromSelection(string fallback)
        {
            var selected = Selection.activeObject;
            if (!selected) return fallback;
            string path = AssetDatabase.GetAssetPath(selected);
            if (string.IsNullOrEmpty(path) || !path.StartsWith("Assets", StringComparison.Ordinal))
                return fallback;
            if (AssetDatabase.IsValidFolder(path)) return path;
            int slash = path.LastIndexOf('/');
            return slash > 0 ? path.Substring(0, slash) : "Assets";
        }
    }
}
