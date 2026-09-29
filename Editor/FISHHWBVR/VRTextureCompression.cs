using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class VRCompressionChange
    {
        public string Path;
        public string Platform;
        public Texture Texture;
        public bool Include = true;
        public bool HadOverride;
        public int BeforeSize;
        public TextureImporterCompression BeforeCompression;
    }

    internal static class VRTextureCompression
    {
        static readonly string[] Platforms = { "Standalone", "Android", "iPhone" };
        internal static List<VRCompressionChange> Collect(GameObject avatar, string folder, out bool cancelled)
        {
            cancelled = false;
            var paths = new HashSet<string>(StringComparer.Ordinal);
            if (avatar)
            {
                foreach (var texture in VRAvatarWorkflow.ReferencedTextures(avatar))
                    paths.Add(AssetDatabase.GetAssetPath(texture));
            }
            else
            {
                foreach (var guid in AssetDatabase.FindAssets("t:Texture", new[] { folder }))
                    paths.Add(AssetDatabase.GUIDToAssetPath(guid));
            }
            var ordered = new List<string>(paths);
            ordered.Sort(StringComparer.Ordinal);
            var changes = new List<VRCompressionChange>();
            try
            {
                for (int i = 0; i < ordered.Count; i++)
                {
                    var path = ordered[i];
                    if (EditorUtility.DisplayCancelableProgressBar("Check Texture Compression", path, ordered.Count == 0 ? 1 : (float)i / ordered.Count))
                    { cancelled = true; break; }
                    if (string.IsNullOrEmpty(path) || !path.StartsWith("Assets/", StringComparison.Ordinal)) continue;
                    var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                    if (!importer || importer.textureShape != TextureImporterShape.Texture2D ||
                        (importer.textureType != TextureImporterType.Default && importer.textureType != TextureImporterType.NormalMap)) continue;
                    foreach (var platform in Platforms)
                    {
                        var p = importer.GetPlatformTextureSettings(platform);
                        var effectiveCompression = p.overridden ? p.textureCompression : importer.textureCompression;
                        // Explicit formats are intentional and cannot be changed safely by this action.
                        if (effectiveCompression != TextureImporterCompression.Uncompressed ||
                            p.overridden && p.format != TextureImporterFormat.Automatic) continue;
                        changes.Add(new VRCompressionChange
                        {
                            Path = path, Platform = platform, Texture = AssetDatabase.LoadAssetAtPath<Texture>(path),
                            HadOverride = p.overridden, BeforeSize = p.overridden ? p.maxTextureSize : importer.maxTextureSize,
                            BeforeCompression = effectiveCompression
                        });
                    }
                }
            }
            finally { EditorUtility.ClearProgressBar(); }
            return changes;
        }

        internal static bool Apply(string path, IList<VRCompressionChange> selected, out string formats)
        {
            formats = "";
            var importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (!importer || !path.StartsWith("Assets/", StringComparison.Ordinal)) return false;
            bool changed = false;
            var applied = new List<VRCompressionChange>();
            foreach (var item in selected)
            {
                var p = importer.GetPlatformTextureSettings(item.Platform);
                if (p.overridden && p.format != TextureImporterFormat.Automatic) continue;
                var effective = p.overridden ? p.textureCompression : importer.textureCompression;
                int effectiveSize = p.overridden ? p.maxTextureSize : importer.maxTextureSize;
                if (effective != TextureImporterCompression.Uncompressed ||
                    effective != item.BeforeCompression || p.overridden != item.HadOverride ||
                    effectiveSize != item.BeforeSize) continue;
                if (!p.overridden)
                {
                    p.overridden = true;
                    p.maxTextureSize = importer.maxTextureSize;
                }
                p.format = TextureImporterFormat.Automatic;
                p.textureCompression = TextureImporterCompression.Compressed;
                importer.SetPlatformTextureSettings(p);
                applied.Add(item);
                changed = true;
            }
            if (!changed) return false;
            importer.SaveAndReimport();
            foreach (var item in applied)
            {
                var after = importer.GetPlatformTextureSettings(item.Platform);
                formats += item.Platform + ": " + (after.format == TextureImporterFormat.Automatic ? importer.GetAutomaticFormat(item.Platform) : after.format) + "; ";
            }
            return true;
        }
    }
}
