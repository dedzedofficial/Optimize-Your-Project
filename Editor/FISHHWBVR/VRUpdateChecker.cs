using System;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using PackageInfo = UnityEditor.PackageManager.PackageInfo;
using UnityEngine;
using UnityEngine.Networking;

namespace FISHHWB.VROptimizer
{
    internal enum VRUpdateHealth
    {
        Unknown,
        Current,
        UpdateAvailable,
        FarBehind
    }

    internal static class VRUpdateChecker
    {
        const string FeedUrl = "https://raw.githubusercontent.com/dedzedofficial/Optimize-Your-Project/main/version.json";
        const string Repository = "https://github.com/dedzedofficial/Optimize-Your-Project.git";
        const string CacheKey = "FISHHWB.VROptimizer.UpdateCheck.v070";
        const string VersionKey = CacheKey + ".Version";
        const string TagKey = CacheKey + ".Tag";
        const string UrlKey = CacheKey + ".Url";

        [Serializable]
        sealed class VersionFeed
        {
            public string unity;
            public string unity_tag;
            public string unity_url;
        }

        static UnityWebRequest request;
        static UnityWebRequestAsyncOperation operation;
        static AddRequest addRequest;
        static string latestVersion;
        static string latestTag;
        static string releaseUrl;
        static string message;
        static bool checking;
        static bool installing;
        static bool manualCheck;

        internal static bool Checking => checking;
        internal static bool Installing => installing;
        internal static string Message => message;
        internal static string LatestTag => latestTag;
        internal static string LatestVersion => latestVersion;

        internal static string CurrentVersion
        {
            get
            {
                var info = PackageInfo.FindForAssetPath("Packages/com.fishhwb.vr-optimizer/package.json");
                return info != null ? info.version : "0.7.4";
            }
        }

        static PackageInfo Installed => PackageInfo.FindForAssetPath("Packages/com.fishhwb.vr-optimizer/package.json");

        internal static bool HasUpdate
        {
            get
            {
                return TryVersions(out var current, out var latest) && latest > current;
            }
        }

        internal static VRUpdateHealth Health
        {
            get
            {
                if (!TryVersions(out var current, out var latest)) return VRUpdateHealth.Unknown;
                if (latest <= current) return VRUpdateHealth.Current;
                return IsFarBehind(current, latest) ? VRUpdateHealth.FarBehind : VRUpdateHealth.UpdateAvailable;
            }
        }

        internal static string SourceLabel
        {
            get
            {
                var info = Installed;
                return info == null ? "Local copy" : info.source.ToString();
            }
        }

        internal static bool CanUpdateDirectly => Installed != null && Installed.source == PackageSource.Git;

        internal static void CheckIfDue()
        {
            latestVersion = EditorPrefs.GetString(VersionKey, "");
            latestTag = EditorPrefs.GetString(TagKey, "");
            releaseUrl = EditorPrefs.GetString(UrlKey, "");
            var last = EditorPrefs.GetString(CacheKey, "");
            if (DateTime.TryParse(last, null, System.Globalization.DateTimeStyles.RoundtripKind, out var previous) &&
                DateTime.UtcNow - previous.ToUniversalTime() < TimeSpan.FromDays(1))
                return;
            Check(false);
        }

        internal static void Check(bool manual)
        {
            if (checking) return;

            checking = true;
            manualCheck = manual;
            message = manual ? "Checking for updates..." : null;

            request = UnityWebRequest.Get(FeedUrl);
            request.SetRequestHeader("User-Agent", "Optimize-Your-Project-Unity");
            operation = request.SendWebRequest();
            EditorApplication.update -= Poll;
            EditorApplication.update += Poll;
        }

        static void Poll()
        {
            if (operation == null || !operation.isDone) return;

            EditorApplication.update -= Poll;
            checking = false;

            if (request.result != UnityWebRequest.Result.Success)
            {
                message = manualCheck ? "Could not check for updates: " + request.error : null;
            }
            else
            {
                try
                {
                    var feed = JsonUtility.FromJson<VersionFeed>(request.downloadHandler.text);
                    if (feed == null || !Version.TryParse(feed.unity, out _))
                    {
                        message = "The update feed did not contain a valid Unity version.";
                    }
                    else
                    {
                        latestVersion = feed.unity;
                        latestTag = string.IsNullOrEmpty(feed.unity_tag) ? "v" + feed.unity : feed.unity_tag;
                        releaseUrl = feed.unity_url;

                        EditorPrefs.SetString(VersionKey, latestVersion);
                        EditorPrefs.SetString(TagKey, latestTag);
                        EditorPrefs.SetString(UrlKey, releaseUrl ?? "");
                        EditorPrefs.SetString(CacheKey, DateTime.UtcNow.ToString("o"));

                        message = HasUpdate
                            ? "Update available: " + latestTag
                            : "Up to date (v" + CurrentVersion + ").";
                    }
                }
                catch (Exception error)
                {
                    message = manualCheck ? "Invalid update response: " + error.Message : null;
                }
            }

            request.Dispose();
            request = null;
            operation = null;
            EditorApplication.delayCall += RepaintWindows;
        }

        static bool TryVersions(out Version current, out Version latest)
        {
            current = null;
            latest = null;
            return Version.TryParse(CurrentVersion, out current) &&
                   Version.TryParse(latestVersion, out latest);
        }

        static bool IsFarBehind(Version current, Version latest)
        {
            if (latest.Major > current.Major) return true;
            if (latest.Minor > current.Minor) return true;

            int currentPatch = current.Build < 0 ? 0 : current.Build;
            int latestPatch = latest.Build < 0 ? 0 : latest.Build;
            return latestPatch - currentPatch >= 2;
        }

        static void RepaintWindows()
        {
            foreach (var window in Resources.FindObjectsOfTypeAll<FISHHWBVROptimizerWindow>())
                window.Repaint();
        }

        internal static void ViewRelease()
        {
            if (!string.IsNullOrEmpty(releaseUrl) &&
                releaseUrl.StartsWith("https://github.com/dedzedofficial/Optimize-Your-Project/releases/tag/", StringComparison.Ordinal))
                Application.OpenURL(releaseUrl);
            else
                Application.OpenURL("https://github.com/dedzedofficial/Optimize-Your-Project/releases");
        }

        internal static void Update()
        {
            if (!HasUpdate || installing) return;

            var info = Installed;
            if (info == null)
            {
                message = "Package source unavailable. Open Package Manager to update.";
                return;
            }

            if (info.source != PackageSource.Git)
            {
                message = info.source == PackageSource.Embedded
                    ? "Embedded package: download the newest release and replace Packages/com.fishhwb.vr-optimizer."
                    : "VCC or registry package: update through Creator Companion or Package Manager.";
                EditorUtility.DisplayDialog("Update through your package source", message, "OK");
                ViewRelease();
                return;
            }

            string tag = string.IsNullOrEmpty(latestTag) ? "v" + latestVersion : latestTag;
            string target = Repository + "#" + tag;

            if (!EditorUtility.DisplayDialog(
                "Update Optimize Your Project",
                "Installed: v" + CurrentVersion + "\nNew: " + tag +
                "\n\nSave your project first. Unity may reload scripts during the update.",
                "Update",
                "Cancel"))
                return;

            installing = true;
            message = "Updating through Unity Package Manager...";
            addRequest = Client.Add(target);
            EditorApplication.update -= PollInstall;
            EditorApplication.update += PollInstall;
        }

        static void PollInstall()
        {
            if (!addRequest.IsCompleted) return;

            EditorApplication.update -= PollInstall;
            installing = false;
            message = addRequest.Status == StatusCode.Success
                ? "Package updated. Unity may reload the Editor."
                : "Update failed: " + (addRequest.Error == null ? "Unknown Package Manager error" : addRequest.Error.message);

            addRequest = null;
            RepaintWindows();
        }
    }
}
