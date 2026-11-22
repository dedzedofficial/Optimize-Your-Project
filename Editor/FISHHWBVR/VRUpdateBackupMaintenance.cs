using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using UnityEngine;
using PackageInfo = UnityEditor.PackageManager.PackageInfo;

namespace FISHHWB.VROptimizer
{
    [Serializable]
    internal sealed class VRUpdateBackupRecord
    {
        public string Directory;
        public string[] ExpectedPackages;
        public string Status;
        public string ManifestFingerprint;
        public string LockFingerprint;
    }

    // Only backups created by our own auto-updater are eligible for removal.
    // A new Editor session must verify package resolution and healthy compilation
    // before these local manifest/lock snapshots are no longer needed.
    internal static class VRUpdateBackupMaintenance
    {
        const string KeyPrefix = "FISHHWB.VROptimizer.AutoUpdate.v0884.PendingBackup.";
        const string Installing = "installing";
        const string Installed = "installed";
        const string Failed = "failed";

        static ListRequest verifyRequest;
        static double stableSince = -1;

        static string Root => Path.Combine(
            Path.GetDirectoryName(Application.dataPath), "Library",
            "OptimizeYourProject", "UpdateBackups");
        static string StateKey => KeyPrefix + Application.dataPath;

        internal static bool HasPending => !string.IsNullOrEmpty(EditorPrefs.GetString(StateKey, ""));
        internal static string PendingStatus
        {
            get
            {
                var record = Read();
                return record == null ? "" : record.Status;
            }
        }

        static VRUpdateBackupRecord Read()
        {
            string json = EditorPrefs.GetString(StateKey, "");
            if (string.IsNullOrEmpty(json)) return null;
            try { return JsonUtility.FromJson<VRUpdateBackupRecord>(json); }
            catch (ArgumentException) { return null; }
        }

        static void Save(VRUpdateBackupRecord record)
        {
            EditorPrefs.SetString(StateKey, JsonUtility.ToJson(record));
        }

        internal static void RecordPending(string directory, string[] expectedPackages)
        {
            if (!SafeBackupDirectory(directory, Root) || expectedPackages == null ||
                expectedPackages.Length == 0 || !File.Exists(Path.Combine(directory, "manifest.json")))
                throw new InvalidOperationException("Cannot track an unverified automatic-update backup.");
            if (HasPending)
                throw new InvalidOperationException("An older update backup still needs verification.");
            Save(new VRUpdateBackupRecord
            {
                Directory = directory,
                ExpectedPackages = (string[])expectedPackages.Clone(),
                ManifestFingerprint = Fingerprint(Path.Combine(directory, "manifest.json")),
                LockFingerprint = Fingerprint(Path.Combine(directory, "packages-lock.json")),
                Status = Installing
            });
        }

        internal static void MarkTransactionSucceeded()
        {
            var record = Read();
            if (record == null) return;
            record.Status = Installed;
            Save(record);
        }

        internal static void MarkTransactionFailed()
        {
            var record = Read();
            if (record == null) return;
            record.Status = Failed;
            Save(record);
        }

        internal static void VerifyOnNextEditorLaunch()
        {
            var record = Read();
            if (record == null || !HasPending)
            {
                VRProjectAutoUpdater.ReportBackupStatus(
                    "Previous update backup needs review; verification metadata is missing.");
                return;
            }
            if (record.Status == Failed)
            {
                VRProjectAutoUpdater.ReportBackupStatus(
                    "Previous package update failed. Its backup was retained for recovery.");
                return;
            }
            if (record.Status != Installing && record.Status != Installed)
            {
                VRProjectAutoUpdater.ReportBackupStatus(
                    "Unknown update verification status. Backup retained for review.");
                return;
            }
            if (!SafeBackupDirectory(record.Directory, Root))
            {
                VRProjectAutoUpdater.ReportBackupStatus(
                    "Update backup is outside the managed directory. No cleanup attempted.");
                return;
            }

            // On a fresh Unity launch only. Compilation must settle and have
            // no errors before the resolved package graph can be accepted.
            stableSince = -1;
            EditorApplication.update -= WaitForHealthyEditor;
            EditorApplication.update += WaitForHealthyEditor;
            VRProjectAutoUpdater.ReportBackupStatus(
                "Retained the previous backup while checking package versions and compilation.");
        }

        static void WaitForHealthyEditor()
        {
            if (EditorApplication.isCompiling || EditorApplication.isUpdating)
            {
                stableSince = -1;
                return;
            }
            if (EditorUtility.scriptCompilationFailed)
            {
                EditorApplication.update -= WaitForHealthyEditor;
                VRProjectAutoUpdater.ReportBackupStatus(
                    "Compilation errors detected. The previous update backup was retained.");
                return;
            }
            if (stableSince < 0)
            {
                stableSince = EditorApplication.timeSinceStartup;
                return;
            }
            if (EditorApplication.timeSinceStartup - stableSince < 5.0)
                return;

            EditorApplication.update -= WaitForHealthyEditor;
            try
            {
                // Offline verification of Unity's actual resolved package graph.
                verifyRequest = Client.List(true, true);
                EditorApplication.update += PollVerifiedPackages;
            }
            catch (Exception error)
            {
                Retain("Package verification could not start: " + error.Message);
            }
        }

        static void PollVerifiedPackages()
        {
            if (verifyRequest == null || !verifyRequest.IsCompleted) return;
            EditorApplication.update -= PollVerifiedPackages;
            var request = verifyRequest;
            verifyRequest = null;

            if (request.Status != StatusCode.Success)
            {
                Retain("Package verification failed. Backup retained.");
                return;
            }
            var record = Read();
            if (record == null || record.Status == Failed ||
                EditorApplication.isCompiling || EditorApplication.isUpdating ||
                EditorUtility.scriptCompilationFailed)
            {
                Retain("Package or compilation state was not confirmed. Backup retained.");
                return;
            }

            var installed = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (PackageInfo info in request.Result)
            {
                if (info == null) continue;
                string source = info.source == PackageSource.Registry ? "registry" :
                    info.source == PackageSource.Git ? "git" : "other";
                installed[info.name + "|" + source] = info.version;
            }
            if (!ExpectedPackagesVerified(record.ExpectedPackages, installed))
            {
                Retain("Updated package versions do not match the expected versions. Backup retained.");
                return;
            }

            string projectPackages = Path.Combine(Path.GetDirectoryName(Application.dataPath), "Packages");
            if (!File.Exists(Path.Combine(projectPackages, "manifest.json")) ||
                (File.Exists(Path.Combine(record.Directory, "packages-lock.json")) &&
                 !File.Exists(Path.Combine(projectPackages, "packages-lock.json"))))
            {
                Retain("The project package manifest or lock file is missing. Backup retained.");
                return;
            }
            if (!BackupSnapshotUnchanged(record))
            {
                Retain("An original backup snapshot was modified or missing. Backup retained.");
                return;
            }
            if (!TryDeleteManagedBackup(record.Directory, Root))
            {
                Retain("A backup file was changed or could not be safely removed. Backup retained.");
                return;
            }

            EditorPrefs.DeleteKey(StateKey);
            VRProjectAutoUpdater.ReportBackupStatus(
                "Verified installed packages and a clean compilation. Obsolete update backup deleted.");
        }

        static void Retain(string message)
        {
            VRProjectAutoUpdater.ReportBackupStatus(message);
        }

        static string Fingerprint(string path)
        {
            if (!File.Exists(path)) return null;
            using (var sha = SHA256.Create())
            using (var stream = File.OpenRead(path))
                return Convert.ToBase64String(sha.ComputeHash(stream));
        }

        internal static bool BackupSnapshotUnchanged(VRUpdateBackupRecord record)
        {
            if (record == null || string.IsNullOrEmpty(record.ManifestFingerprint) ||
                string.IsNullOrEmpty(record.Directory))
                return false;
            try
            {
                return string.Equals(record.ManifestFingerprint,
                           Fingerprint(Path.Combine(record.Directory, "manifest.json")),
                           StringComparison.Ordinal) &&
                       string.Equals(record.LockFingerprint,
                           Fingerprint(Path.Combine(record.Directory, "packages-lock.json")),
                           StringComparison.Ordinal);
            }
            catch (Exception error) when (error is IOException ||
                                           error is UnauthorizedAccessException)
            {
                return false;
            }
        }

        // Expected entry format is name|version|source. Source must be Registry
        // or Git. This method is pure so we can unit-test bad/missing versions.
        internal static bool ExpectedPackagesVerified(
            IList<string> expected, IDictionary<string, string> installed)
        {
            if (expected == null || expected.Count == 0 || installed == null)
                return false;
            foreach (string item in expected)
            {
                if (string.IsNullOrEmpty(item)) return false;
                var parts = item.Split('|');
                if (parts.Length != 3 || string.IsNullOrEmpty(parts[0]) ||
                    string.IsNullOrEmpty(parts[1]) ||
                    (parts[2] != "registry" && parts[2] != "git"))
                    return false;
                if (!installed.TryGetValue(parts[0] + "|" + parts[2], out string actual) ||
                    !string.Equals(actual, parts[1], StringComparison.Ordinal))
                    return false;
            }
            return true;
        }

        internal static bool SafeBackupDirectory(string directory, string root)
        {
            if (string.IsNullOrEmpty(directory) || string.IsNullOrEmpty(root))
                return false;
            try
            {
                string normalizedRoot = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar);
                string normalized = Path.GetFullPath(directory).TrimEnd(Path.DirectorySeparatorChar);
                if (!string.Equals(Path.GetDirectoryName(normalized), normalizedRoot,
                    StringComparison.OrdinalIgnoreCase) || !Directory.Exists(normalized))
                    return false;
                if ((File.GetAttributes(normalized) & FileAttributes.ReparsePoint) != 0)
                    return false;
                if ((File.GetAttributes(normalizedRoot) & FileAttributes.ReparsePoint) != 0)
                    return false;
                return true;
            }
            catch (Exception error) when (error is ArgumentException || error is IOException ||
                                           error is UnauthorizedAccessException ||
                                           error is NotSupportedException)
            {
                return false;
            }
        }

        internal static bool TryDeleteManagedBackup(string directory, string root)
        {
            if (!SafeBackupDirectory(directory, root)) return false;
            try
            {
                if (Directory.GetDirectories(directory).Length != 0)
                    return false;
                string[] files = Directory.GetFiles(directory);
                bool manifestPresent = false;
                foreach (string file in files)
                {
                    string name = Path.GetFileName(file);
                    var attributes = File.GetAttributes(file);
                    if ((attributes & (FileAttributes.ReparsePoint | FileAttributes.ReadOnly)) != 0)
                        return false;
                    if (name == "manifest.json") manifestPresent = true;
                    else if (name != "packages-lock.json") return false;
                }
                if (!manifestPresent) return false;
                foreach (string file in files)
                    File.Delete(file);
                Directory.Delete(directory, false);
                return true;
            }
            catch (Exception error) when (error is IOException ||
                                           error is UnauthorizedAccessException)
            {
                return false;
            }
        }
    }
}
