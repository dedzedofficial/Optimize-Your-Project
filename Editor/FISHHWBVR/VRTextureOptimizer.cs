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
            changed |= Platform(importer, "Standalone", settings.pc, settings.overridePC, settings);
            changed |= Platform(importer, "Android", settings.android, settings.overrideAndroid, settings);
            changed |= Platform(importer, "iPhone", settings.ios, settings.overrideIOS, settings);
            bool colorTexture = importer.textureType == TextureImporterType.Default && importer.textureShape == TextureImporterShape.Texture2D;
            if (colorTexture)
            {
                if (settings.changeMipmaps && importer.mipmapEnabled != settings.mipmaps) { importer.mipmapEnabled = settings.mipmaps; changed = true; }
                if (settings.changeFilter && importer.filterMode != settings.filter) { importer.filterMode = settings.filter; changed = true; }
                if (settings.changeAniso && importer.anisoLevel != settings.aniso) { importer.anisoLevel = settings.aniso; changed = true; }
            }
            if (changed) importer.SaveAndReimport();
            return changed;
        }

        static bool Platform(TextureImporter importer, string name, int maximum, bool enabled, VRSettings settings)
        {
            if (!enabled) return false;
            var p = importer.GetPlatformTextureSettings(name);
            bool changed = false;
            bool hadOverride = p.overridden;
            if (!p.overridden) { p.overridden = true; changed = true; }
            // A cap preserves smaller textures and does not increase a pre-existing stricter limit.
            int current = hadOverride && p.maxTextureSize > 0 ? p.maxTextureSize : maximum;
            int next = Mathf.Min(current, maximum);
            if (p.maxTextureSize != next) { p.maxTextureSize = next; changed = true; }
            // Automatic lets Unity choose a supported format for the platform and texture type.
            var wanted = settings.compression ? TextureImporterFormat.Automatic : TextureImporterFormat.RGBA32;
            if (p.format != wanted) { p.format = wanted; changed = true; }
            var mode = settings.compression ? TextureImporterCompression.Compressed : TextureImporterCompression.Uncompressed;
            if (p.textureCompression != mode) { p.textureCompression = mode; changed = true; }
            bool crunch = settings.compression && settings.crunch && name != "iPhone" &&
                          importer.textureType == TextureImporterType.Default && importer.textureShape == TextureImporterShape.Texture2D;
            if (p.crunchedCompression != crunch) { p.crunchedCompression = crunch; changed = true; }
            if (p.compressionQuality != settings.quality) { p.compressionQuality = settings.quality; changed = true; }
            if (changed) importer.SetPlatformTextureSettings(p);
            return changed;
        }
    }
}
