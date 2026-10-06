using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRMissingScriptCleaner
    {
        internal static string Clean(GameObject root, bool confirm = true)
        {
            var objects = new List<GameObject>();

            if (root)
            {
                foreach (var transform in root.GetComponentsInChildren<Transform>(true))
                    if (transform) objects.Add(transform.gameObject);
            }
            else
            {
                foreach (var transform in VRProjectScanner.SceneObjects<Transform>())
                    if (transform) objects.Add(transform.gameObject);
            }

            int pendingObjects = 0;
            int pendingScripts = 0;
            foreach (var gameObject in objects)
            {
                if (!gameObject) continue;
                int missing = GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(gameObject);
                if (missing <= 0) continue;
                pendingObjects++;
                pendingScripts += missing;
            }

            if (pendingScripts == 0)
                return "Missing scripts: nothing to clean in this scope.";

            if (confirm && !EditorUtility.DisplayDialog(
                "Clean missing scripts",
                "Remove " + pendingScripts + " missing script component(s) from " + pendingObjects +
                " object(s)?\n\nOnly broken MonoBehaviour entries are removed. Valid scripts and components are untouched. Unity Undo is available.",
                "Clean Missing Scripts",
                "Cancel"))
                return "Missing script cleanup cancelled. Nothing changed.";

            int affectedObjects = 0;
            int removedScripts = 0;

            Undo.IncrementCurrentGroup();
            int group = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName("Clean Missing Scripts");

            try
            {
                foreach (var gameObject in objects)
                {
                    if (!gameObject) continue;

                    int missing = GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(gameObject);
                    if (missing <= 0) continue;

                    Undo.RegisterCompleteObjectUndo(gameObject, "Clean Missing Scripts");
                    int removed = GameObjectUtility.RemoveMonoBehavioursWithMissingScript(gameObject);
                    if (removed <= 0) continue;

                    affectedObjects++;
                    removedScripts += removed;
                    PrefabUtility.RecordPrefabInstancePropertyModifications(gameObject);
                    EditorUtility.SetDirty(gameObject);
                }
            }
            finally
            {
                Undo.CollapseUndoOperations(group);
            }

            return "Missing scripts cleaned: " + removedScripts + " removed from " + affectedObjects +
                   " objects. Use Undo if needed.";
        }
    }
}
