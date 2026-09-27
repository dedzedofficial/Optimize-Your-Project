using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRParticleOptimizer
    {
        public static bool Optimize(ParticleSystem system, VRSettings settings)
        {
            if (!system) return false;
            settings.Sanitize();
            var main = system.main;
            bool change = settings.capParticles && main.maxParticles > settings.maxParticles;
            change |= settings.capLifetime && main.startLifetime.mode == ParticleSystemCurveMode.Constant && main.startLifetime.constant > settings.maxLifetime;
            change |= settings.disableTrails && system.trails.enabled;
            change |= settings.disableCollision && system.collision.enabled;
            change |= settings.disableNoise && system.noise.enabled;
            change |= settings.disableLights && system.lights.enabled;
            change |= settings.disableSubEmitters && system.subEmitters.enabled;
            var renderer = system.GetComponent<ParticleSystemRenderer>();
            change |= settings.disableShadows && renderer && renderer.shadowCastingMode != UnityEngine.Rendering.ShadowCastingMode.Off;
            if (!change) return false;
            Undo.RegisterCompleteObjectUndo(system, "Optimize Particle System");
            if (renderer && settings.disableShadows) Undo.RecordObject(renderer, "Optimize Particle Shadows");
            if (settings.capParticles) main.maxParticles = Mathf.Min(main.maxParticles, settings.maxParticles);
            if (settings.capLifetime && main.startLifetime.mode == ParticleSystemCurveMode.Constant && main.startLifetime.constant > settings.maxLifetime)
                main.startLifetime = settings.maxLifetime;
            if (settings.disableTrails) { var m = system.trails; m.enabled = false; }
            if (settings.disableCollision) { var m = system.collision; m.enabled = false; }
            if (settings.disableNoise) { var m = system.noise; m.enabled = false; }
            if (settings.disableLights) { var m = system.lights; m.enabled = false; }
            if (settings.disableSubEmitters) { var m = system.subEmitters; m.enabled = false; }
            if (renderer && settings.disableShadows) { renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off; EditorUtility.SetDirty(renderer); }
            EditorUtility.SetDirty(system);
            return true;
        }
    }
}
