using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRLightOptimizer
    {
        // Called by the confirmed realtime shadow batch.
        public static bool Optimize(Light light, VRSettings settings)
        {
            if (!light || !light.enabled || light.lightmapBakeType != LightmapBakeType.Realtime)
                return false;
            if (light.shadows == LightShadows.None)
                return false;

            Undo.RecordObject(light, "Optimize Light");
            light.shadows = LightShadows.None;
            PrefabUtility.RecordPrefabInstancePropertyModifications(light);
            EditorUtility.SetDirty(light);
            return true;
        }
    }
}
