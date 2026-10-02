using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class VRTextureImportFix
    {
        internal readonly string Path;
        internal readonly bool SetNormalMap;
        internal readonly bool DisableSrgb;

        internal VRTextureImportFix(string path, bool setNormalMap, bool disableSrgb)
        {
            Path = path;
            SetNormalMap = setNormalMap;
            DisableSrgb = disableSrgb;
        }
    }

    internal sealed class VRUnusedMaterialSlotFix
    {
        internal readonly Renderer Renderer;
        internal readonly int KeepCount;
        internal readonly int RemoveCount;

        internal VRUnusedMaterialSlotFix(Renderer renderer, int keepCount, int removeCount)
        {
            Renderer = renderer;
            KeepCount = keepCount;
            RemoveCount = removeCount;
        }
    }

    internal sealed class VRDuplicateMaterialFix
    {
        internal readonly Renderer Renderer;
        internal readonly Material[] Materials;
        internal readonly int ReplacementCount;

        internal VRDuplicateMaterialFix(Renderer renderer, Material[] materials, int replacementCount)
        {
            Renderer = renderer;
            Materials = materials;
            ReplacementCount = replacementCount;
        }
    }

    internal sealed class VROversizedMeshImportFix
    {
        internal readonly string Path;
        internal readonly int TriangleCount;

        internal VROversizedMeshImportFix(string path, int triangleCount)
        {
            Path = path;
            TriangleCount = triangleCount;
        }
    }

    internal static class VRProjectMaintenance
    {
        static readonly string[] NormalTokens =
        {
            "_normal", "-normal", "_norm", "-norm", "_nrm", "-nrm", " normal"
        };

        static readonly string[] LinearDataTokens =
        {
            "_mask", "-mask", "_metallic", "-metallic", "_roughness", "-roughness",
            "_smoothness", "-smoothness", "_occlusion", "-occlusion", "_ao", "-ao", "_height", "-height",
            "_displacement", "-displacement", "_orm", "-orm", "_rma", "-rma", "_mra", "-mra"
        };

        internal static List<VRTextureImportFix> CollectTextureImportFixes(string folder)
        {
            var fixes = new List<VRTextureImportFix>();
            foreach (var guid in AssetDatabase.FindAssets("t:Texture", new[] { folder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (string.IsNullOrEmpty(path) || !path.StartsWith("Assets/", StringComparison.Ordinal))
                    continue;

                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null || importer.textureShape != TextureImporterShape.Texture2D ||
                    importer.textureType != TextureImporterType.Default)
                    continue;

                string file = Path.GetFileNameWithoutExtension(path).ToLowerInvariant();
                bool normal = ContainsToken(file, NormalTokens);
                bool linear = !normal && ContainsToken(file, LinearDataTokens);
                if (!normal && !(linear && importer.sRGBTexture))
                    continue;

                fixes.Add(new VRTextureImportFix(path, normal, linear && importer.sRGBTexture));
            }
            return fixes;
        }

        internal static VRActionOutcome ApplyTextureImportFix(VRTextureImportFix fix)
        {
            if (fix == null || string.IsNullOrEmpty(fix.Path))
                return VRActionOutcome.Skipped;

            var importer = AssetImporter.GetAtPath(fix.Path) as TextureImporter;
            if (importer == null || importer.textureShape != TextureImporterShape.Texture2D)
                return VRActionOutcome.Unsupported;

            bool changed = false;
            if (fix.SetNormalMap && importer.textureType == TextureImporterType.Default)
            {
                importer.textureType = TextureImporterType.NormalMap;
                changed = true;
            }

            if (fix.DisableSrgb && importer.textureType == TextureImporterType.Default && importer.sRGBTexture)
            {
                importer.sRGBTexture = false;
                changed = true;
            }

            if (changed)
                importer.SaveAndReimport();
            return changed ? VRActionOutcome.Changed : VRActionOutcome.Unchanged;
        }

        internal static List<VRDuplicateMaterialFix> CollectDuplicateMaterialFixes(GameObject root, string folder)
        {
            var renderers = CollectRenderers(root);
            var materials = new HashSet<Material>();

            foreach (var renderer in renderers)
                foreach (var material in renderer.sharedMaterials ?? Array.Empty<Material>())
                    if (PersistentMaterial(material) && (root || InFolder(AssetDatabase.GetAssetPath(material), folder)))
                        materials.Add(material);

            if (!root && !string.IsNullOrEmpty(folder))
            {
                foreach (var guid in AssetDatabase.FindAssets("t:Material", new[] { folder }))
                {
                    string path = AssetDatabase.GUIDToAssetPath(guid);
                    var material = AssetDatabase.LoadAssetAtPath<Material>(path);
                    if (PersistentMaterial(material))
                        materials.Add(material);
                }
            }

            var ordered = new List<Material>(materials);
            ordered.Sort((a, b) => string.CompareOrdinal(AssetDatabase.GetAssetPath(a), AssetDatabase.GetAssetPath(b)));

            var canonical = new Dictionary<string, Material>(StringComparer.Ordinal);
            var replacement = new Dictionary<Material, Material>();
            foreach (var material in ordered)
            {
                string signature = VRProjectInsights.MaterialSignature(material);
                if (string.IsNullOrEmpty(signature)) continue;
                if (!canonical.TryGetValue(signature, out var first))
                    canonical.Add(signature, material);
                else if (first != material)
                    replacement[material] = first;
            }

            var fixes = new List<VRDuplicateMaterialFix>();
            foreach (var renderer in renderers)
            {
                var current = renderer.sharedMaterials ?? Array.Empty<Material>();
                var next = (Material[])current.Clone();
                int changed = 0;

                for (int i = 0; i < next.Length; i++)
                {
                    var material = next[i];
                    if (material && replacement.TryGetValue(material, out var first) && first != material)
                    {
                        next[i] = first;
                        changed++;
                    }
                }

                if (changed > 0)
                    fixes.Add(new VRDuplicateMaterialFix(renderer, next, changed));
            }

            return fixes;
        }

        internal static VRActionOutcome ApplyDuplicateMaterialFix(VRDuplicateMaterialFix fix)
        {
            if (fix == null || !fix.Renderer || fix.Materials == null)
                return VRActionOutcome.Skipped;

            Undo.RecordObject(fix.Renderer, "Fix Duplicate Materials");
            fix.Renderer.sharedMaterials = fix.Materials;
            EditorUtility.SetDirty(fix.Renderer);
            return VRActionOutcome.Changed;
        }

        internal static List<VRUnusedMaterialSlotFix> CollectUnusedMaterialSlots(GameObject root)
        {
            var fixes = new List<VRUnusedMaterialSlotFix>();
            foreach (var renderer in CollectRenderers(root))
            {
                Mesh mesh = MeshFor(renderer);
                if (!mesh) continue;

                int submeshes = Mathf.Max(0, mesh.subMeshCount);
                var materials = renderer.sharedMaterials ?? Array.Empty<Material>();
                int keep = materials.Length;
                while (keep > submeshes && materials[keep - 1] == null)
                    keep--;

                if (keep < materials.Length)
                    fixes.Add(new VRUnusedMaterialSlotFix(renderer, keep, materials.Length - keep));
            }
            return fixes;
        }

        internal static VRActionOutcome ApplyUnusedMaterialSlotFix(VRUnusedMaterialSlotFix fix)
        {
            if (fix == null || !fix.Renderer)
                return VRActionOutcome.Skipped;

            var current = fix.Renderer.sharedMaterials ?? Array.Empty<Material>();
            if (current.Length <= fix.KeepCount)
                return VRActionOutcome.Unchanged;

            Undo.RecordObject(fix.Renderer, "Clean Unused Material Slots");
            var trimmed = new Material[fix.KeepCount];
            Array.Copy(current, trimmed, fix.KeepCount);
            fix.Renderer.sharedMaterials = trimmed;
            EditorUtility.SetDirty(fix.Renderer);
            return VRActionOutcome.Changed;
        }

        internal static List<VROversizedMeshImportFix> CollectOversizedMeshImportFixes(
            GameObject root, int triangleThreshold = 100000)
        {
            var fixes = new List<VROversizedMeshImportFix>();
            var seen = new HashSet<string>(StringComparer.Ordinal);

            foreach (var renderer in CollectRenderers(root))
            {
                Mesh mesh = MeshFor(renderer);
                if (!mesh) continue;

                int triangles = TriangleCount(mesh);
                if (triangles < triangleThreshold) continue;

                string path = AssetDatabase.GetAssetPath(mesh);
                if (string.IsNullOrEmpty(path) || !path.StartsWith("Assets/", StringComparison.Ordinal) ||
                    !seen.Add(path))
                    continue;

                if (AssetImporter.GetAtPath(path) is ModelImporter)
                    fixes.Add(new VROversizedMeshImportFix(path, triangles));
            }

            fixes.Sort((a, b) => b.TriangleCount.CompareTo(a.TriangleCount));
            return fixes;
        }

        internal static VRActionOutcome ApplyOversizedMeshImportFix(VROversizedMeshImportFix fix)
        {
            if (fix == null || string.IsNullOrEmpty(fix.Path))
                return VRActionOutcome.Skipped;

            var importer = AssetImporter.GetAtPath(fix.Path) as ModelImporter;
            if (importer == null)
                return VRActionOutcome.Unsupported;

            bool changed = false;
            if (importer.meshCompression == ModelImporterMeshCompression.Off ||
                importer.meshCompression == ModelImporterMeshCompression.Low)
            {
                importer.meshCompression = ModelImporterMeshCompression.Medium;
                changed = true;
            }

            if (!importer.optimizeMeshPolygons)
            {
                importer.optimizeMeshPolygons = true;
                changed = true;
            }

            if (!importer.optimizeMeshVertices)
            {
                importer.optimizeMeshVertices = true;
                changed = true;
            }

            if (changed)
                importer.SaveAndReimport();
            return changed ? VRActionOutcome.Changed : VRActionOutcome.Unchanged;
        }

        static List<Renderer> CollectRenderers(GameObject root)
        {
            var renderers = new List<Renderer>();
            if (root)
            {
                renderers.AddRange(root.GetComponentsInChildren<MeshRenderer>(true));
                renderers.AddRange(root.GetComponentsInChildren<SkinnedMeshRenderer>(true));
            }
            else
            {
                renderers.AddRange(VRProjectScanner.SceneObjects<MeshRenderer>());
                renderers.AddRange(VRProjectScanner.SceneObjects<SkinnedMeshRenderer>());
            }
            return renderers;
        }

        static Mesh MeshFor(Renderer renderer)
        {
            if (!renderer) return null;
            if (renderer is SkinnedMeshRenderer skinned)
                return skinned.sharedMesh;
            var filter = renderer.GetComponent<MeshFilter>();
            return filter ? filter.sharedMesh : null;
        }

        static int TriangleCount(Mesh mesh)
        {
            int triangles = 0;
            for (int i = 0; i < mesh.subMeshCount; i++)
                if (mesh.GetTopology(i) == MeshTopology.Triangles)
                    triangles += (int)(mesh.GetIndexCount(i) / 3);
            return triangles;
        }

        static bool PersistentMaterial(Material material)
        {
            if (!material) return false;
            string path = AssetDatabase.GetAssetPath(material);
            return !string.IsNullOrEmpty(path) && path.StartsWith("Assets/", StringComparison.Ordinal);
        }

        static bool InFolder(string path, string folder)
        {
            if (string.IsNullOrEmpty(path) || string.IsNullOrEmpty(folder)) return false;
            if (folder == "Assets") return path.StartsWith("Assets/", StringComparison.Ordinal);
            return path == folder || path.StartsWith(folder.TrimEnd('/') + "/", StringComparison.Ordinal);
        }

        static bool ContainsToken(string value, IEnumerable<string> tokens)
        {
            foreach (var token in tokens)
                if (value.IndexOf(token, StringComparison.Ordinal) >= 0)
                    return true;
            return false;
        }
    }
}
