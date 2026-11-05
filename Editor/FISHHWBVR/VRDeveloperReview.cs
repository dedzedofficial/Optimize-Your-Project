// Developer quality-of-life checks are intentionally read-only.
// All results are recommendations, not automated runtime-performance claims.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace FISHHWB.VROptimizer
{
    internal static class VRDeveloperReview
    {
        internal static List<VRIssue> Prioritize(IEnumerable<VRIssue> input)
        {
            var list = new List<VRIssue>(input ?? Enumerable.Empty<VRIssue>());
            list.Sort((a, b) =>
            {
                int severity = b.Severity.CompareTo(a.Severity);
                if (severity != 0) return severity;
                int actionable = b.CanOptimize.CompareTo(a.CanOptimize);
                if (actionable != 0) return actionable;
                int category = a.Category.CompareTo(b.Category);
                return category != 0 ? category : string.CompareOrdinal(a.Message, b.Message);
            });
            return list;
        }

        internal static List<VRIssue> TextureWaste(string folder)
        {
            var issues = new List<VRIssue>();
            if (!AssetDatabase.IsValidFolder(folder)) return issues;
            var hashes = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (var guid in AssetDatabase.FindAssets("t:Texture", new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (!path.StartsWith("Assets/", StringComparison.Ordinal)) continue;
                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                var texture = AssetDatabase.LoadAssetAtPath<Texture>(path);
                if (!importer || !texture || importer.textureShape != TextureImporterShape.Texture2D) continue;

                if (importer.textureType == TextureImporterType.Default
                    && !importer.mipmapEnabled && Mathf.Max(texture.width, texture.height) >= 2048)
                    issues.Add(new VRIssue(
                        VRSeverity.Info, VRCategory.Texture,
                        "Large texture with mipmaps disabled. Check if it is displayed at different distances.",
                        texture, path));
                if (importer.textureType == TextureImporterType.NormalMap && importer.sRGBTexture)
                    issues.Add(new VRIssue(
                        VRSeverity.Warning, VRCategory.Texture,
                        "Normal map uses sRGB sampling. Verify normal-map import settings before changing it.",
                        texture, path));
                if (importer.textureType == TextureImporterType.Default
                    && importer.alphaSource != TextureImporterAlphaSource.None
                    && !importer.DoesSourceTextureHaveAlpha())
                    issues.Add(new VRIssue(
                        VRSeverity.Info, VRCategory.Texture,
                        "Alpha source requested, but source texture has no alpha. Review before removing alpha support.",
                        texture, path));
                // Hash source files only when reasonably small, never rewrite imports.
                try
                {
                    var file = new FileInfo(path);
                    if (!file.Exists || file.Length > 32L * 1024 * 1024) continue;
                    string hash;
                    using (var stream = file.OpenRead())
                    using (var sha = SHA256.Create())
                        hash = Convert.ToBase64String(sha.ComputeHash(stream));
                    if (hashes.TryGetValue(hash, out var original))
                        issues.Add(new VRIssue(
                            VRSeverity.Warning, VRCategory.Texture,
                            "Exact duplicate texture file. Review references before consolidation: " + original,
                            texture, path));
                    else hashes[hash] = path;
                }
                catch (IOException) { /* File unavailable: skip hash only. */ }
                catch (UnauthorizedAccessException) { /* Skip protected source. */ }
            }
            return Prioritize(issues);
        }

        internal static List<VRIssue> BuildReadiness(string folder)
        {
            var issues = new List<VRIssue>();
            if (!AssetDatabase.IsValidFolder(folder)) return issues;

            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var importer = AssetImporter.GetAtPath(path) as ModelImporter;
                if (importer == null) continue;
                var model = AssetDatabase.LoadMainAssetAtPath(path);
                if (!importer.optimizeMeshPolygons || !importer.optimizeMeshVertices)
                    issues.Add(new VRIssue(
                        VRSeverity.Info, VRCategory.Mesh,
                        "Mesh import optimisation disabled. Review model complexity and vertex order requirements.",
                        model, path));
                if (importer.globalScale <= 0.0001f || importer.globalScale > 100f)
                    issues.Add(new VRIssue(
                        VRSeverity.Warning, VRCategory.Mesh,
                        "Unusual import scale (" + importer.globalScale + "). Check units and colliders.",
                        model, path));
            }

            foreach (var guid in AssetDatabase.FindAssets("t:Model", new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                // Evidence-based import recommendations only; do not mutate
                // animations, bindposes, UVs or model importer settings.
                foreach (var asset in AssetDatabase.LoadAllAssetsAtPath(path))
                {
                    var mesh = asset as Mesh;
                    if (!mesh) continue;
                    if (mesh.subMeshCount > 8)
                        issues.Add(new VRIssue(
                            VRSeverity.Warning, VRCategory.Mesh,
                            mesh.name + ": " + mesh.subMeshCount
                            + " submeshes. Review draw-call/material costs and whether consolidation is appropriate.",
                            mesh, path));
                    if (mesh.bindposes.Length > 128)
                        issues.Add(new VRIssue(
                            VRSeverity.Warning, VRCategory.Mesh,
                            mesh.name + ": " + mesh.bindposes.Length
                            + " bind poses. Check skinning and target hardware limits.",
                            mesh, path));
                    if (mesh.isReadable && mesh.uv.Length == 0)
                        issues.Add(new VRIssue(
                            VRSeverity.Info, VRCategory.Mesh,
                            mesh.name + ": no UV0 channel on the imported mesh. Texture baking may be unavailable.",
                            mesh, path));
                }
            }

            foreach (var guid in AssetDatabase.FindAssets("t:Material", new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var material = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (material && !material.shader)
                    issues.Add(new VRIssue(
                        VRSeverity.Critical, VRCategory.Material,
                        "Missing shader. Verify render pipeline and shader dependencies.",
                        material, path));
            }

            foreach (var guid in AssetDatabase.FindAssets("t:Prefab", new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                if (!prefab) continue;
                int missing = 0;
                foreach (var item in prefab.GetComponentsInChildren<Transform>(true))
                    missing += GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(item.gameObject);
                if (missing > 0)
                    issues.Add(new VRIssue(
                        VRSeverity.Critical, VRCategory.Mesh,
                        prefab.name + ": " + missing +
                        " missing script components. Review before building.",
                        prefab, path));
            }
            // Scene-loaded checks do not inspect closed scenes; report this limitation.
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                var scene = SceneManager.GetSceneAt(i);
                if (!scene.isLoaded) continue;
                foreach (var root in scene.GetRootGameObjects())
                    foreach (var transform in root.GetComponentsInChildren<Transform>(true))
                    {
                        int missing = GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(transform.gameObject);
                        if (missing > 0)
                            issues.Add(new VRIssue(
                                VRSeverity.Critical, VRCategory.Mesh,
                                transform.gameObject.name + ": " + missing +
                                " missing scene script components (loaded scenes only).",
                                transform.gameObject));
                    }
            }
            return Prioritize(issues);
        }

        internal static string AssetUsers(string assetPath, string folder, int maxAssets = 4000)
        {
            if (string.IsNullOrEmpty(assetPath) || !assetPath.StartsWith("Assets/", StringComparison.Ordinal))
                return "Select a project asset with an Assets/ path first.";
            if (!AssetDatabase.IsValidFolder(folder))
                return "Select a valid Assets folder before checking dependencies.";
            var users = new List<string>();
            var guids = AssetDatabase.FindAssets("", new[] { folder });
            if (guids.Length > maxAssets)
                return "Dependency review limited to " + maxAssets +
                       " candidate assets. Select a smaller folder to avoid an expensive scan.";
            try
            {
                for (int i = 0; i < guids.Length; i++)
                {
                    string candidate = AssetDatabase.GUIDToAssetPath(guids[i]);
                    if (candidate == assetPath || AssetDatabase.IsValidFolder(candidate)) continue;
                    if (EditorUtility.DisplayCancelableProgressBar(
                        "Find asset users", candidate, (float)i / Mathf.Max(1, guids.Length)))
                        return "Dependency search cancelled; no files changed.";
                    if (Array.IndexOf(AssetDatabase.GetDependencies(candidate, true), assetPath) >= 0)
                        users.Add(candidate);
                }
            }
            finally { EditorUtility.ClearProgressBar(); }
            users.Sort(StringComparer.Ordinal);
            return "Serialized dependencies referencing " + assetPath + ": " + users.Count +
                   (users.Count > 0 ? "\n" + string.Join("\n", users.Take(25).ToArray()) : "") +
                   (users.Count > 25 ? "\n... and " + (users.Count - 25) + " more." : "") +
                   "\nRuntime string/reflection references cannot be detected.";
        }

        internal static string ExportCsv(IList<VRIssue> issues)
        {
            if (issues == null) return "Run a review first.";
            string path = EditorUtility.SaveFilePanel(
                "Export optimisation review", "", "OptimizeYourProject-Review.csv", "csv");
            if (string.IsNullOrEmpty(path)) return "Export cancelled.";
            try
            {
                using (var writer = new StreamWriter(path, false, Encoding.UTF8))
                {
                    writer.WriteLine("Severity,Category,Asset Path,Finding,Can Optimize");
                    foreach (var issue in Prioritize(issues))
                        writer.WriteLine(
                            Csv(issue.Severity.ToString()) + "," + Csv(issue.Category.ToString())
                            + "," + Csv(issue.AssetPath) + "," + Csv(issue.Message)
                            + "," + Csv(issue.CanOptimize ? "Yes" : "Review only"));
                    writer.WriteLine(Csv("Notice") + ",,,"
                        + Csv("Read-only editor analysis; not a measured runtime performance benchmark") + ",");
                }
                return "Review exported: " + issues.Count + " findings. " + path;
            }
            catch (Exception error) { return "Could not export review: " + error.Message; }
        }

        static string Csv(string value)
        {
            return "\"" + (value ?? "").Replace("\"", "\"\"") + "\"";
        }
    }
}
