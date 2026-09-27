using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class VRMeshScanner : IVRScanner
    {
        public void ScanAsset(string path, VRSettings settings, List<VRIssue> issues)
        {
            var importer = AssetImporter.GetAtPath(path) as ModelImporter;
            if (importer == null) return;
            var meshes = AssetDatabase.LoadAllAssetsAtPath(path);
            foreach (var asset in meshes)
            {
                var mesh = asset as Mesh;
                if (!mesh) continue;
                int triangles = 0;
                for (int i = 0; i < mesh.subMeshCount; i++)
                    if (mesh.GetTopology(i) == MeshTopology.Triangles) triangles += (int)(mesh.GetIndexCount(i) / 3);
                if (mesh.vertexCount > 100000 || triangles > 200000)
                    issues.Add(new VRIssue(mesh.vertexCount > 250000 ? VRSeverity.Critical : VRSeverity.Warning, VRCategory.Mesh,
                        mesh.name + ": " + mesh.vertexCount + " vertices, " + triangles + " triangles.", mesh, path));
                if (mesh.vertexCount > 65535 && mesh.indexFormat == UnityEngine.Rendering.IndexFormat.UInt32)
                    issues.Add(new VRIssue(VRSeverity.Info, VRCategory.Mesh, mesh.name + ": 32-bit indices required by large vertex count.", mesh, path));
                var bounds = mesh.bounds.size;
                if (Mathf.Max(bounds.x, bounds.y, bounds.z) > 1000)
                    issues.Add(new VRIssue(VRSeverity.Warning, VRCategory.Mesh, mesh.name + ": unusually large bounds " + bounds + ".", mesh, path));
            }
            if (importer.isReadable) issues.Add(new VRIssue(VRSeverity.Info, VRCategory.Mesh, "Read/Write enabled; check whether runtime mesh access is necessary.", AssetDatabase.LoadMainAssetAtPath(path), path));
            if (importer.meshCompression == ModelImporterMeshCompression.Off) issues.Add(new VRIssue(VRSeverity.Info, VRCategory.Mesh, "Mesh compression disabled; evaluate visual impact before changing.", AssetDatabase.LoadMainAssetAtPath(path), path));
            if (!importer.optimizeMeshPolygons || !importer.optimizeMeshVertices) issues.Add(new VRIssue(VRSeverity.Info, VRCategory.Mesh, "Import mesh optimization partially disabled.", AssetDatabase.LoadMainAssetAtPath(path), path));
        }
        public void ScanScene(VRSettings settings, List<VRIssue> issues) { }
    }
}
