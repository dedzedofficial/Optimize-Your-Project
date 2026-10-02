using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
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

        internal static List<VRIssue> OversizedMeshes(GameObject root, int triangleThreshold = 100000)
        {
            var rows = new List<Tuple<int, VRIssue>>();
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

            rows.Sort((a, b) => b.Item1.CompareTo(a.Item1));
            var issues = new List<VRIssue>();
            foreach (var row in rows)
                issues.Add(row.Item2);
            return issues;

            void Add(Mesh mesh, GameObject owner)
            {
                if (!mesh || !owner || !seen.Add(mesh)) return;
                int triangles = TriangleCount(mesh);
                if (triangles < triangleThreshold) return;

                var renderer = owner.GetComponent<Renderer>();
                int materialSlots = renderer && renderer.sharedMaterials != null ? renderer.sharedMaterials.Length : 0;
                string message = owner.name + " / " + mesh.name + ": " +
                                 triangles.ToString("N0") + " triangles, " +
                                 mesh.vertexCount.ToString("N0") + " vertices, " +
                                 mesh.subMeshCount.ToString("N0") + " submeshes, " +
                                 materialSlots.ToString("N0") + " material slots";

                rows.Add(Tuple.Create(
                    triangles,
                    new VRIssue(
                        triangles >= triangleThreshold * 2 ? VRSeverity.Critical : VRSeverity.Warning,
                        VRCategory.Mesh,
                        message,
                        owner)));
            }
        }

        internal static List<VRIssue> HeavyMeshes(GameObject root, int triangleThreshold = 100000)
        {
            return OversizedMeshes(root, triangleThreshold);
        }

        internal static List<VRIssue> DuplicateMaterials(string folder)
        {
            var groups = new Dictionary<string, List<Tuple<Material, string>>>(StringComparer.Ordinal);
            foreach (var guid in AssetDatabase.FindAssets("t:Material", new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (string.IsNullOrEmpty(path) || !path.StartsWith("Assets/", StringComparison.Ordinal))
                    continue;

                var material = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (!material || !material.shader)
                    continue;

                string signature = MaterialSignature(material);
                if (string.IsNullOrEmpty(signature))
                    continue;

                if (!groups.TryGetValue(signature, out var list))
                {
                    list = new List<Tuple<Material, string>>();
                    groups.Add(signature, list);
                }
                list.Add(Tuple.Create(material, path));
            }

            var issues = new List<VRIssue>();
            foreach (var group in groups.Values)
            {
                if (group.Count < 2) continue;
                group.Sort((a, b) => string.CompareOrdinal(a.Item2, b.Item2));
                var original = group[0];
                for (int i = 1; i < group.Count; i++)
                {
                    var duplicate = group[i];
                    issues.Add(new VRIssue(
                        VRSeverity.Warning,
                        VRCategory.Material,
                        duplicate.Item1.name + " duplicates " + original.Item1.name +
                        ": same shader, keywords, queue and saved shader properties.",
                        duplicate.Item1,
                        duplicate.Item2,
                        false));
                }
            }

            issues.Sort((a, b) => string.CompareOrdinal(a.AssetPath, b.AssetPath));
            return issues;
        }

        internal static List<VRIssue> ExpensiveMaterials(GameObject root, int warningSlots = 4, int criticalSlots = 8)
        {
            var issues = new List<VRIssue>();
            if (root)
            {
                foreach (var renderer in root.GetComponentsInChildren<MeshRenderer>(true))
                    Add(renderer, renderer.GetComponent<MeshFilter>() ? renderer.GetComponent<MeshFilter>().sharedMesh : null);
                foreach (var renderer in root.GetComponentsInChildren<SkinnedMeshRenderer>(true))
                    Add(renderer, renderer.sharedMesh);
            }
            else
            {
                foreach (var renderer in VRProjectScanner.SceneObjects<MeshRenderer>())
                    Add(renderer, renderer.GetComponent<MeshFilter>() ? renderer.GetComponent<MeshFilter>().sharedMesh : null);
                foreach (var renderer in VRProjectScanner.SceneObjects<SkinnedMeshRenderer>())
                    Add(renderer, renderer.sharedMesh);
            }

            issues.Sort((a, b) => string.CompareOrdinal(a.Message, b.Message));
            return issues;

            void Add(Renderer renderer, Mesh mesh)
            {
                if (!renderer || !mesh) return;
                int slots = renderer.sharedMaterials == null ? 0 : renderer.sharedMaterials.Length;
                int submeshes = mesh.subMeshCount;
                int cost = Mathf.Max(slots, submeshes);
                if (cost <= warningSlots) return;

                issues.Add(new VRIssue(
                    cost >= criticalSlots ? VRSeverity.Critical : VRSeverity.Warning,
                    VRCategory.Material,
                    renderer.gameObject.name + ": " + slots + " material slots, " +
                    submeshes + " submeshes. Review whether this object needs this many separate material sections.",
                    renderer.gameObject));
            }
        }

        static int TriangleCount(Mesh mesh)
        {
            int triangles = 0;
            for (int i = 0; i < mesh.subMeshCount; i++)
                if (mesh.GetTopology(i) == MeshTopology.Triangles)
                    triangles += (int)(mesh.GetIndexCount(i) / 3);
            return triangles;
        }

        static string MaterialSignature(Material material)
        {
            var shader = material.shader;
            if (!shader) return null;

            var builder = new StringBuilder(512);
            builder.Append(shader.name).Append('|')
                   .Append(material.renderQueue).Append('|')
                   .Append(material.enableInstancing).Append('|')
                   .Append(material.doubleSidedGI).Append('|')
                   .Append((int)material.globalIlluminationFlags).Append('|');

            var keywords = material.shaderKeywords ?? Array.Empty<string>();
            Array.Sort(keywords, StringComparer.Ordinal);
            foreach (var keyword in keywords)
                builder.Append("K:").Append(keyword).Append(';');

            int propertyCount = ShaderUtil.GetPropertyCount(shader);
            for (int i = 0; i < propertyCount; i++)
            {
                string property = ShaderUtil.GetPropertyName(shader, i);
                var type = ShaderUtil.GetPropertyType(shader, i);
                builder.Append('|').Append(property).Append(':').Append((int)type).Append('=');

                switch (type)
                {
                    case ShaderUtil.ShaderPropertyType.Color:
                        AppendColor(builder, material.GetColor(property));
                        break;
                    case ShaderUtil.ShaderPropertyType.Vector:
                        AppendVector(builder, material.GetVector(property));
                        break;
                    case ShaderUtil.ShaderPropertyType.Float:
                    case ShaderUtil.ShaderPropertyType.Range:
                        AppendFloat(builder, material.GetFloat(property));
                        break;
                    case ShaderUtil.ShaderPropertyType.TexEnv:
                        var texture = material.GetTexture(property);
                        string texturePath = texture ? AssetDatabase.GetAssetPath(texture) : "";
                        builder.Append(texturePath);
                        if (texture && string.IsNullOrEmpty(texturePath))
                            builder.Append('#').Append(texture.GetInstanceID());
                        builder.Append('@');
                        AppendVector2(builder, material.GetTextureScale(property));
                        builder.Append(',');
                        AppendVector2(builder, material.GetTextureOffset(property));
                        break;
                    default:
                        return null;
                }
            }
            return builder.ToString();
        }

        static void AppendFloat(StringBuilder builder, float value)
        {
            builder.Append(value.ToString("R", CultureInfo.InvariantCulture));
        }

        static void AppendColor(StringBuilder builder, Color value)
        {
            AppendFloat(builder, value.r); builder.Append(',');
            AppendFloat(builder, value.g); builder.Append(',');
            AppendFloat(builder, value.b); builder.Append(',');
            AppendFloat(builder, value.a);
        }

        static void AppendVector(StringBuilder builder, Vector4 value)
        {
            AppendFloat(builder, value.x); builder.Append(',');
            AppendFloat(builder, value.y); builder.Append(',');
            AppendFloat(builder, value.z); builder.Append(',');
            AppendFloat(builder, value.w);
        }

        static void AppendVector2(StringBuilder builder, Vector2 value)
        {
            AppendFloat(builder, value.x); builder.Append(',');
            AppendFloat(builder, value.y);
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
