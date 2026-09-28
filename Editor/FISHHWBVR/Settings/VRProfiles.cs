using System;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    [Serializable]
    internal sealed class VRSettings
    {
        public int pc = 2048, android = 512, ios = 512;
        public bool capParticles = true, capLifetime, disableTrails, disableCollision, disableNoise;
        public bool disableLights, disableShadows, disableSubEmitters;
        public int maxParticles = 500;
        public float maxLifetime = 10f;
        public bool capLightRange;
        public float maxLightRange = 20f;

        const string Key = "FISHHWB.VROptimizer.v064.Settings";
        public static VRSettings Load()
        {
            var json = EditorPrefs.GetString(Key, "");
            if (string.IsNullOrEmpty(json)) return new VRSettings();
            try { return JsonUtility.FromJson<VRSettings>(json) ?? new VRSettings(); }
            catch { return new VRSettings(); }
        }
        public void Save() { EditorPrefs.SetString(Key, JsonUtility.ToJson(this)); }
        public void Sanitize()
        {
            pc = Mathf.Clamp(Mathf.ClosestPowerOfTwo(Mathf.Max(32, pc)), 32, 16384);
            android = Mathf.Clamp(Mathf.ClosestPowerOfTwo(Mathf.Max(32, android)), 32, 16384);
            ios = Mathf.Clamp(Mathf.ClosestPowerOfTwo(Mathf.Max(32, ios)), 32, 16384);
            maxParticles = Mathf.Max(1, maxParticles);
            maxLifetime = Mathf.Max(.01f, maxLifetime);
            maxLightRange = Mathf.Max(.01f, maxLightRange);
        }
    }
}
