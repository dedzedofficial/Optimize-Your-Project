using System;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRTextureOptimizer
    {
        public static bool Optimize(string path, VRSettings settings)
        {
            var importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null || !path.StartsWith("Assets/", StringComparison.Ordinal) ||
                importer.textureShape != TextureImporterShape.Texture2D ||
                (importer.textureType != TextureImporterType.Default && importer.textureType != TextureImporterType.NormalMap)) return false;
            settings.Sanitize();
            bool changed = false;
            changed |= Platform(importer, "Standalone", settings.pc);
            changed |= Platform(importer, "Android", settings.android);
            changed |= Platform(importer, "iPhone", settings.ios);
            if (changed) importer.SaveAndReimport();
            return changed;
        }

        public static bool OptimizeWithCompression(string path, VRSettings settings, System.Collections.Generic.IList<VRCompressionChange> candidates)
        {
            var importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null || !path.StartsWith("Assets/", StringComparison.Ordinal) ||
                importer.textureShape != TextureImporterShape.Texture2D ||
                (importer.textureType != TextureImporterType.Default && importer.textureType != TextureImporterType.NormalMap)) return false;
            settings.Sanitize();
            bool changed = false;
            if (candidates != null)
                foreach (var item in candidates)
                {
                    var p = importer.GetPlatformTextureSettings(item.Platform);
                    var effective = p.overridden ? p.textureCompression : importer.textureCompression;
                    int size = p.overridden ? p.maxTextureSize : importer.maxTextureSize;
                    if (p.overridden && p.format != TextureImporterFormat.Automatic ||
                        effective != TextureImporterCompression.Uncompressed ||
                        p.overridden != item.HadOverride || size != item.BeforeSize) continue;
                    if (!p.overridden) { p.overridden = true; p.maxTextureSize = importer.maxTextureSize; }
                    p.format = TextureImporterFormat.Automatic;
                    p.textureCompression = TextureImporterCompression.Compressed;
                    importer.SetPlatformTextureSettings(p);
                    changed = true;
                }
            changed |= Platform(importer, "Standalone", settings.pc);
            changed |= Platform(importer, "Android", settings.android);
            changed |= Platform(importer, "iPhone", settings.ios);
            if (changed) importer.SaveAndReimport();
            return changed;
        }

        static bool Platform(TextureImporter importer, string name, int maximum)
        {
            var p = importer.GetPlatformTextureSettings(name);
            bool changed = false;
            bool hadOverride = p.overridden;
            if (!p.overridden) { p.overridden = true; changed = true; }
            // A cap preserves smaller textures and does not increase a pre-existing stricter limit.
            int current = hadOverride && p.maxTextureSize > 0 ? p.maxTextureSize : maximum;
            int next = Mathf.Min(current, maximum);
            if (p.maxTextureSize != next) { p.maxTextureSize = next; changed = true; }
            // Preserve all format, compression, mip, filter and anisotropy settings.
            if (changed) importer.SetPlatformTextureSettings(p);
            return changed;
        }
    }
}
