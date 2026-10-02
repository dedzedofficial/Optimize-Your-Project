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

        internal static List<VRUnusedMaterialSlotFix> CollectUnusedMaterialSlots(GameObject root)
        {
            var fixes = new List<VRUnusedMaterialSlotFix>();
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
            return fixes;

            void Add(Renderer renderer, Mesh mesh)
            {
                if (!renderer || !mesh) return;
                int submeshes = Mathf.Max(0, mesh.subMeshCount);
                var materials = renderer.sharedMaterials ?? Array.Empty<Material>();
                int keep = materials.Length;
                while (keep > submeshes && materials[keep - 1] == null)
                    keep--;
                if (keep == materials.Length) return;
                fixes.Add(new VRUnusedMaterialSlotFix(renderer, keep, materials.Length - keep));
            }
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

        static bool ContainsToken(string value, IEnumerable<string> tokens)
        {
            foreach (var token in tokens)
                if (value.IndexOf(token, StringComparison.Ordinal) >= 0)
                    return true;
            return false;
        }
    }
}
