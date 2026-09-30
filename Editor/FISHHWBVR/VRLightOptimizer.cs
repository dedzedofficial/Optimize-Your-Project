using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRLightOptimizer
    {
        // Called by the confirmed realtime shadow batch.
        public static bool Optimize(Light light, VRSettings settings)
        {
            if (!light) return false;
            bool shadows = light.shadows != LightShadows.None;
            if (!shadows) return false;
            Undo.RecordObject(light, "Optimize Light");
            if (shadows) light.shadows = LightShadows.None;
            EditorUtility.SetDirty(light);
            return true;
        }
    }
}
