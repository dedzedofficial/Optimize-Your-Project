using NUnit.Framework;

namespace FISHHWB.VROptimizer
{
    public sealed class VRProjectAutoUpdaterTests
    {
        [TestCase("1.2.3", "1.2.4", true)]
        [TestCase("0.8.8", "0.8.9", true)]
        [TestCase("1.2.3", "1.2.3", false)]
        [TestCase("1.2.4", "1.2.3", false)]
        [TestCase("1.2.3", "1.3.0", false)]
        [TestCase("1.2.3", "2.0.0", false)]
        [TestCase("1.2.3", "1.2.4-preview.1", false)]
        [TestCase("1.2.3", "1.2.4.5", false)]
        [TestCase("1.2.3-preview.1", "1.2.4", false)]
        [TestCase("", "1.2.4", false)]
        public void OnlyStableSameMinorPatchUpgradesAreAutomatic(
            string installed, string available, bool expected)
        {
            Assert.AreEqual(expected, VRProjectAutoUpdater.IsCompatiblePatch(installed, available));
        }

        [Test]
        public void OnlyOfficialGitOriginMayBeUpgraded()
        {
            Assert.IsTrue(VRProjectAutoUpdater.TrustedGitOrigin(
                "com.fishhwb.vr-optimizer@https://github.com/dedzedofficial/Optimize-Your-Project.git#v0.8.8"));
            Assert.IsFalse(VRProjectAutoUpdater.TrustedGitOrigin(
                "com.fishhwb.vr-optimizer@https://github.com/someone/Optimize-Your-Project.git#v0.8.8"));
            Assert.IsFalse(VRProjectAutoUpdater.TrustedGitOrigin(
                "com.fishhwb.vr-optimizer@https://github.com/dedzedofficial/Optimize-Your-Project.git.evil#v0.8.8"));
            Assert.IsFalse(VRProjectAutoUpdater.TrustedGitOrigin(null));
        }

        [TestCase("v0.8.9", true)]
        [TestCase("v0.8.8.4", false)]
        [TestCase("v1.0.0-preview", false)]
        [TestCase("https://example.com", false)]
        public void GitTagMustBeASafePackageVersion(string tag, bool expected)
        {
            Assert.AreEqual(expected, VRProjectAutoUpdater.SafeTag(tag));
        }
    }
}
