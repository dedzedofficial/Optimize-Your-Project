using System;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRAudioOptimizer
    {
        const float StreamingThresholdSeconds = 30f;

        internal static string Optimize(string folder)
        {
            if (string.IsNullOrEmpty(folder) || !AssetDatabase.IsValidFolder(folder))
                return "Audio optimization: choose a valid Assets folder.";

            string[] guids = AssetDatabase.FindAssets("t:AudioClip", new[] { folder });
            int changed = 0;
            int unchanged = 0;
            int unsupported = 0;
            int failed = 0;

            foreach (string guid in guids)
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                var importer = AssetImporter.GetAtPath(path) as AudioImporter;
                var clip = AssetDatabase.LoadAssetAtPath<AudioClip>(path);
                if (!importer || !clip)
                {
                    unsupported++;
                    continue;
                }

                try
                {
                    var settings = importer.defaultSampleSettings;
                    bool longClip = clip.length >= StreamingThresholdSeconds;
                    var desiredLoadType = longClip ? AudioClipLoadType.Streaming : AudioClipLoadType.CompressedInMemory;
                    const AudioCompressionFormat desiredFormat = AudioCompressionFormat.Vorbis;
                    float desiredQuality = longClip ? 0.65f : 0.75f;

                    bool dirty = false;
                    if (settings.loadType != desiredLoadType)
                    {
                        settings.loadType = desiredLoadType;
                        dirty = true;
                    }
                    if (settings.compressionFormat != desiredFormat)
                    {
                        settings.compressionFormat = desiredFormat;
                        dirty = true;
                    }
                    if (Math.Abs(settings.quality - desiredQuality) > 0.001f)
                    {
                        settings.quality = desiredQuality;
                        dirty = true;
                    }

                    if (!dirty)
                    {
                        unchanged++;
                        continue;
                    }

                    importer.defaultSampleSettings = settings;
                    importer.SaveAndReimport();
                    changed++;
                }
                catch (Exception exception)
                {
                    failed++;
                    Debug.LogWarning("[Optimize Your Project] Audio optimization failed for " + path + ": " + exception.Message);
                }
            }

            AssetDatabase.Refresh();
            return "Audio optimization complete: " + changed + " changed, " + unchanged + " already optimized, " + unsupported + " unsupported, " + failed + " failed. Long clips use Streaming; shorter clips use Compressed In Memory with Vorbis compression.";
        }

        [MenuItem("FISHHWB/Optimize Your Project/Optimize Audio")]
        static void OptimizeSelectedFolder()
        {
            string folder = VRProjectInsights.FolderFromSelection("Assets");
            string result = Optimize(folder);
            Debug.Log("[Optimize Your Project] " + result);
            EditorUtility.DisplayDialog("Optimize Audio", result, "OK");
        }
    }
}
