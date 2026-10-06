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
            change |= settings.capLifetime && LifetimeNeedsCap(main.startLifetime, settings.maxLifetime);
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

            if (settings.capParticles)
                main.maxParticles = Mathf.Min(main.maxParticles, settings.maxParticles);

            if (settings.capLifetime)
            {
                var lifetime = main.startLifetime;
                if (CapLifetime(ref lifetime, settings.maxLifetime))
                    main.startLifetime = lifetime;
            }

            if (settings.disableTrails) { var m = system.trails; m.enabled = false; }
            if (settings.disableCollision) { var m = system.collision; m.enabled = false; }
            if (settings.disableNoise) { var m = system.noise; m.enabled = false; }
            if (settings.disableLights) { var m = system.lights; m.enabled = false; }
            if (settings.disableSubEmitters) { var m = system.subEmitters; m.enabled = false; }
            if (renderer && settings.disableShadows)
            {
                renderer.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                EditorUtility.SetDirty(renderer);
            }

            EditorUtility.SetDirty(system);
            return true;
        }

        static bool LifetimeNeedsCap(ParticleSystem.MinMaxCurve lifetime, float maximum)
        {
            switch (lifetime.mode)
            {
                case ParticleSystemCurveMode.Constant:
                    return lifetime.constant > maximum;
                case ParticleSystemCurveMode.TwoConstants:
                    return lifetime.constantMax > maximum || lifetime.constantMin > maximum;
                default:
                    // Curve-based lifetime data is intentionally preserved because
                    // rescaling authored curves would be a more destructive change.
                    return false;
            }
        }

        static bool CapLifetime(ref ParticleSystem.MinMaxCurve lifetime, float maximum)
        {
            if (!LifetimeNeedsCap(lifetime, maximum)) return false;

            if (lifetime.mode == ParticleSystemCurveMode.Constant)
            {
                lifetime.constant = Mathf.Min(lifetime.constant, maximum);
                return true;
            }

            if (lifetime.mode == ParticleSystemCurveMode.TwoConstants)
            {
                float nextMax = Mathf.Min(lifetime.constantMax, maximum);
                float nextMin = Mathf.Min(lifetime.constantMin, nextMax);
                lifetime.constantMax = nextMax;
                lifetime.constantMin = nextMin;
                return true;
            }

            return false;
        }
    }
}
