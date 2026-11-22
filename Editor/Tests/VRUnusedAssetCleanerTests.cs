using System;
using System.Collections.Generic;
using System.IO;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    public sealed class VRUnusedAssetCleanerTests
    {
        string folder;
        string ownerFolder;
        string texturePath;
        string historyBackup;

        [SetUp]
        public void SetUp()
        {
            historyBackup = EditorJsonUtility.ToJson(VRImportHistory.instance);
            folder = "Assets/OYPUnusedTest_" + Guid.NewGuid().ToString("N");
            ownerFolder = "Assets/OYPUnusedOwner_" + Guid.NewGuid().ToString("N");
            AssetDatabase.CreateFolder("Assets", Path.GetFileName(folder));
            AssetDatabase.CreateFolder("Assets", Path.GetFileName(ownerFolder));
            texturePath = folder + "/Unused.png";

            var texture = new Texture2D(8, 8, TextureFormat.RGBA32, false);
            try { File.WriteAllBytes(texturePath, texture.EncodeToPNG()); }
            finally { UnityEngine.Object.DestroyImmediate(texture); }
            AssetDatabase.ImportAsset(texturePath, ImportAssetOptions.ForceSynchronousImport);
        }

        [TearDown]
        public void TearDown()
        {
            if (AssetDatabase.IsValidFolder(folder)) AssetDatabase.DeleteAsset(folder);
            if (AssetDatabase.IsValidFolder(ownerFolder)) AssetDatabase.DeleteAsset(ownerFolder);
            EditorJsonUtility.FromJsonOverwrite(historyBackup, VRImportHistory.instance);
            VRImportHistory.instance.Persist();
        }

        [Test]
        public void UnreferencedTextureIsAReportCandidate()
        {
            List<string> result = VRUnusedAssetCleaner.FindUnused(folder, out int protectedAssets, out int unsupported);
            CollectionAssert.Contains(result, texturePath);
            Assert.AreEqual(0, protectedAssets);
            Assert.AreEqual(0, unsupported);
            Assert.IsTrue(File.Exists(texturePath), "Scanning must not delete files.");
        }

        [Test]
        public void ExplicitImporterHistoryProtectionIsHonored()
        {
            VRImportHistory.instance.SetProtection(new[] { texturePath }, true);

            var result = VRUnusedAssetCleaner.FindUnused(folder, out int protectedAssets, out _);
            CollectionAssert.DoesNotContain(result, texturePath);
            Assert.AreEqual(1, protectedAssets);
            Assert.IsTrue(File.Exists(texturePath));
        }

        [Test]
        public void SerializedReferenceOutsideScanFolderProtectsTexture()
        {
            var fixture = ScriptableObject.CreateInstance<OYPUnusedReferenceFixture>();
            fixture.Texture = AssetDatabase.LoadAssetAtPath<Texture2D>(texturePath);
            string ownerPath = ownerFolder + "/UsesTexture.asset";
            AssetDatabase.CreateAsset(fixture, ownerPath);
            AssetDatabase.SaveAssets();

            CollectionAssert.Contains(AssetDatabase.GetDependencies(ownerPath, false), texturePath);
            var result = VRUnusedAssetCleaner.FindUnused(folder, out _, out _);
            CollectionAssert.DoesNotContain(result, texturePath);
        }

        [Test]
        public void ResourcesDirectoryIsProtected()
        {
            AssetDatabase.CreateFolder(folder, "Resources");
            string runtimePath = folder + "/Resources/Runtime.png";
            File.Copy(texturePath, runtimePath);
            AssetDatabase.ImportAsset(runtimePath, ImportAssetOptions.ForceSynchronousImport);

            var result = VRUnusedAssetCleaner.FindUnused(folder, out int protectedAssets, out _);
            CollectionAssert.DoesNotContain(result, runtimePath);
            CollectionAssert.Contains(result, texturePath);
            Assert.AreEqual(1, protectedAssets);
        }

        [Test]
        public void CandidateSetChangesRequireAnotherReview()
        {
            var reviewed = new List<string> { "Assets/A.png", "Assets/B.png" };
            Assert.IsTrue(VRUnusedAssetCleaner.CandidateSetUnchanged(
                reviewed, new List<string> { "assets/b.png", "Assets/A.png" }));
            Assert.IsFalse(VRUnusedAssetCleaner.CandidateSetUnchanged(
                reviewed, new List<string> { "Assets/A.png", "Assets/C.png" }));
            Assert.IsFalse(VRUnusedAssetCleaner.CandidateSetUnchanged(
                reviewed, new List<string> { "Assets/A.png" }));
            Assert.IsFalse(VRUnusedAssetCleaner.CandidateSetUnchanged(
                reviewed, new List<string> { "Assets/A.png", "Assets/A.png" }));
        }
    }
}
