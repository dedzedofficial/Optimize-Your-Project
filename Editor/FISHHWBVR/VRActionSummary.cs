using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FISHHWB.VROptimizer
{
    internal enum VRActionOutcome { Changed, Unchanged, Skipped, Unsupported }

    internal sealed class VRActionSummary
    {
        internal int Changed, Unchanged, Skipped, Unsupported, Failed;
        internal bool Cancelled;

        internal string Format(string action)
        {
            return action + (Cancelled ? " cancelled. Partial results:" : " complete:") +
                "\nChanged: " + Changed + " | Unchanged: " + Unchanged +
                " | Skipped: " + Skipped + " | Unsupported: " + Unsupported + " | Failed: " + Failed;
        }

        // Each candidate has exactly one outcome. Unvisited candidates are skipped.
        internal static VRActionSummary Run<T>(string title, IList<T> items,
            Func<T, string> label, Func<T, VRActionOutcome> apply, int unsupported = 0)
        {
            var result = new VRActionSummary { Unsupported = unsupported };
            try
            {
                for (int i = 0; i < items.Count; i++)
                {
                    string itemLabel = "Item " + (i + 1);
                    try
                    {
                        itemLabel = label(items[i]);
                        if (EditorUtility.DisplayCancelableProgressBar(title, itemLabel, (float)i / items.Count))
                        {
                            result.Cancelled = true;
                            result.Skipped += items.Count - i;
                            break;
                        }
                        switch (apply(items[i]))
                        {
                            case VRActionOutcome.Changed: result.Changed++; break;
                            case VRActionOutcome.Unchanged: result.Unchanged++; break;
                            case VRActionOutcome.Skipped: result.Skipped++; break;
                            case VRActionOutcome.Unsupported: result.Unsupported++; break;
                        }
                    }
                    catch (Exception error)
                    {
                        result.Failed++;
                        Debug.LogError("Optimize Your Project: " + title + ": " + itemLabel + ": " + error);
                    }
                }
            }
            finally { EditorUtility.ClearProgressBar(); }
            return result;
        }
    }
}
