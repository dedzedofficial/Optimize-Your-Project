// Per-project local presets: stored in EditorPrefs only, never uploaded.
using System;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRDeveloperPresets
    {
        static string ProjectKey
        {
            get
            {
                using (var sha = SHA256.Create())
                {
                    var raw = Encoding.UTF8.GetBytes(Application.dataPath);
                    var hash = BitConverter.ToString(sha.ComputeHash(raw)).Replace("-", "");
                    return "FISHHWB.OptimizeYourProject.Presets." + hash.Substring(0, 20);
                }
            }
        }

        internal static VRSettings Apply(string profile, VRSettings current)
        {
            if (current == null) current = new VRSettings();
            var result = JsonUtility.FromJson<VRSettings>(JsonUtility.ToJson(current));
            switch (profile)
            {
                case "Desktop":
                    result.pc = 4096; result.android = 1024; result.ios = 1024;
                    result.capParticles = true; result.maxParticles = 1000;
                    break;
                case "Mobile":
                    result.pc = 2048; result.android = 512; result.ios = 512;
                    result.capParticles = true; result.maxParticles = 200;
                    result.disableTrails = true;
                    break;
                case "Standalone VR":
                    result.pc = 2048; result.android = 512; result.ios = 512;
                    result.capParticles = true; result.maxParticles = 250;
                    result.disableShadows = true;
                    break;
                case "Balanced":
                    result.pc = 2048; result.android = 512; result.ios = 512;
                    result.capParticles = true; result.maxParticles = 500;
                    break;
                case "My Project":
                    try
                    {
                        var saved = EditorPrefs.GetString(ProjectKey, "");
                        if (string.IsNullOrEmpty(saved)) return result;
                        var loaded = JsonUtility.FromJson<VRSettings>(saved);
                        if (loaded != null) result = loaded;
                    }
                    catch (Exception error)
                    {
                        Debug.LogWarning("Could not load local optimisation preset: " + error.Message);
                    }
                    break;
            }
            result.Sanitize();
            return result;
        }

        internal static VRSettings LoadCurrent()
        {
            var json = EditorPrefs.GetString(ProjectKey + ".Current", "");
            if (string.IsNullOrEmpty(json)) return VRSettings.Load();
            try
            {
                var profile = JsonUtility.FromJson<VRSettings>(json);
                if (profile != null) { profile.Sanitize(); return profile; }
            }
            catch (Exception error)
            {
                Debug.LogWarning("Could not load current project settings: " + error.Message);
            }
            return VRSettings.Load();
        }

        internal static void SaveCurrent(VRSettings settings)
        {
            if (settings == null) return;
            settings.Sanitize();
            EditorPrefs.SetString(ProjectKey + ".Current", JsonUtility.ToJson(settings));
            settings.Save(); // Keep existing settings consumers working.
        }

        internal static bool HasLocal => EditorPrefs.HasKey(ProjectKey);

        internal static void SaveProject(VRSettings current)
        {
            if (current == null) return;
            current.Sanitize();
            EditorPrefs.SetString(ProjectKey, JsonUtility.ToJson(current));
        }
    }
}
