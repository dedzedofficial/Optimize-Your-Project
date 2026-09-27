using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRLightOptimizer
    {
        // Called only from an individual audit row after an explicit confirmation.
        public static bool Optimize(Light light, VRSettings settings)
        {
            if (!light) return false;
            bool shadows = light.shadows != LightShadows.None;
            bool range = settings.capLightRange && light.type != LightType.Directional && light.range > settings.maxLightRange;
            if (!shadows && !range) return false;
            Undo.RecordObject(light, "Optimize VR Light");
            if (shadows) light.shadows = LightShadows.None;
            if (range) light.range = settings.maxLightRange;
            EditorUtility.SetDirty(light);
            return true;
        }
    }
}
