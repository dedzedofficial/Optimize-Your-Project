using System;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal enum VRTarget { AndroidQuest, Standalone, IOS }
    internal enum VRTexturePreset { PCQuality, QuestBalanced, QuestPerformance, Custom }
    internal enum VRParticlePreset { Conservative, Balanced, QuestPerformance, Custom }

    [Serializable]
    internal sealed class VRSettings
    {
        public VRTarget target = VRTarget.AndroidQuest;
        public VRTexturePreset texturePreset = VRTexturePreset.QuestBalanced;
        public int pc = 2048, android = 512, ios = 512;
        public bool overridePC = true, overrideAndroid = true, overrideIOS = true;
        public bool compression = true, crunch, mipmaps = true, changeMipmaps;
        public int quality = 50;
        public bool changeFilter, changeAniso;
        public FilterMode filter = FilterMode.Bilinear;
        public int aniso = 1;
        public VRParticlePreset particlePreset = VRParticlePreset.Balanced;
        public bool capParticles = true, capLifetime, disableTrails, disableCollision, disableNoise;
        public bool disableLights, disableShadows, disableSubEmitters;
        public int maxParticles = 500;
        public float maxLifetime = 10f;
        public bool capLightRange;
        public float maxLightRange = 20f;

        const string Key = "FISHHWB.VROptimizer.v063.Settings";
        public static VRSettings Load()
        {
            var json = EditorPrefs.GetString(Key, "");
            if (string.IsNullOrEmpty(json)) return new VRSettings();
            try { return JsonUtility.FromJson<VRSettings>(json) ?? new VRSettings(); }
            catch { return new VRSettings(); }
        }
        public void Save() { EditorPrefs.SetString(Key, JsonUtility.ToJson(this)); }
        public void SetTexturePreset(VRTexturePreset preset)
        {
            texturePreset = preset;
            switch (preset)
            {
                case VRTexturePreset.PCQuality: pc = 4096; android = 1024; ios = 1024; break;
                case VRTexturePreset.QuestBalanced: pc = 2048; android = 512; ios = 512; break;
                case VRTexturePreset.QuestPerformance: pc = 1024; android = 256; ios = 256; break;
            }
        }
        public void SetParticlePreset(VRParticlePreset preset)
        {
            particlePreset = preset;
            capParticles = true;
            capLifetime = preset == VRParticlePreset.QuestPerformance;
            disableTrails = preset == VRParticlePreset.QuestPerformance;
            disableCollision = preset == VRParticlePreset.QuestPerformance;
            disableNoise = preset == VRParticlePreset.QuestPerformance;
            disableLights = preset == VRParticlePreset.QuestPerformance;
            disableShadows = preset != VRParticlePreset.Conservative;
            disableSubEmitters = false;
            maxParticles = preset == VRParticlePreset.QuestPerformance ? 250 : 500;
            maxLifetime = 10f;
        }
        public int TargetMax { get { return target == VRTarget.Standalone ? pc : target == VRTarget.IOS ? ios : android; } }
        public string TargetName { get { return target == VRTarget.Standalone ? "Standalone" : target == VRTarget.IOS ? "iPhone" : "Android"; } }
        public void Sanitize()
        {
            pc = Mathf.Clamp(Mathf.ClosestPowerOfTwo(Mathf.Max(32, pc)), 32, 16384);
            android = Mathf.Clamp(Mathf.ClosestPowerOfTwo(Mathf.Max(32, android)), 32, 16384);
            ios = Mathf.Clamp(Mathf.ClosestPowerOfTwo(Mathf.Max(32, ios)), 32, 16384);
            maxParticles = Mathf.Max(1, maxParticles);
            maxLifetime = Mathf.Max(.01f, maxLifetime);
            maxLightRange = Mathf.Max(.01f, maxLightRange);
            quality = Mathf.Clamp(quality, 0, 100);
            aniso = Mathf.Clamp(aniso, 0, 16);
        }
    }
}
