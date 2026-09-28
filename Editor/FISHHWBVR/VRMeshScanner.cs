using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class VRMeshScanner : IVRScanner
    {
        public void ScanAsset(string path, VRSettings settings, List<VRIssue> issues) { }

        public void ScanScene(VRSettings settings, List<VRIssue> issues)
        {
            foreach (var filter in VRProjectScanner.SceneObjects<MeshFilter>())
                Inspect(filter.sharedMesh, filter.gameObject, issues);
            foreach (var renderer in VRProjectScanner.SceneObjects<SkinnedMeshRenderer>())
                Inspect(renderer.sharedMesh, renderer.gameObject, issues);
        }

        static void Inspect(Mesh mesh, GameObject owner, List<VRIssue> issues)
        {
            if (!mesh || !owner) return;
            int triangles = 0;
            for (int i = 0; i < mesh.subMeshCount; i++)
                if (mesh.GetTopology(i) == MeshTopology.Triangles) triangles += (int)(mesh.GetIndexCount(i) / 3);
            if (mesh.vertexCount > 100000 || triangles > 200000)
                Add(mesh.vertexCount > 250000 ? VRSeverity.Critical : VRSeverity.Warning,
                    mesh.vertexCount + " vertices, " + triangles + " triangles");
            var bounds = mesh.bounds.size;
            if (Mathf.Max(bounds.x, bounds.y, bounds.z) > 1000)
                Add(VRSeverity.Warning, "Large mesh bounds: " + bounds);
            if (mesh.vertexCount > 65535 && mesh.indexFormat == UnityEngine.Rendering.IndexFormat.UInt32)
                Add(VRSeverity.Info, "Uses 32-bit indices");

            var importer = AssetImporter.GetAtPath(AssetDatabase.GetAssetPath(mesh)) as ModelImporter;
            if (importer == null) return;
            if (importer.isReadable) Add(VRSeverity.Info, "Read/Write enabled on imported model");
            if (!importer.optimizeMeshPolygons || !importer.optimizeMeshVertices) Add(VRSeverity.Info, "Import mesh optimization partially disabled");

            void Add(VRSeverity severity, string message)
            {
                issues.Add(new VRIssue(severity, VRCategory.Mesh, owner.name + " / " + mesh.name + ": " + message, owner));
            }
        }
    }
}
