using System.Collections.Generic;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class VRLightScanner : IVRScanner
    {
        public void ScanAsset(string path, VRSettings settings, List<VRIssue> issues)
        { foreach (var light in VRProjectScanner.PrefabObjects<Light>(path)) Inspect(light, path, issues); }
        public void ScanScene(VRSettings settings, List<VRIssue> issues)
        {
            int realtime = 0;
            foreach (var light in VRProjectScanner.SceneObjects<Light>())
            {
                if (light.enabled && light.lightmapBakeType == LightmapBakeType.Realtime) realtime++;
                Inspect(light, null, issues);
            }
            if (realtime > 8) issues.Add(new VRIssue(VRSeverity.Warning, VRCategory.Light, realtime + " realtime lights across loaded scenes.", null));
        }
        static void Inspect(Light light, string path, List<VRIssue> issues)
        {
            if (!light.enabled) return;
            if (light.lightmapBakeType == LightmapBakeType.Realtime)
                Add("Realtime " + light.type + " light", VRSeverity.Info);
            if (light.shadows != LightShadows.None)
                Add("Shadows enabled (" + light.shadows + ", " + light.shadowResolution + " resolution)", light.type == LightType.Point ? VRSeverity.Critical : VRSeverity.Warning);
            if (light.type != LightType.Directional && light.range > 30) Add("Range " + light.range + "m", VRSeverity.Warning);
            if (light.lightmapBakeType == LightmapBakeType.Mixed && light.shadows != LightShadows.None) Add("Mixed light with shadows", VRSeverity.Info);
            void Add(string message, VRSeverity severity) { issues.Add(new VRIssue(severity, VRCategory.Light, light.name + ": " + message, light, path, true)); }
        }
    }
}
