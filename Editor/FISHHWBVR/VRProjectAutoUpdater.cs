using System;
using System.Collections.Generic;
using System.IO;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;
using UnityEngine.SceneManagement;
using PackageInfo = UnityEditor.PackageManager.PackageInfo;

namespace FISHHWB.VROptimizer
{
    // Project-scoped, once-per-Editor-session updates. Never touch Asset Store
    // imports, embedded/local packages, VRChat/VCC Git packages or built-in modules.
    // Update every direct registry package with a newer stable release compatible
    // with this Unity Editor, plus our verified official Git package.
    // Transitive dependencies are resolved by the Package Manager transaction.
    [InitializeOnLoad]
    internal static class VRProjectAutoUpdater
    {
        const string SessionKey = "FISHHWB.VROptimizer.AutoUpdate.v0884.Ran";
        const string ReportKey = "FISHHWB.VROptimizer.AutoUpdate.v0884.Report";
        const string ScanKey = "FISHHWB.VROptimizer.AutoUpdate.v0884.Scan";
        const string Repository = "https://github.com/dedzedofficial/Optimize-Your-Project.git";
        const string GitPackage = "com.fishhwb.vr-optimizer";
        const string PreferencePrefix = "FISHHWB.VROptimizer.AutoUpdate.v0884.";

        static ListRequest listRequest;
        static AddAndRemoveRequest upgradeRequest;
        static string[] targets;
        static string[] expectedPackages;

        internal static void ReportBackupStatus(string status)
        {
            SessionState.SetString(ReportKey, status);
            Debug.Log("Optimize Your Project backup maintenance: " + status);
        }

        internal static string PreferenceKey => PreferencePrefix + Application.dataPath;
        internal static bool Enabled
        {
            get => EditorPrefs.GetBool(PreferenceKey, true);
            set => EditorPrefs.SetBool(PreferenceKey, value);
        }
        internal static string Report => SessionState.GetString(ReportKey, "Startup updates have not run in this Editor session.")
            + "\n" + SessionState.GetString(ScanKey, "");

        static VRProjectAutoUpdater()
        {
            EditorApplication.delayCall += Start;
        }

        static void Start()
        {
            if (SessionState.GetBool(SessionKey, false))
                return;
            // Mark before requests to avoid an infinite update/recompile loop.
            SessionState.SetBool(SessionKey, true);
            if (!Application.isBatchMode && VRUpdateBackupMaintenance.HasPending)
            {
                VRUpdateBackupMaintenance.VerifyOnNextEditorLaunch();
                return; // Verify a prior update before trying another one.
            }
            if (!Enabled || Application.isBatchMode)
            {
                SessionState.SetString(ReportKey, Enabled ? "Skipped in batch mode." : "Automatic project updates disabled.");
                return;
            }
            SessionState.SetString(ReportKey, "Checking compatible installed packages...");
            EditorApplication.update += BeginWhenReady;
        }

        static bool Ready => !EditorApplication.isCompiling && !EditorApplication.isUpdating && !HasDirtyScenes();

        static bool HasDirtyScenes()
        {
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                var scene = SceneManager.GetSceneAt(i);
                if (scene.IsValid() && scene.isDirty) return true;
            }
            return false;
        }

        static void BeginWhenReady()
        {
            if (EditorApplication.isCompiling || EditorApplication.isUpdating)
                return;
            EditorApplication.update -= BeginWhenReady;
            if (!Ready)
            {
                SessionState.SetString(ReportKey, "Skipped: save open scenes before automatic package updates.");
                return;
            }
            try
            {
                VRUpdateChecker.CheckIfDue();
                listRequest = Client.List(false, true);
                EditorApplication.update += PollList;
            }
            catch (Exception error)
            {
                Fail("Could not start package scan: " + error.Message);
            }
        }

        static void PollList()
        {
            if (listRequest == null || !listRequest.IsCompleted || VRUpdateChecker.Checking)
                return;
            EditorApplication.update -= PollList;
            if (listRequest.Status != StatusCode.Success)
            {
                Fail("Package scan failed: " + (listRequest.Error == null ? "Unknown error" : listRequest.Error.message));
                listRequest = null;
                return;
            }

            var updates = new List<string>();
            var expected = new List<string>();
            int installedCount = 0, indirectCount = 0, currentCount = 0, unmanagedCount = 0;
            var examples = new List<string>();
            foreach (PackageInfo installed in listRequest.Result)
            {
                if (installed == null) continue;
                installedCount++;

                // All resolved packages are inventoried. Only direct dependencies
                // are independently editable; Unity resolves indirect versions.
                if (!installed.isDirectDependency)
                {
                    indirectCount++;
                    continue;
                }

                if (installed.source == PackageSource.Registry)
                {
                    string candidate = installed.versions == null
                        ? null : installed.versions.latestCompatible;
                    if (IsCompatibleRelease(installed.version, candidate))
                    {
                        updates.Add(installed.name + "@" + candidate);
                        expected.Add(installed.name + "|" + candidate + "|registry");
                        if (examples.Count < 12)
                            examples.Add(installed.name + ": " + installed.version + " -> " + candidate);
                    }
                    else if (string.Equals(installed.version, candidate, StringComparison.Ordinal))
                        currentCount++;
                    else
                        unmanagedCount++; // Unknown, preview or unavailable compatible version.
                }
                else if (installed.name == GitPackage &&
                         installed.source == PackageSource.Git &&
                         TrustedGitOrigin(installed.packageId))
                {
                    if (VRUpdateChecker.HasUpdate && SafeTag(VRUpdateChecker.LatestTag))
                    {
                        updates.Add(Repository + "#" + VRUpdateChecker.LatestTag);
                        expected.Add(GitPackage + "|" + VRUpdateChecker.LatestVersion + "|git");
                        if (examples.Count < 12)
                            examples.Add(installed.name + ": " + installed.version +
                                         " -> " + VRUpdateChecker.LatestTag);
                    }
                    else
                        currentCount++;
                }
                else
                    unmanagedCount++; // Embedded, local, built-in or other vendor-managed source.
            }
            listRequest = null;
            updates.Sort(StringComparer.Ordinal);
            targets = updates.ToArray();
            expectedPackages = expected.ToArray();
            string scan = "Checked " + installedCount + " installed packages: " +
                targets.Length + " eligible update(s), " + currentCount + " current, " +
                indirectCount + " dependency-managed, " + unmanagedCount +
                " unsupported/untracked. All installed packages were checked; " +
                "only directly managed packages are changed.";
            if (examples.Count > 0)
                scan += "\nAvailable updates:\n" + string.Join("\n", examples.ToArray()) +
                    (targets.Length > examples.Count ? "\n...and " +
                     (targets.Length - examples.Count) + " more." : "");
            SessionState.SetString(ScanKey, scan);
            if (targets.Length == 0)
            {
                SessionState.SetString(ReportKey,
                    "No eligible managed updates. Other package sources remain untouched.");
                return;
            }
            if (!Enabled || !Ready)
            {
                SessionState.SetString(ReportKey, "Skipped: updates disabled or scenes need saving.");
                return;
            }

            try
            {
                string backup = BackupManifests();
                VRUpdateBackupMaintenance.RecordPending(backup, expectedPackages);
                SessionState.SetString(ReportKey,
                    "Installing " + targets.Length + " compatible update(s). Manifest backup: " + backup);
                upgradeRequest = Client.AddAndRemove(targets, Array.Empty<string>());
                EditorApplication.update += PollUpgrade;
            }
            catch (Exception error)
            {
                VRUpdateBackupMaintenance.MarkTransactionFailed();
                Fail("Automatic updates not started: " + error.Message);
            }
        }

        static void PollUpgrade()
        {
            if (upgradeRequest == null || !upgradeRequest.IsCompleted)
                return;
            EditorApplication.update -= PollUpgrade;
            bool succeeded = upgradeRequest.Status == StatusCode.Success;
            if (succeeded) VRUpdateBackupMaintenance.MarkTransactionSucceeded();
            else VRUpdateBackupMaintenance.MarkTransactionFailed();
            string result = succeeded
                ? "Package Manager completed " + targets.Length + " update request(s). Review Unity Console and test the project."
                : "Package Manager update failed: " +
                  (upgradeRequest.Error == null ? "Unknown error" : upgradeRequest.Error.message);
            SessionState.SetString(ReportKey, result);
            Debug.Log("Optimize Your Project auto-update: " + result);
            upgradeRequest = null;
            targets = null;
            expectedPackages = null;
        }

        internal static bool IsCompatibleRelease(string current, string available)
        {
            // latestCompatible comes from Unity, so cross-major/minor releases
            // are eligible, but never accept prereleases or downgrades.
            if (!TryTriple(current, out int major, out int minor, out int patch) ||
                !TryTriple(available, out int newerMajor, out int newerMinor, out int newerPatch))
                return false;
            return newerMajor > major ||
                   (newerMajor == major && newerMinor > minor) ||
                   (newerMajor == major && newerMinor == minor && newerPatch > patch);
        }

        static bool TryTriple(string text, out int major, out int minor, out int patch)
        {
            major = minor = patch = 0;
            if (string.IsNullOrEmpty(text)) return false;
            string[] parts = text.Split('.');
            return parts.Length == 3 &&
                   int.TryParse(parts[0], out major) && major >= 0 &&
                   int.TryParse(parts[1], out minor) && minor >= 0 &&
                   int.TryParse(parts[2], out patch) && patch >= 0;
        }

        internal static bool TrustedGitOrigin(string packageId)
        {
            return !string.IsNullOrEmpty(packageId) &&
                   packageId.StartsWith(GitPackage + "@" + Repository, StringComparison.OrdinalIgnoreCase) &&
                   (packageId.Length == (GitPackage + "@" + Repository).Length ||
                    packageId[(GitPackage + "@" + Repository).Length] == '#');
        }

        internal static bool SafeTag(string tag)
        {
            if (string.IsNullOrEmpty(tag) || tag[0] != 'v')
                return false;
            return TryTriple(tag.Substring(1), out _, out _, out _);
        }

        static string BackupManifests()
        {
            string project = Path.GetDirectoryName(Application.dataPath);
            string directory = Path.Combine(project, "Library", "OptimizeYourProject", "UpdateBackups",
                DateTime.UtcNow.ToString("yyyyMMdd_HHmmss_fff"));
            string manifest = Path.Combine(project, "Packages", "manifest.json");
            if (!File.Exists(manifest))
                throw new FileNotFoundException("Unity package manifest is missing; refusing automatic updates.", manifest);
            Directory.CreateDirectory(directory);
            foreach (string name in new[] { "manifest.json", "packages-lock.json" })
            {
                string source = Path.Combine(project, "Packages", name);
                if (File.Exists(source))
                    File.Copy(source, Path.Combine(directory, name), false);
            }
            return directory;
        }

        static void Fail(string problem)
        {
            SessionState.SetString(ReportKey, problem);
            Debug.LogWarning("Optimize Your Project auto-update: " + problem);
        }
    }
}
