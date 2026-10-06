using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRMissingScriptCleaner
    {
        internal static string Clean(GameObject root)
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
                    EditorUtility.SetDirty(gameObject);
                }
            }
            finally
            {
                Undo.CollapseUndoOperations(group);
            }

            return removedScripts == 0
                ? "Missing scripts: nothing to clean in this scope."
                : "Missing scripts cleaned: " + removedScripts + " removed from " + affectedObjects + " objects. Use Undo if needed.";
        }
    }
}
