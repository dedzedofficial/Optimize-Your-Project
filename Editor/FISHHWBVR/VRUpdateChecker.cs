using System;
using UnityEditor;
using UnityEditor.PackageManager;
using UnityEditor.PackageManager.Requests;
using PackageInfo = UnityEditor.PackageManager.PackageInfo;
using UnityEngine;
using UnityEngine.Networking;

namespace FISHHWB.VROptimizer
{
    internal static class VRUpdateChecker
    {
        const string Api = "https://api.github.com/repos/dedzedofficial/VR-Optimizer/releases/latest";
        const string Repository = "https://github.com/dedzedofficial/VR-Optimizer.git";
        const string CacheKey = "FISHHWB.VROptimizer.UpdateCheck.v0673";
        const string TagKey = CacheKey + ".Tag";
        const string UrlKey = CacheKey + ".Url";
        [Serializable] sealed class Release { public string tag_name; public string html_url; }
        static UnityWebRequest request;
        static UnityWebRequestAsyncOperation operation;
        static AddRequest addRequest;
        static string latestTag, releaseUrl, message;
        static bool checking, installing, manualCheck;
        internal static bool Checking => checking;
        internal static bool Installing => installing;
        internal static string Message => message;
        internal static string CurrentVersion
        {
            get
            {
                var info = PackageInfo.FindForAssetPath("Packages/com.fishhwb.vr-optimizer/package.json");
                return info != null ? info.version : "0.6.73";
            }
        }
        static PackageInfo Installed => PackageInfo.FindForAssetPath("Packages/com.fishhwb.vr-optimizer/package.json");
        internal static bool HasUpdate
        {
            get
            {
                if (string.IsNullOrEmpty(latestTag)) return false;
                return Version.TryParse(latestTag.TrimStart('v', 'V'), out var latest) &&
                       Version.TryParse(CurrentVersion, out var current) && latest > current;
            }
        }
        internal static string LatestTag => latestTag;
        internal static string SourceLabel
        {
            get
            {
                var info = Installed;
                return info == null ? "Unknown / local copy" : info.source.ToString();
            }
        }
        internal static bool CanUpdateDirectly => Installed != null && Installed.source == PackageSource.Git;

        internal static void CheckIfDue()
        {
            latestTag = EditorPrefs.GetString(TagKey, "");
            releaseUrl = EditorPrefs.GetString(UrlKey, "");
            var last = EditorPrefs.GetString(CacheKey, "");
            if (DateTime.TryParse(last, null, System.Globalization.DateTimeStyles.RoundtripKind, out var previous) &&
                DateTime.UtcNow - previous.ToUniversalTime() < TimeSpan.FromDays(1)) return;
            Check(false);
        }
        internal static void Check(bool manual)
        {
            if (checking) return;
            checking = true;
            manualCheck = manual;
            EditorPrefs.SetString(CacheKey, DateTime.UtcNow.ToString("o"));
            message = manual ? "Checking GitHub releases..." : null;
            request = UnityWebRequest.Get(Api);
            request.SetRequestHeader("Accept", "application/vnd.github+json");
            request.SetRequestHeader("User-Agent", "FISHHWB-VR-Optimizer");
            operation = request.SendWebRequest();
            EditorApplication.update -= Poll;
            EditorApplication.update += Poll;
        }
        static void Poll()
        {
            if (!operation.isDone) return;
            EditorApplication.update -= Poll;
            checking = false;
            if (request.result != UnityWebRequest.Result.Success)
            {
                // A missing release or offline Editor is not an optimization error.
                message = manualCheck ? "Could not check releases: " + request.error : null;
            }
            else
            {
                try
                {
                    var release = JsonUtility.FromJson<Release>(request.downloadHandler.text);
                    if (release == null || !Version.TryParse(release.tag_name.TrimStart('v', 'V'), out _))
                        message = "No compatible numbered release found.";
                    else
                    {
                        latestTag = release.tag_name;
                        releaseUrl = release.html_url;
                        EditorPrefs.SetString(TagKey, latestTag);
                        EditorPrefs.SetString(UrlKey, releaseUrl ?? "");
                        message = HasUpdate ? "Update available: " + latestTag :
                            Version.TryParse(CurrentVersion, out var installed) && Version.TryParse(latestTag.TrimStart('v', 'V'), out var published) && installed > published ?
                            "Installed copy is newer than the latest published release (" + latestTag + ")." :
                            "Up to date (" + CurrentVersion + ").";
                        EditorPrefs.SetString(CacheKey, DateTime.UtcNow.ToString("o"));
                    }
                }
                catch (Exception error) { message = manualCheck ? "Invalid release response: " + error.Message : null; }
            }
            request.Dispose();
            request = null;
            operation = null;
            EditorApplication.delayCall += RepaintWindows;
        }
        static void RepaintWindows()
        {
            foreach (var window in Resources.FindObjectsOfTypeAll<FISHHWBVROptimizerWindow>()) window.Repaint();
        }
        internal static void ViewRelease()
        { if (!string.IsNullOrEmpty(releaseUrl) && releaseUrl.StartsWith("https://github.com/dedzedofficial/VR-Optimizer/releases/tag/", StringComparison.Ordinal)) Application.OpenURL(releaseUrl); }
        internal static void Update()
        {
            if (!HasUpdate || installing) return;
            var info = Installed;
            if (info == null) { message = "Package source unavailable. Open Package Manager to update."; return; }
            if (info.source != PackageSource.Git)
            {
                message = info.source == PackageSource.Embedded ?
                    "Embedded package: download the release ZIP and replace Packages/com.fishhwb.vr-optimizer." :
                    "VCC/registry package: update through Creator Companion or Package Manager.";
                EditorUtility.DisplayDialog("Update through your package source", message, "OK");
                ViewRelease();
                return;
            }
            string target = Repository + "#" + latestTag;
            if (!EditorUtility.DisplayDialog("Update VR Optimizer", "Installed: " + CurrentVersion + "\nNew: " + latestTag +
                "\nSource: Unity Git package\n\nSave your project first. Unity may reload scripts during the update. Install " + target + "?", "Update", "Cancel")) return;
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
            message = addRequest.Status == StatusCode.Success ? "Package updated. Unity may reload the Editor." :
                "Update failed: " + (addRequest.Error == null ? "Unknown Package Manager error" : addRequest.Error.message);
            addRequest = null;
            RepaintWindows();
        }
    }
}
