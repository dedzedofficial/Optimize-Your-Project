using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal sealed class VRTextureChange
    {
        public string Path;
        public Texture Texture;
        public bool Include = true;
        public int[] Before = new int[3];
        public int[] After = new int[3];
        public bool Changed;
    }

    internal static class VRAvatarWorkflow
    {
        static readonly string[] Platforms = { "Standalone", "Android", "iPhone" };
        internal static bool EditableRoot(GameObject root)
        { return root && root.scene.IsValid() && root.scene.isLoaded && !EditorUtility.IsPersistent(root); }

        internal static HashSet<Texture> ReferencedTextures(GameObject root)
        {
            var textures = new HashSet<Texture>();
            if (!root) return textures;
            foreach (var renderer in root.GetComponentsInChildren<Renderer>(true))
                foreach (var material in renderer.sharedMaterials)
                {
                    if (!material) continue;
                    foreach (var property in material.GetTexturePropertyNames())
                    {
                        var texture = material.GetTexture(property);
                        if (texture) textures.Add(texture);
                    }
                }
            return textures;
        }

        internal static List<VRTextureChange> CollectTextures(GameObject root, VRSettings settings)
        {
            var paths = new HashSet<string>(StringComparer.Ordinal);
            if (root)
            {
                foreach (var renderer in root.GetComponentsInChildren<Renderer>(true))
                    foreach (var material in renderer.sharedMaterials)
                    {
                        if (!material) continue;
                        foreach (var property in material.GetTexturePropertyNames())
                        {
                            var texture = material.GetTexture(property);
                            if (texture) paths.Add(AssetDatabase.GetAssetPath(texture));
                        }
                    }
            }
            else foreach (var guid in AssetDatabase.FindAssets("t:Texture", new[] { "Assets" }))
                paths.Add(AssetDatabase.GUIDToAssetPath(guid));
            var changes = new List<VRTextureChange>();
            foreach (var path in paths)
            {
                if (string.IsNullOrEmpty(path) || !path.StartsWith("Assets/", StringComparison.Ordinal)) continue;
                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (!importer || importer.textureShape != TextureImporterShape.Texture2D ||
                    (importer.textureType != TextureImporterType.Default && importer.textureType != TextureImporterType.NormalMap)) continue;
                var entry = new VRTextureChange { Path = path, Texture = AssetDatabase.LoadAssetAtPath<Texture>(path) };
                int[] caps = { settings.pc, settings.android, settings.ios };
                for (int i = 0; i < 3; i++)
                {
                    var platform = importer.GetPlatformTextureSettings(Platforms[i]);
                    entry.Before[i] = platform.overridden ? platform.maxTextureSize : importer.maxTextureSize;
                    // 0.6.5 retains stricter existing overrides; the preview shows effective caps.
                    entry.After[i] = platform.overridden && platform.maxTextureSize > 0 ? Mathf.Min(platform.maxTextureSize, caps[i]) : caps[i];
                    entry.Changed |= !platform.overridden || platform.maxTextureSize != entry.After[i];
                }
                changes.Add(entry);
            }
            changes.Sort((a, b) => string.CompareOrdinal(a.Path, b.Path));
            return changes;
        }

        internal static List<VRIssue> Check(GameObject root, out string overview)
        {
            var issues = new List<VRIssue>();
            var textures = new HashSet<Texture>();
            var materials = new Dictionary<Material, int>();
            int slots = 0, triangles = 0, skinned = 0;
            foreach (var renderer in root.GetComponentsInChildren<Renderer>(true))
            {
                if (renderer is SkinnedMeshRenderer skin)
                {
                    skinned++;
                    if (skin.sharedMesh) triangles += CountTriangles(skin.sharedMesh);
                }
                foreach (var material in renderer.sharedMaterials)
                {
                    slots++;
                    if (!material)
                    {
                        issues.Add(new VRIssue(VRSeverity.Info, VRCategory.Material, renderer.name + ": Empty material slot", renderer));
                        continue;
                    }
                    materials[material] = materials.TryGetValue(material, out int count) ? count + 1 : 1;
                    foreach (var property in material.GetTexturePropertyNames())
                    {
                        var texture = material.GetTexture(property);
                        if (texture) textures.Add(texture);
                    }
                }
                if (renderer.sharedMaterials.Length > 4)
                    issues.Add(new VRIssue(VRSeverity.Info, VRCategory.Material, renderer.name + ": " + renderer.sharedMaterials.Length + " material slots", renderer));
            }
            foreach (var pair in materials)
                if (pair.Value > 1) issues.Add(new VRIssue(VRSeverity.Info, VRCategory.Material,
                    pair.Key.name + " used in " + pair.Value + " slots", pair.Key));
            int particles = root.GetComponentsInChildren<ParticleSystem>(true).Length;
            int lights = root.GetComponentsInChildren<Light>(true).Length;
            overview = "Textures: " + textures.Count + " | Materials: " + materials.Count + " | Slots: " + slots +
                       " | Skinned meshes: " + skinned + " | Triangles: " + triangles + " | Particles: " + particles + " | Lights: " + lights;
            foreach (var texture in textures)
                if (Mathf.Max(texture.width, texture.height) >= 4096)
                    issues.Add(new VRIssue(VRSeverity.Warning, VRCategory.Texture, texture.name + ": " + texture.width + " x " + texture.height, texture));
            foreach (var particle in root.GetComponentsInChildren<ParticleSystem>(true))
                if (particle.main.maxParticles > 500)
                    issues.Add(new VRIssue(VRSeverity.Warning, VRCategory.Particle, particle.name + ": max " + particle.main.maxParticles + " particles", particle));
            return issues;
        }

        static int CountTriangles(Mesh mesh)
        {
            int count = 0;
            for (int i = 0; i < mesh.subMeshCount; i++)
                if (mesh.GetTopology(i) == MeshTopology.Triangles) count += (int)(mesh.GetIndexCount(i) / 3);
            return count;
        }
    }
}
