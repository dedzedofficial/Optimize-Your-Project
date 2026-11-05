using System;
using System.IO;
using NUnit.Framework;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    public sealed class VRDeveloperReviewTests
    {
        string folder;

        [SetUp]
        public void SetUp()
        {
            folder = "Assets/OYPReviewTest_" + Guid.NewGuid().ToString("N");
            AssetDatabase.CreateFolder("Assets", Path.GetFileName(folder));
        }

        [TearDown]
        public void TearDown()
        {
            if (AssetDatabase.IsValidFolder(folder))
                AssetDatabase.DeleteAsset(folder);
        }

        [Test]
        public void FindingsSortCriticalFirstAndActionableSecond()
        {
            var input = new[]
            {
                new VRIssue(VRSeverity.Info, VRCategory.Mesh, "info", null),
                new VRIssue(VRSeverity.Warning, VRCategory.Texture, "warn", null, "", false),
                new VRIssue(VRSeverity.Warning, VRCategory.Texture, "action", null, "", true),
                new VRIssue(VRSeverity.Critical, VRCategory.Mesh, "critical", null)
            };
            var sorted = VRDeveloperReview.Prioritize(input);
            Assert.AreEqual("critical", sorted[0].Message);
            Assert.AreEqual("action", sorted[1].Message);
            Assert.AreEqual("warn", sorted[2].Message);
            Assert.AreEqual("info", sorted[3].Message);
            Assert.AreEqual("info", input[0].Message, "Original input order must not change.");
        }

        [Test]
        public void BuiltinPresetsDoNotMutateExistingSettings()
        {
            var settings = new VRSettings { pc = 1024, android = 256, ios = 128 };
            var mobile = VRDeveloperPresets.Apply("Mobile", settings);
            var desktop = VRDeveloperPresets.Apply("Desktop", settings);
            Assert.AreEqual(512, mobile.android);
            Assert.AreEqual(4096, desktop.pc);
            Assert.AreEqual(1024, settings.pc);
            Assert.AreEqual(256, settings.android);
        }

        [Test]
        public void ReviewFindsIdenticalSourceTexturesWithoutEditingImports()
        {
            var texture = new Texture2D(8, 8, TextureFormat.RGBA32, false);
            try
            {
                byte[] png = texture.EncodeToPNG();
                File.WriteAllBytes(folder + "/A.png", png);
                File.WriteAllBytes(folder + "/B.png", png);
                AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
                var findings = VRDeveloperReview.TextureWaste(folder);
                Assert.That(findings.Exists(
                    f => f.Message.Contains("Exact duplicate texture file")), Is.True);
                Assert.IsTrue(File.Exists(folder + "/A.png"));
                Assert.IsTrue(File.Exists(folder + "/B.png"));
            }
            finally { UnityEngine.Object.DestroyImmediate(texture); }
        }
    }
}
