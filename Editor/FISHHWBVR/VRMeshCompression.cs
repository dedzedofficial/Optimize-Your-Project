using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class VRMeshCompressionEntry
    {
        public string Path;
        public bool Include = true;
        public ModelImporterMeshCompression Current;
        public int Renderers;
    }

    internal static class VRMeshCompression
    {
        internal static List<VRMeshCompressionEntry> Collect(GameObject root)
        {
            var entries = new Dictionary<string, VRMeshCompressionEntry>(StringComparer.Ordinal);
            IEnumerable<MeshFilter> filters = root ? (IEnumerable<MeshFilter>)root.GetComponentsInChildren<MeshFilter>(true) : VRProjectScanner.SceneObjects<MeshFilter>();
            IEnumerable<SkinnedMeshRenderer> skins = root ? (IEnumerable<SkinnedMeshRenderer>)root.GetComponentsInChildren<SkinnedMeshRenderer>(true) : VRProjectScanner.SceneObjects<SkinnedMeshRenderer>();
            foreach (var filter in filters) Add(filter.sharedMesh);
            foreach (var skin in skins) Add(skin.sharedMesh);
            var result = new List<VRMeshCompressionEntry>(entries.Values);
            result.Sort((a, b) => string.CompareOrdinal(a.Path, b.Path));
            return result;

            void Add(Mesh mesh)
            {
                if (!mesh) return;
                var path = AssetDatabase.GetAssetPath(mesh);
                if (string.IsNullOrEmpty(path) || !path.StartsWith("Assets/", StringComparison.Ordinal)) return;
                var importer = AssetImporter.GetAtPath(path) as ModelImporter;
                if (!importer) return;
                if (!entries.TryGetValue(path, out var entry))
                {
                    entry = new VRMeshCompressionEntry { Path = path, Current = importer.meshCompression };
                    entries.Add(path, entry);
                }
                entry.Renderers++;
            }
        }
    }
}
