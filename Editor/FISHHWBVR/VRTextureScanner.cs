using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class VRTextureScanner : IVRScanner
    {
        public void ScanAsset(string path, VRSettings settings, List<VRIssue> issues)
        {
            var importer = AssetImporter.GetAtPath(path) as TextureImporter;
            if (importer == null) return;
            var texture = AssetDatabase.LoadAssetAtPath<Texture>(path);
            if (!texture) return;
            int largest = Mathf.Max(texture.width, texture.height);
            var platform = importer.GetPlatformTextureSettings(settings.TargetName);
            int limit = platform.overridden ? platform.maxTextureSize : importer.maxTextureSize;
            if (largest >= 8192) issues.Add(new VRIssue(VRSeverity.Critical, VRCategory.Texture, "8K source (" + texture.width + " x " + texture.height + "); inspect platform limits.", texture, path, true));
            else if (largest >= 4096) issues.Add(new VRIssue(VRSeverity.Warning, VRCategory.Texture, "4K source (" + texture.width + " x " + texture.height + ").", texture, path, true));
            if (!platform.overridden) issues.Add(new VRIssue(VRSeverity.Warning, VRCategory.Texture, "Missing " + settings.TargetName + " platform override.", texture, path, true));
            if (limit > settings.TargetMax) issues.Add(new VRIssue(VRSeverity.Warning, VRCategory.Texture, "Importer cap " + limit + " exceeds profile " + settings.TargetMax + ".", texture, path, true));
            if (platform.overridden && platform.textureCompression == TextureImporterCompression.Uncompressed && largest >= 1024)
                issues.Add(new VRIssue(VRSeverity.Warning, VRCategory.Texture, "Large uncompressed platform texture; inspect format and alpha needs.", texture, path, true));
            // Source dimensions are not a reliable estimate of actual runtime GPU memory.
        }
        public void ScanScene(VRSettings settings, List<VRIssue> issues) { }
    }
}
