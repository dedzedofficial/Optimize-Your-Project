using System;
using System.IO;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    public sealed class VRImportHistoryTests
    {
        string folder, path, historyBackup;

        [SetUp]
        public void SetUp()
        {
            historyBackup = EditorJsonUtility.ToJson(VRImportHistory.instance);
            folder = "Assets/OYPHistoryTest_" + Guid.NewGuid().ToString("N");
            AssetDatabase.CreateFolder("Assets", Path.GetFileName(folder));
            path = folder + "/Sample.png";
            var texture = new Texture2D(8, 8, TextureFormat.RGBA32, false);
            File.WriteAllBytes(path, texture.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(texture);
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
        }

        [TearDown]
        public void TearDown()
        {
            AssetDatabase.DeleteAsset(folder);
            EditorJsonUtility.FromJsonOverwrite(historyBackup, VRImportHistory.instance);
            VRImportHistory.instance.Persist();
        }

        VRActionOutcome ChangeFilter()
        {
            var importer = (TextureImporter)AssetImporter.GetAtPath(path);
            importer.filterMode = importer.filterMode == FilterMode.Point ? FilterMode.Bilinear : FilterMode.Point;
            importer.SaveAndReimport();
            return VRActionOutcome.Changed;
        }

        [Test]
        public void UnchangedAssetDoesNotRunAgain()
        {
            Assert.AreEqual(VRActionOutcome.Changed, new VRImportBatch().Apply(path, "test", "policy", ChangeFilter));
            bool called = false;
            var batch = new VRImportBatch();
            Assert.AreEqual(VRActionOutcome.Unchanged, batch.Apply(path, "test", "policy", () => { called = true; return ChangeFilter(); }));
            Assert.IsFalse(called);
            Assert.AreEqual(1, batch.Cached);
        }

        [Test]
        public void ManualImporterEditIsPreserved()
        {
            new VRImportBatch().Apply(path, "test", "policy", ChangeFilter);
            var importer = (TextureImporter)AssetImporter.GetAtPath(path);
            importer.wrapMode = importer.wrapMode == TextureWrapMode.Clamp ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
            var manualWrap = importer.wrapMode;
            importer.SaveAndReimport();
            var batch = new VRImportBatch();
            Assert.AreEqual(VRActionOutcome.Skipped, batch.Apply(path, "test", "new-policy", ChangeFilter));
            Assert.AreEqual(1, batch.ManualEdits);
            Assert.AreEqual(manualWrap, ((TextureImporter)AssetImporter.GetAtPath(path)).wrapMode);
        }

        [Test]
        public void TrialWithNoMeasuredSavingRestoresSettings()
        {
            var before = ((TextureImporter)AssetImporter.GetAtPath(path)).filterMode;
            var batch = new VRImportBatch();
            Assert.AreEqual(VRActionOutcome.Skipped, batch.Apply(path, "trial", "policy", () => VRActionOutcome.Changed, true));
            Assert.AreEqual(1, batch.Rejected);
            Assert.AreEqual(before, ((TextureImporter)AssetImporter.GetAtPath(path)).filterMode);
        }

        [Test]
        public void ProtectedAssetDoesNotRun()
        {
            VRImportHistory.instance.SetProtection(new[] { path }, true);
            var batch = new VRImportBatch();
            Assert.AreEqual(VRActionOutcome.Skipped, batch.Apply(path, "test", "policy", ChangeFilter));
            Assert.AreEqual(1, batch.Protected);
        }

        [Test]
        public void RestoreChecksForLaterEdits()
        {
            new VRImportBatch().Apply(path, "test", "policy", ChangeFilter);
            var importer = (TextureImporter)AssetImporter.GetAtPath(path);
            importer.wrapMode = importer.wrapMode == TextureWrapMode.Clamp ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
            var manualWrap = importer.wrapMode;
            importer.SaveAndReimport();
            Assert.That(VRImportHistory.instance.RestoreLastBatch(), Does.Contain("1 later-edit/source conflicts"));
            Assert.AreEqual(manualWrap, ((TextureImporter)AssetImporter.GetAtPath(path)).wrapMode);
        }

        [Test]
        public void FailedImportRestoresTheBeforeSettings()
        {
            var before = ((TextureImporter)AssetImporter.GetAtPath(path)).filterMode;
            Assert.Throws<InvalidOperationException>(() => new VRImportBatch().Apply(path, "test", "policy", () =>
            {
                ChangeFilter();
                throw new InvalidOperationException("Simulated failure after reimport");
            }));
            Assert.AreEqual(before, ((TextureImporter)AssetImporter.GetAtPath(path)).filterMode);
        }

        [Test]
        public void SuccessfulImportCanBeRestored()
        {
            var before = ((TextureImporter)AssetImporter.GetAtPath(path)).filterMode;
            new VRImportBatch().Apply(path, "test", "policy", ChangeFilter);
            Assert.That(VRImportHistory.instance.RestoreLastBatch(), Does.Contain("1 restored"));
            Assert.AreEqual(before, ((TextureImporter)AssetImporter.GetAtPath(path)).filterMode);
        }
    }
}
