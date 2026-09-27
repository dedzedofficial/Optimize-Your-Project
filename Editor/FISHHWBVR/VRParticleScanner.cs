using System.Collections.Generic;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class VRParticleScanner : IVRScanner
    {
        public void ScanAsset(string path, VRSettings settings, List<VRIssue> issues)
        { foreach (var p in VRProjectScanner.PrefabObjects<ParticleSystem>(path)) Inspect(p, path, issues); }
        public void ScanScene(VRSettings settings, List<VRIssue> issues)
        { foreach (var p in VRProjectScanner.SceneObjects<ParticleSystem>()) Inspect(p, null, issues); }
        static void Inspect(ParticleSystem p, string path, List<VRIssue> issues)
        {
            var main = p.main;
            if (main.maxParticles > 2000) Add("Maximum particles: " + main.maxParticles, VRSeverity.Critical);
            else if (main.maxParticles > 500) Add("Maximum particles: " + main.maxParticles, VRSeverity.Warning);
            var emission = p.emission;
            if (emission.enabled && emission.rateOverTime.mode == ParticleSystemCurveMode.Constant && emission.rateOverTime.constant > 100)
                Add("High continuous emission: " + emission.rateOverTime.constant + "/s", VRSeverity.Warning);
            if (p.trails.enabled) Add("Trails enabled", VRSeverity.Warning);
            if (p.collision.enabled) Add("Collision enabled", VRSeverity.Warning);
            if (p.noise.enabled) Add("Noise enabled", VRSeverity.Info);
            if (p.lights.enabled) Add("Particle lights enabled", VRSeverity.Warning);
            if (p.subEmitters.enabled) Add("Sub emitters enabled", VRSeverity.Info);
            if (main.startSize3D || main.startRotation3D) Add("3D size or rotation", VRSeverity.Info);
            if (main.simulationSpace == ParticleSystemSimulationSpace.World) Add("World simulation space", VRSeverity.Info);
            if (main.startLifetime.mode == ParticleSystemCurveMode.Constant && main.startLifetime.constant > 10) Add("Long lifetime: " + main.startLifetime.constant + "s", VRSeverity.Info);
            if (main.startSize.mode == ParticleSystemCurveMode.Constant && main.startSize.constant > 5) Add("Large start size", VRSeverity.Warning);
            var r = p.GetComponent<ParticleSystemRenderer>();
            if (r)
            {
                if (r.renderMode == ParticleSystemRenderMode.Mesh) Add("Mesh particle renderer", VRSeverity.Warning);
                if (r.shadowCastingMode != UnityEngine.Rendering.ShadowCastingMode.Off) Add("Casts shadows", VRSeverity.Warning);
                if (r.sortMode != ParticleSystemSortMode.None) Add("Particle sorting enabled", VRSeverity.Info);
                if (r.sharedMaterial && r.sharedMaterial.renderQueue >= 3000) Add("Transparent material; inspect overdraw on screen", VRSeverity.Info);
            }
            void Add(string message, VRSeverity severity) { issues.Add(new VRIssue(severity, VRCategory.Particle, p.name + ": " + message, p, path, true)); }
        }
    }
}
