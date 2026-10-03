using System;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace FISHHWB.VROptimizer
{
    internal static class VRLightingSetup
    {
        internal static string Optimize()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode || Lightmapping.isRunning)
                return "Lighting setup unavailable during play or an existing bake.";
            if (PrefabStageUtility.GetCurrentPrefabStage() != null)
                return "Open a scene before optimizing lighting; prefab editing is unsupported.";
            // Baking requires saved scene assets. Never silently save unrelated edits.
            for (int i = 0; i < SceneManager.sceneCount; i++)
            {
                var scene = SceneManager.GetSceneAt(i);
                if (!scene.isLoaded || EditorSceneManager.IsPreviewScene(scene)) continue;
                if (string.IsNullOrEmpty(scene.path))
                    return "Save all loaded scenes before optimizing lighting. No changes applied.";
                if (!Lightmapping.GetLightingSettingsForScene(scene) && !Lightmapping.lightingSettingsDefaults.bakedGI)
                    return "Assign Lighting Settings to each scene before optimizing lighting. No changes applied.";
            }
            Undo.IncrementCurrentGroup();
            int group = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName("Optimize Lighting Setup");
            int lights = 0, meshes = 0, skipped = 0;
            try
            {
                for (int i = 0; i < SceneManager.sceneCount; i++)
                {
                    var scene = SceneManager.GetSceneAt(i);
                    if (!scene.isLoaded || EditorSceneManager.IsPreviewScene(scene)) continue;
                    foreach (var root in scene.GetRootGameObjects())
                    {
                        foreach (var light in root.GetComponentsInChildren<Light>(true))
                        {
                            if (light.lightmapBakeType == LightmapBakeType.Baked) continue;
                            Undo.RecordObject(light, "Set Baked Light");
                            light.lightmapBakeType = LightmapBakeType.Baked;
                            PrefabUtility.RecordPrefabInstancePropertyModifications(light);
                            EditorUtility.SetDirty(light);
                            lights++;
                        }
                        foreach (var renderer in root.GetComponentsInChildren<MeshRenderer>(true))
                        {
                            var filter = renderer.GetComponent<MeshFilter>();
                            if (!filter || !filter.sharedMesh || Dynamic(renderer.transform)) { skipped++; continue; }
                            var go = renderer.gameObject;
                            var flags = GameObjectUtility.GetStaticEditorFlags(go);
                            var desired = flags | StaticEditorFlags.ContributeGI | StaticEditorFlags.BatchingStatic;
                            bool change = flags != desired || renderer.receiveGI != ReceiveGI.Lightmaps;
                            if (!change) continue;
                            Undo.RecordObject(go, "Set Static Lighting Flags");
                            Undo.RecordObject(renderer, "Receive Baked Lighting");
                            // Lighting/batching flags only: navigation and occlusion require separate validation.
                            GameObjectUtility.SetStaticEditorFlags(go, desired);
                            renderer.receiveGI = ReceiveGI.Lightmaps;
                            PrefabUtility.RecordPrefabInstancePropertyModifications(go);
                            PrefabUtility.RecordPrefabInstancePropertyModifications(renderer);
                            meshes++;
                        }
                    }
                    var lighting = Lightmapping.GetLightingSettingsForScene(scene);
                    // Scenes without an explicit asset use Unity's baked-GI defaults.
                    // Do not create transient settings that are lost after closing the scene.
                    if (lighting && (!lighting.bakedGI || lighting.autoGenerate))
                    {
                        Undo.RecordObject(lighting, "Enable Baked GI");
                        lighting.bakedGI = true;
                        lighting.autoGenerate = false;
                        EditorUtility.SetDirty(lighting);
                    }
                    EditorSceneManager.MarkSceneDirty(scene);
                }
                bool started = Lightmapping.BakeAsync();
                return "Lighting setup: " + lights + " lights changed, " + meshes + " meshes changed, " + skipped +
                    " dynamic/unsupported meshes skipped. " + (started ? "Bake started; check Unity Lighting for completion." :
                    "Bake did not start; inspect Unity Console and Lighting settings.") +
                    " Setup supports Undo; baked files do not. Custom scripted movement must be reviewed.";
            }
            catch (Exception ex)
            {
                Undo.RevertAllDownToGroup(group);
                return "Lighting setup failed and setup changes were reverted: " + ex.Message;
            }
            finally { Undo.CollapseUndoOperations(group); }
        }

        static bool Dynamic(Transform transform)
        {
            for (var current = transform; current; current = current.parent)
                if (current.GetComponent<Animator>() || current.GetComponent<Animation>() ||
                    current.GetComponent<Rigidbody>() || current.GetComponent<Rigidbody2D>() ||
                    current.GetComponent<SkinnedMeshRenderer>()) return true;
            return false;
        }
    }
}
