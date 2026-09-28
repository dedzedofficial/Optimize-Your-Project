using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal enum VRSeverity { Info, Warning, Critical }
    internal enum VRCategory { Texture, Particle, Light, Mesh, Material }
    internal sealed class VRIssue
    {
        public readonly VRSeverity Severity;
        public readonly VRCategory Category;
        public readonly string Message;
        public readonly Object Target;
        public readonly string AssetPath;
        public readonly bool CanOptimize;
        public VRIssue(VRSeverity severity, VRCategory category, string message, Object target, string assetPath = null, bool canOptimize = false)
        { Severity = severity; Category = category; Message = message; Target = target; AssetPath = assetPath; CanOptimize = canOptimize; }
    }
}
