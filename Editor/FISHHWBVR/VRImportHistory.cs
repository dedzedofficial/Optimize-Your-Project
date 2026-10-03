using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Runtime.CompilerServices;
using UnityEditor;
using UnityEngine;
using UnityEngine.Profiling;

[assembly: InternalsVisibleTo("FISHHWB.VROptimizer.Editor.Tests")]

namespace FISHHWB.VROptimizer
{
    [Serializable]
    internal sealed class VRImportRecord
    {
        public string Guid, Job, Policy, Source, After, BeforeMeta, Batch;
    }

    [FilePath("ProjectSettings/OptimizeYourProjectHistory.asset", FilePathAttribute.Location.ProjectFolder)]
    internal sealed class VRImportHistory : ScriptableSingleton<VRImportHistory>
    {
        [SerializeField] List<VRImportRecord> records = new List<VRImportRecord>();
        [SerializeField] List<VRImportRecord> lastBatch = new List<VRImportRecord>();
        [SerializeField] List<string> protectedAssets = new List<string>();
        [SerializeField] string lastBatchId;

        internal void Persist() => Save(true);

        internal static string Fingerprint(string path)
        {
            using (var sha = SHA256.Create())
            using (var stream = File.OpenRead(path))
                return Convert.ToBase64String(sha.ComputeHash(stream));
        }

        internal bool Protected(string path) => protectedAssets.Contains(AssetDatabase.AssetPathToGUID(path));

        internal VRImportRecord FindAny(string guid) => records.Find(x => x.Guid == guid);

        internal VRImportRecord Find(string guid, string job) => records.Find(x => x.Guid == guid && x.Job == job);

        internal void Remember(VRImportRecord record, string beforeMeta, bool changed)
        {
            // Our own changes must not look like a manual edit to another owning workflow.
            foreach (var previous in records)
                if (previous.Guid == record.Guid) previous.After = record.After;
            records.RemoveAll(x => x.Guid == record.Guid && x.Job == record.Job);
            records.Add(record);
            if (changed)
            {
                if (lastBatchId != record.Batch) { lastBatch.Clear(); lastBatchId = record.Batch; }
                lastBatch.Add(new VRImportRecord { Guid = record.Guid, Source = record.Source,
                    Job = record.Job, After = record.After, BeforeMeta = beforeMeta });
            }
            Persist();
        }

        internal void SetProtection(IEnumerable<string> paths, bool protect)
        {
            foreach (var path in paths)
            {
                string guid = AssetDatabase.AssetPathToGUID(path);
                if (string.IsNullOrEmpty(guid)) continue;
                if (protect && !protectedAssets.Contains(guid)) protectedAssets.Add(guid);
                if (!protect) protectedAssets.Remove(guid);
            }
            Persist();
        }

        internal void RebaseMetadata(string guid, string after)
        {
            foreach (var record in records)
                if (record.Guid == guid) record.After = after;
            Persist();
        }

        internal void Forget(IEnumerable<string> paths)
        {
            foreach (var path in paths)
            {
                string guid = AssetDatabase.AssetPathToGUID(path);
                records.RemoveAll(x => x.Guid == guid);
            }
            Persist();
        }

        internal string RestoreLastBatch()
        {
            int restored = 0, conflicts = 0, failed = 0;
            for (int i = lastBatch.Count - 1; i >= 0; i--)
            {
                var record = lastBatch[i];
                string path = AssetDatabase.GUIDToAssetPath(record.Guid);
                if (!File.Exists(path) || !File.Exists(path + ".meta") ||
                    Fingerprint(path) != record.Source || Fingerprint(path + ".meta") != record.After)
                { conflicts++; continue; }
                try
                {
                    File.WriteAllText(path + ".meta", record.BeforeMeta);
                    AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate);
                    records.RemoveAll(x => x.Guid == record.Guid);
                    lastBatch.RemoveAt(i);
                    restored++;
                }
                catch (Exception error) { failed++; Debug.LogException(error); }
            }
            Persist();
            return "Restore import batch: " + restored + " restored, " + conflicts + " later-edit/source conflicts, " + failed + " failed.";
        }

        internal static List<string> SelectedPaths()
        {
            var paths = new HashSet<string>(StringComparer.Ordinal);
            foreach (var selected in Selection.objects)
            {
                Add(AssetDatabase.GetAssetPath(selected));
                var go = selected as GameObject;
                if (go)
                    foreach (var renderer in go.GetComponentsInChildren<Renderer>(true))
                    {
                        var filter = renderer.GetComponent<MeshFilter>();
                        Add(AssetDatabase.GetAssetPath(filter ? filter.sharedMesh :
                            renderer is SkinnedMeshRenderer skin ? skin.sharedMesh : null));
                        foreach (var material in renderer.sharedMaterials)
                            AddMaterial(material);
                    }
                if (selected is Material mat) AddMaterial(mat);
            }
            return new List<string>(paths);

            void Add(string path)
            {
                if (string.IsNullOrEmpty(path) || !path.StartsWith("Assets/", StringComparison.Ordinal)) return;
                var importer = AssetImporter.GetAtPath(path);
                if (importer is TextureImporter || importer is ModelImporter) paths.Add(path);
            }
            void AddMaterial(Material material)
            {
                if (!material) return;
                foreach (var property in material.GetTexturePropertyNames())
                    Add(AssetDatabase.GetAssetPath(material.GetTexture(property)));
            }
        }
    }

    internal sealed class VRImportBatch
    {
        readonly string id = System.Guid.NewGuid().ToString("N");
        internal int Cached, Protected, ManualEdits, Rejected;
        internal long MemoryBefore, MemoryAfter;

        internal VRActionOutcome Apply(string path, string job, string policy,
            Func<VRActionOutcome> apply, bool testMemory = false)
        {
            if (!File.Exists(path) || !File.Exists(path + ".meta")) return VRActionOutcome.Unsupported;
            var history = VRImportHistory.instance;
            if (history.Protected(path)) { Protected++; return VRActionOutcome.Skipped; }
            string guid = AssetDatabase.AssetPathToGUID(path);
            string source = VRImportHistory.Fingerprint(path);
            string state = VRImportHistory.Fingerprint(path + ".meta");
            var previous = history.Find(guid, job);
            var owner = previous ?? history.FindAny(guid);
            if (owner != null && state != owner.After)
            { ManualEdits++; Debug.Log("Optimize Your Project preserved manual importer edits: " + path); return VRActionOutcome.Skipped; }
            if (previous != null && source == previous.Source && policy == previous.Policy)
            { Cached++; return VRActionOutcome.Unchanged; }
            string beforeMeta = File.ReadAllText(path + ".meta");
            long before = testMemory ? Measure(path) : 0;
            VRActionOutcome outcome;
            try
            {
                outcome = apply();
                if (outcome == VRActionOutcome.Unsupported || outcome == VRActionOutcome.Skipped) return outcome;
                long after = testMemory ? Measure(path) : 0;
                if (testMemory && outcome == VRActionOutcome.Changed && (before <= 0 || after <= 0 || after >= before))
                {
                    Restore();
                    Rejected++;
                    Debug.Log("Optimize Your Project restored trial with no verified native asset-memory saving: " + path);
                    // Do not cache a rejected trial as an accepted optimization.
                    return VRActionOutcome.Skipped;
                }
                if (testMemory) { MemoryBefore += before; MemoryAfter += after; }
                history.Remember(new VRImportRecord { Guid = guid, Job = job, Policy = policy,
                    Source = source, After = VRImportHistory.Fingerprint(path + ".meta"), Batch = id },
                    beforeMeta, outcome == VRActionOutcome.Changed);
                return outcome;
            }
            catch
            {
                Restore();
                throw;
            }

            void Restore()
            {
                if (VRImportHistory.Fingerprint(path) != source)
                    throw new InvalidOperationException("Source changed during batch; importer restoration requires review: " + path);
                File.WriteAllText(path + ".meta", beforeMeta);
                AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceUpdate);
                history.RebaseMetadata(guid, VRImportHistory.Fingerprint(path + ".meta"));
            }
        }

        static long Measure(string path)
        {
            long bytes = 0;
            foreach (var asset in AssetDatabase.LoadAllAssetsAtPath(path))
                if (asset is Texture || asset is Mesh)
                    bytes += Profiler.GetRuntimeMemorySizeLong(asset);
            return bytes;
        }

        internal string Details(bool tested = false)
        {
            return "\nAlready processed: " + Cached + " | Protected: " + Protected +
                " | Manual edits preserved: " + ManualEdits + " | Trials restored: " + Rejected +
                (tested ? "\nSampled native asset memory: " + MemoryBefore + " -> " + MemoryAfter +
                    " bytes (processed samples only; not player FPS or visual-quality validation)." : "");
        }
    }
}
