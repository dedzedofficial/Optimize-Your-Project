using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal static class VRUIRaycastOptimizer
    {
        internal static string Optimize(GameObject root)
        {
            var graphics = CollectGraphics(root);
            var candidates = new List<Component>();
            int interactive = 0;
            int alreadyOptimized = 0;

            foreach (var graphic in graphics)
            {
                if (!graphic) continue;

                var serialized = new SerializedObject(graphic);
                var raycast = serialized.FindProperty("m_RaycastTarget");
                if (raycast == null || raycast.propertyType != SerializedPropertyType.Boolean)
                    continue;

                if (!raycast.boolValue)
                {
                    alreadyOptimized++;
                    continue;
                }

                if (HasInteractiveHierarchy(graphic.transform))
                {
                    interactive++;
                    continue;
                }

                candidates.Add(graphic);
            }

            if (candidates.Count == 0)
                return "UI raycasts: nothing safe to change. " + alreadyOptimized + " already disabled, " + interactive + " kept for interactive UI.";

            if (!EditorUtility.DisplayDialog(
                "Optimize UI raycasts",
                "Disable Raycast Target on " + candidates.Count + " decorative UI graphics?\n\n" +
                "Graphics on objects or parent hierarchies with EventSystem interaction handlers are skipped. " +
                "This reduces unnecessary GraphicRaycaster checks without changing interactive controls.\n\n" +
                "Unity Undo is available.",
                "Optimize",
                "Cancel"))
                return "UI raycast optimization cancelled.";

            Undo.IncrementCurrentGroup();
            int group = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName("Optimize UI Raycasts");
            int changed = 0;

            try
            {
                foreach (var graphic in candidates)
                {
                    if (!graphic) continue;

                    var serialized = new SerializedObject(graphic);
                    var raycast = serialized.FindProperty("m_RaycastTarget");
                    if (raycast == null || raycast.propertyType != SerializedPropertyType.Boolean || !raycast.boolValue)
                        continue;

                    Undo.RecordObject(graphic, "Optimize UI Raycasts");
                    raycast.boolValue = false;
                    serialized.ApplyModifiedProperties();
                    EditorUtility.SetDirty(graphic);
                    changed++;
                }
            }
            finally
            {
                Undo.CollapseUndoOperations(group);
            }

            return "UI raycasts optimized: " + changed + " decorative graphics changed. " +
                   interactive + " interactive graphics kept, " + alreadyOptimized + " already optimized. Use Undo if needed.";
        }

        static List<Component> CollectGraphics(GameObject root)
        {
            var result = new List<Component>();
            var seen = new HashSet<int>();

            if (root)
            {
                foreach (var transform in root.GetComponentsInChildren<Transform>(true))
                    CollectFromObject(transform ? transform.gameObject : null, result, seen);
            }
            else
            {
                foreach (var transform in VRProjectScanner.SceneObjects<Transform>())
                    CollectFromObject(transform ? transform.gameObject : null, result, seen);
            }

            return result;
        }

        static void CollectFromObject(GameObject gameObject, List<Component> result, HashSet<int> seen)
        {
            if (!gameObject || !seen.Add(gameObject.GetInstanceID())) return;

            foreach (var component in gameObject.GetComponents<Component>())
                if (component && IsGraphic(component.GetType()))
                    result.Add(component);
        }

        static bool IsGraphic(System.Type type)
        {
            while (type != null)
            {
                if (type.FullName == "UnityEngine.UI.Graphic")
                    return true;
                type = type.BaseType;
            }
            return false;
        }

        static bool HasInteractiveHierarchy(Transform transform)
        {
            for (var current = transform; current; current = current.parent)
            {
                foreach (var component in current.GetComponents<Component>())
                {
                    if (!component) continue;
                    var type = component.GetType();

                    foreach (var contract in type.GetInterfaces())
                    {
                        if (contract.Namespace == "UnityEngine.EventSystems" && IsInteractionContract(contract.Name))
                            return true;
                    }
                }

                if (current.GetComponent<Canvas>())
                    break;
            }

            return false;
        }

        static bool IsInteractionContract(string name)
        {
            switch (name)
            {
                case "IPointerClickHandler":
                case "IPointerDownHandler":
                case "IPointerUpHandler":
                case "IPointerEnterHandler":
                case "IPointerExitHandler":
                case "IBeginDragHandler":
                case "IDragHandler":
                case "IEndDragHandler":
                case "IDropHandler":
                case "IScrollHandler":
                case "ISelectHandler":
                case "IDeselectHandler":
                case "ISubmitHandler":
                case "ICancelHandler":
                case "IMoveHandler":
                case "IUpdateSelectedHandler":
                    return true;
                default:
                    return false;
            }
        }
    }
}
