using System;
using System.Collections.Generic;
using System.IO;
using NUnit.Framework;

namespace FISHHWB.VROptimizer
{
    public sealed class VRUpdateBackupMaintenanceTests
    {
        string root;
        string backup;

        [SetUp]
        public void SetUp()
        {
            root = Path.Combine(Path.GetTempPath(), "OYPBackupTest_" + Guid.NewGuid().ToString("N"));
            backup = Path.Combine(root, "20261122_120000_000");
            Directory.CreateDirectory(backup);
            File.WriteAllText(Path.Combine(backup, "manifest.json"), "{\"dependencies\":{}}");
            File.WriteAllText(Path.Combine(backup, "packages-lock.json"), "{}");
        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(root)) Directory.Delete(root, true);
        }

        [Test]
        public void AllExpectedInstalledVersionsMustMatchExactly()
        {
            var expected = new List<string> {
                "com.unity.test-framework|1.4.5|registry",
                "com.fishhwb.vr-optimizer|0.8.9|git"
            };
            var installed = new Dictionary<string, string> {
                { "com.unity.test-framework|registry", "1.4.5" },
                { "com.fishhwb.vr-optimizer|git", "0.8.9" }
            };
            Assert.IsTrue(VRUpdateBackupMaintenance.ExpectedPackagesVerified(expected, installed));

            installed["com.unity.test-framework|registry"] = "1.4.4";
            Assert.IsFalse(VRUpdateBackupMaintenance.ExpectedPackagesVerified(expected, installed));
            installed["com.unity.test-framework|registry"] = "1.4.5";
            installed.Remove("com.fishhwb.vr-optimizer|git");
            Assert.IsFalse(VRUpdateBackupMaintenance.ExpectedPackagesVerified(expected, installed));
            Assert.IsFalse(VRUpdateBackupMaintenance.ExpectedPackagesVerified(
                new List<string>(), installed));
            Assert.IsFalse(VRUpdateBackupMaintenance.ExpectedPackagesVerified(
                new List<string> { "invalid-format" }, installed));
        }

        [Test]
        public void VerifiedManagedBackupDeletesOnlyItsManifestSnapshots()
        {
            Assert.IsTrue(VRUpdateBackupMaintenance.SafeBackupDirectory(backup, root));
            Assert.IsTrue(VRUpdateBackupMaintenance.TryDeleteManagedBackup(backup, root));
            Assert.IsFalse(Directory.Exists(backup));
            Assert.IsTrue(Directory.Exists(root));
        }

        [Test]
        public void UnexpectedFileAlwaysProtectsBackupFromAutomaticCleanup()
        {
            string sentinel = Path.Combine(backup, "my-important-notes.txt");
            File.WriteAllText(sentinel, "Do not delete this.");
            Assert.IsFalse(VRUpdateBackupMaintenance.TryDeleteManagedBackup(backup, root));
            Assert.IsTrue(File.Exists(sentinel));
            Assert.IsTrue(File.Exists(Path.Combine(backup, "manifest.json")));
        }

        [Test]
        public void CleanupRefusesNestedAndOutsideDirectories()
        {
            var nested = Path.Combine(backup, "nested");
            Directory.CreateDirectory(nested);
            File.WriteAllText(Path.Combine(nested, "manifest.json"), "{}");
            Assert.IsFalse(VRUpdateBackupMaintenance.SafeBackupDirectory(nested, root));
            Assert.IsFalse(VRUpdateBackupMaintenance.TryDeleteManagedBackup(nested, root));
            Assert.IsFalse(VRUpdateBackupMaintenance.TryDeleteManagedBackup(root, root));
            Assert.IsFalse(VRUpdateBackupMaintenance.TryDeleteManagedBackup(
                Path.GetTempPath(), root));
        }

        [Test]
        public void CleanupRefusesMissingManifestOrNestedDirectories()
        {
            File.Delete(Path.Combine(backup, "manifest.json"));
            Assert.IsFalse(VRUpdateBackupMaintenance.TryDeleteManagedBackup(backup, root));

            File.WriteAllText(Path.Combine(backup, "manifest.json"), "{}");
            Directory.CreateDirectory(Path.Combine(backup, "nested"));
            Assert.IsFalse(VRUpdateBackupMaintenance.TryDeleteManagedBackup(backup, root));
        }
    }
}
