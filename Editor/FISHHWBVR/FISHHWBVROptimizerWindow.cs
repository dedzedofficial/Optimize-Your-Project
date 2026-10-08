using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using static FISHHWB.VROptimizer.OYPLocalization;

namespace FISHHWB.VROptimizer
{
    internal sealed class FISHHWBVROptimizerWindow : EditorWindow
    {
        enum Page { Project, Avatar }
        enum Filter { All, Critical, Warning }

        static readonly int[] Sizes = { 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384 };
        static readonly string[] SizeNames = { "32", "64", "128", "256", "512", "1024", "2048", "4096", "8192", "16384", "Custom..." };

        VRSettings settings;
        Page page;
        Filter filter;
        GameObject avatar;
        string projectFolder = "Assets";
        Texture2D icon;
        Vector2 scroll;
        List<VRIssue> issues;
        ModelImporterMeshCompression meshLevel = ModelImporterMeshCompression.Medium;
        string summary;
        bool showAdvanced;
        bool showTextureSettings;
        bool showParticleControls;
        bool showMeshSettings;
        bool testImportedMemory;

        GUIStyle panelStyle;
        GUIStyle sectionTitleStyle;
        GUIStyle mutedStyle;
        GUIStyle primaryButtonStyle;
        GUIStyle compactButtonStyle;
        GUIStyle heroButtonStyle;

        [MenuItem("FISHHWB/Optimize Your Project")]
        static void Open()
        {
            var window = GetWindow<FISHHWBVROptimizerWindow>();
            window.minSize = new Vector2(500, 570);
            window.titleContent = new GUIContent("Optimize Your Project", window.icon);
        }

        void OnEnable()
        {
            settings = VRSettings.Load();
            icon = AssetDatabase.LoadAssetAtPath<Texture2D>(
                "Packages/com.fishhwb.vr-optimizer/Editor/FISHHWBVR/Icons/Optimize-Your-Project.png");
            titleContent = new GUIContent("Optimize Your Project", icon);
            summary = T("ready");
            VRUpdateChecker.CheckIfDue();
        }

        void OnGUI()
        {
            if (settings == null) settings = VRSettings.Load();
            EnsureStyles();

            DrawHeader();
            DrawTopBar();

            scroll = EditorGUILayout.BeginScrollView(scroll);
            GUILayout.Space(10);
            EditorGUILayout.BeginHorizontal();
            GUILayout.Space(12);
            EditorGUILayout.BeginVertical();

            if (page == Page.Project) DrawProject();
            else DrawAvatar();

            DrawIssues();
            DrawResultStrip();
            DrawFooter();

            EditorGUILayout.EndVertical();
            GUILayout.Space(12);
            EditorGUILayout.EndHorizontal();
            GUILayout.Space(10);
            EditorGUILayout.EndScrollView();
        }

        void EnsureStyles()
        {
            if (panelStyle != null) return;

            panelStyle = new GUIStyle(EditorStyles.helpBox)
            {
                padding = new RectOffset(12, 12, 10, 11),
                margin = new RectOffset(0, 0, 0, 8)
            };

            sectionTitleStyle = new GUIStyle(EditorStyles.boldLabel)
            {
                fontSize = 11,
                wordWrap = true
            };

            mutedStyle = new GUIStyle(EditorStyles.wordWrappedMiniLabel)
            {
                fontSize = 10,
                wordWrap = true
            };

            primaryButtonStyle = new GUIStyle(GUI.skin.button)
            {
                fontStyle = FontStyle.Bold,
                fixedHeight = 36,
                margin = new RectOffset(2, 2, 3, 3),
                wordWrap = true,
                alignment = TextAnchor.MiddleCenter
            };

            compactButtonStyle = new GUIStyle(GUI.skin.button)
            {
                fixedHeight = 30,
                margin = new RectOffset(2, 2, 2, 2),
                wordWrap = true,
                alignment = TextAnchor.MiddleCenter
            };

            heroButtonStyle = new GUIStyle(GUI.skin.button)
            {
                fontStyle = FontStyle.Bold,
                fontSize = 12,
                fixedHeight = 42,
                margin = new RectOffset(1, 1, 5, 6),
                wordWrap = true,
                alignment = TextAnchor.MiddleCenter
            };
        }

        void DrawHeader()
        {
            var rect = GUILayoutUtility.GetRect(1, 64, GUILayout.ExpandWidth(true));
            var background = EditorGUIUtility.isProSkin
                ? new Color(.075f, .085f, .095f)
                : new Color(.93f, .94f, .95f);
            EditorGUI.DrawRect(rect, background);

            if (icon)
                GUI.DrawTexture(new Rect(rect.x + 14, rect.y + 12, 40, 40), icon, ScaleMode.ScaleToFit, true);

            var title = new GUIStyle(EditorStyles.boldLabel) { fontSize = 16 };
            var detail = new GUIStyle(EditorStyles.miniLabel) { fontSize = 10 };
            if (EditorGUIUtility.isProSkin)
            {
                title.normal.textColor = Color.white;
                detail.normal.textColor = new Color(.70f, .74f, .78f);
            }

            GUI.Label(new Rect(rect.x + 66, rect.y + 11, rect.width - 160, 24), "Optimize Your Project", title);
            GUI.Label(new Rect(rect.x + 66, rect.y + 36, rect.width - 160, 18), T("developer_optimizer"), detail);
            GUI.Label(new Rect(rect.xMax - 88, rect.y + 22, 74, 20), "v" + VRUpdateChecker.CurrentVersion, detail);
        }

        void DrawTopBar()
        {
            EditorGUILayout.BeginHorizontal(EditorStyles.toolbar);
            int next = GUILayout.Toolbar(
                (int)page,
                new[] { T("project"), T("avatar") },
                EditorStyles.toolbarButton,
                GUILayout.ExpandWidth(true));
            EditorGUILayout.EndHorizontal();

            if (next != (int)page)
            {
                page = (Page)next;
                issues = null;
                summary = T("ready");
            }

            EditorGUILayout.BeginHorizontal(EditorStyles.toolbar);
            GUILayout.Space(8);
            GUILayout.Label(T("language"), EditorStyles.miniLabel, GUILayout.Width(72));
            int language = (int)OYPLocalization.Current;
            int selected = EditorGUILayout.Popup(
                language,
                OYPLocalization.LanguageNames,
                EditorStyles.toolbarPopup,
                GUILayout.MinWidth(210));
            if (selected != language)
            {
                OYPLocalization.Current = (OYPLanguage)selected;
                summary = T("ready");
                Repaint();
            }
            GUILayout.FlexibleSpace();
            EditorGUILayout.EndHorizontal();
        }

        void DrawProject()
        {
            bool valid = DrawProjectScope();
            DrawOptimizeArea(null, projectFolder, valid, false);
            DrawProjectReview(valid);
            DrawDangerZone(valid);
        }

        bool DrawProjectScope()
        {
            EditorGUILayout.BeginVertical(panelStyle);
            EditorGUILayout.LabelField(T("project_scope"), sectionTitleStyle);
            EditorGUILayout.BeginHorizontal();
            projectFolder = EditorGUILayout.TextField(projectFolder, GUILayout.MinWidth(260));
            if (GUILayout.Button(T("use_selection"), compactButtonStyle, GUILayout.Width(132)))
                projectFolder = VRProjectInsights.FolderFromSelection(projectFolder);
            EditorGUILayout.EndHorizontal();

            bool valid = projectFolder == "Assets" ||
                         projectFolder.StartsWith("Assets/", StringComparison.Ordinal) &&
                         AssetDatabase.IsValidFolder(projectFolder);
            EditorGUILayout.LabelField(T("scope_help"), mutedStyle);
            if (!valid)
                EditorGUILayout.HelpBox(T("invalid_folder"), MessageType.Warning);

            EditorGUILayout.EndVertical();
            return valid;
        }

        void DrawAvatar()
        {
            EditorGUILayout.BeginVertical(panelStyle);
            EditorGUILayout.LabelField(T("avatar_root"), sectionTitleStyle);
            EditorGUILayout.BeginHorizontal();
            avatar = (GameObject)EditorGUILayout.ObjectField(avatar, typeof(GameObject), true);
            if (GUILayout.Button(T("use_selection"), compactButtonStyle, GUILayout.Width(132)))
                avatar = Selection.activeGameObject;
            EditorGUILayout.EndHorizontal();

            bool valid = VRAvatarWorkflow.EditableRoot(avatar);
            if (!valid)
                EditorGUILayout.LabelField(T("avatar_help"), mutedStyle);
            EditorGUILayout.EndVertical();

            DrawOptimizeArea(avatar, "Assets", valid, true);

            DrawSectionLabel(T("review"));
            EditorGUILayout.BeginVertical(panelStyle);
            using (new EditorGUI.DisabledScope(!valid))
            {
                if (Compact(T("heavy_meshes")))
                {
                    issues = VRProjectInsights.OversizedMeshes(avatar);
                    summary = "Heavy mesh review: " + issues.Count + " candidates.";
                }
            }
            EditorGUILayout.EndVertical();
        }

        void DrawOptimizeArea(GameObject root, string folder, bool valid, bool avatarScope)
        {
            DrawSectionLabel(T("one_click"));
            EditorGUILayout.BeginVertical(panelStyle);

            using (new EditorGUI.DisabledScope(!valid))
            {
                EditorGUILayout.BeginHorizontal();
                if (Primary(T("optimize_textures"))) OptimizeTextures(root, folder);
                if (Primary(T("optimize_models"))) OptimizeModelImports(root);
                EditorGUILayout.EndHorizontal();

                EditorGUILayout.BeginHorizontal();
                if (Primary(T("optimize_particles"))) OptimizeParticles(root);
                if (Primary(T("fix_materials"))) FixExpensiveMaterialSetups(root, folder);
                EditorGUILayout.EndHorizontal();

                EditorGUILayout.BeginHorizontal();
                if (avatarScope)
                {
                    if (Primary(T("disable_shadows"))) DisableRealtimeShadows(root);
                }
                else
                {
                    using (new EditorGUI.DisabledScope(EditorApplication.isPlayingOrWillChangePlaymode || Lightmapping.isRunning))
                        if (Primary(T("optimize_lighting"))) summary = VRLightingSetup.Optimize();
                }

                if (Primary(T("optimize_ui_raycasts"))) summary = VRUIRaycastOptimizer.Optimize(root);
                EditorGUILayout.EndHorizontal();

                EditorGUILayout.BeginHorizontal();
                if (!avatarScope)
                {
                    if (Primary(T("optimize_audio"))) summary = VRAudioOptimizer.Optimize(folder);
                }
                else
                {
                    GUILayout.FlexibleSpace();
                }
                if (Primary(T("clean_missing_scripts"))) summary = VRMissingScriptCleaner.Clean(root);
                EditorGUILayout.EndHorizontal();
            }

            DrawAdvancedSettings();
            EditorGUILayout.EndVertical();
        }

        void DrawProjectReview(bool valid)
        {
            DrawSectionLabel(T("review"));
            EditorGUILayout.BeginVertical(panelStyle);
            EditorGUILayout.BeginHorizontal();
            using (new EditorGUI.DisabledScope(!valid))
            {
                if (Compact(T("largest_textures")))
                {
                    issues = VRProjectInsights.LargestTextures(projectFolder);
                    summary = "Largest texture review: " + issues.Count + " candidates.";
                }

                if (Compact(T("readwrite_review")))
                {
                    issues = VRProjectInsights.ReadWriteReview(projectFolder);
                    summary = "Read/Write review: " + issues.Count + " candidates.";
                }
            }
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.BeginHorizontal();
            if (Compact(T("heavy_meshes")))
            {
                issues = VRProjectInsights.OversizedMeshes(null);
                summary = "Heavy mesh review: " + issues.Count + " candidates.";
            }

            if (Compact(T("scan_project")))
            {
                issues = VRProjectScanner.Scan(settings, null, out bool cancelled);
                summary = (cancelled ? "Partial scan: " : "Project scan complete: ") + issues.Count + " findings.";
            }
            EditorGUILayout.EndHorizontal();
            EditorGUILayout.EndVertical();
        }

        void DrawDangerZone(bool valid)
        {
            DrawSectionLabel(T("danger_zone"));
            EditorGUILayout.BeginVertical(panelStyle);
            EditorGUILayout.HelpBox(T("unused_assets_warning"), MessageType.Warning);
            using (new EditorGUI.DisabledScope(!valid))
            {
                if (GUILayout.Button(T("delete_unused_assets"), heroButtonStyle))
                    summary = VRUnusedAssetCleaner.DeleteUnused(projectFolder);
            }
            EditorGUILayout.EndVertical();
        }

        void DrawSectionLabel(string label)
        {
            GUILayout.Space(4);
            EditorGUILayout.LabelField(label, sectionTitleStyle);
        }

        bool Primary(string label)
        {
            return GUILayout.Button(label, primaryButtonStyle, GUILayout.ExpandWidth(true));
        }

        bool Compact(string label)
        {
            return GUILayout.Button(label, compactButtonStyle, GUILayout.ExpandWidth(true));
        }

        void DrawAdvancedSettings()
        {
            showAdvanced = EditorGUILayout.Foldout(showAdvanced, T("advanced"), true);
            if (!showAdvanced) return;

            GUILayout.Space(4);
            EditorGUI.BeginChangeCheck();

            showTextureSettings = EditorGUILayout.Foldout(showTextureSettings, T("texture_settings"), true);
            if (showTextureSettings)
            {
                settings.pc = SizeField(T("pc"), settings.pc);
                settings.android = SizeField(T("android"), settings.android);
                settings.ios = SizeField(T("ios"), settings.ios);
            }

            showParticleControls = EditorGUILayout.Foldout(showParticleControls, T("particle_settings"), true);
            if (showParticleControls)
            {
                settings.capParticles = EditorGUILayout.Toggle(T("cap_particles"), settings.capParticles);
                if (settings.capParticles)
                    settings.maxParticles = EditorGUILayout.IntField(T("max_particles"), settings.maxParticles);

                settings.capLifetime = EditorGUILayout.Toggle(T("cap_lifetime"), settings.capLifetime);
                if (settings.capLifetime)
                    settings.maxLifetime = EditorGUILayout.FloatField(T("max_lifetime"), settings.maxLifetime);

                settings.disableTrails = EditorGUILayout.Toggle(T("disable_trails"), settings.disableTrails);
                settings.disableCollision = EditorGUILayout.Toggle(T("disable_collision"), settings.disableCollision);
                settings.disableNoise = EditorGUILayout.Toggle(T("disable_noise"), settings.disableNoise);
                settings.disableLights = EditorGUILayout.Toggle(T("disable_particle_lights"), settings.disableLights);
                settings.disableShadows = EditorGUILayout.Toggle(T("disable_particle_shadows"), settings.disableShadows);
                settings.disableSubEmitters = EditorGUILayout.Toggle(T("disable_subemitters"), settings.disableSubEmitters);
            }

            showMeshSettings = EditorGUILayout.Foldout(showMeshSettings, T("model_settings"), true);
            if (showMeshSettings)
                meshLevel = (ModelImporterMeshCompression)EditorGUILayout.EnumPopup(T("compression"), meshLevel);

            if (EditorGUI.EndChangeCheck())
            {
                settings.Sanitize();
                settings.Save();
            }

            GUILayout.Space(4);
            DrawImportOptions(true);
        }

        static int SizeField(string label, int value)
        {
            int index = Array.IndexOf(Sizes, value);
            int selected = EditorGUILayout.Popup(label, index < 0 ? Sizes.Length : index, SizeNames);
            if (selected < Sizes.Length)
                return Sizes[selected];

            int typed = EditorGUILayout.IntField("Custom " + label, value);
            return Mathf.Clamp(Mathf.ClosestPowerOfTwo(Mathf.Max(32, typed)), 32, 16384);
        }

        void OptimizeTextures(GameObject root, string folder, bool confirm = true)
        {
            settings.Sanitize();
            var textures = VRAvatarWorkflow.CollectTextures(root, settings, folder, out int unsupported);
            var compression = VRTextureCompression.Collect(root, folder, out bool scanCancelled);

            if (scanCancelled)
            {
                summary = new VRActionSummary { Cancelled = true, Skipped = textures.Count, Unsupported = unsupported }.Format("Textures") + "\nNo changes applied.";
                return;
            }

            var importFixes = new Dictionary<string, VRTextureImportFix>(StringComparer.Ordinal);
            foreach (var fix in VRProjectMaintenance.CollectTextureImportFixes(folder))
                importFixes[fix.Path] = fix;

            var byPath = new Dictionary<string, List<VRCompressionChange>>(StringComparer.Ordinal);
            foreach (var item in compression)
            {
                if (!byPath.TryGetValue(item.Path, out var list))
                {
                    list = new List<VRCompressionChange>();
                    byPath.Add(item.Path, list);
                }
                list.Add(item);
            }

            if (textures.Count == 0)
            {
                summary = new VRActionSummary { Unsupported = unsupported }.Format("Textures") + "\nNo supported textures found in this scope.";
                return;
            }

            if (confirm && !EditorUtility.DisplayDialog(
                "Optimize textures",
                "Optimize " + textures.Count + " supported textures? Recognized normal/data imports are repaired. Existing explicit formats and stricter size caps are preserved.",
                "Optimize",
                "Cancel"))
            {
                summary = new VRActionSummary { Cancelled = true, Skipped = textures.Count, Unsupported = unsupported }.Format("Textures");
                return;
            }

            var batch = new VRImportBatch();
            string policy = "textures-v0800:" + settings.pc + ":" + settings.android + ":" + settings.ios + ":" + testImportedMemory;
            var result = VRActionSummary.Run("Textures", textures, item => item.Path, item =>
                batch.Apply(item.Path, "textures", policy, () =>
            {
                var importer = AssetImporter.GetAtPath(item.Path) as TextureImporter;
                if (!importer || importer.textureShape != TextureImporterShape.Texture2D ||
                    (importer.textureType != TextureImporterType.Default && importer.textureType != TextureImporterType.NormalMap))
                    return VRActionOutcome.Unsupported;

                bool repaired = importFixes.TryGetValue(item.Path, out var fix) &&
                    VRProjectMaintenance.ApplyTextureImportFix(fix, false) == VRActionOutcome.Changed;
                byPath.TryGetValue(item.Path, out var entries);
                bool optimized = VRTextureOptimizer.OptimizeWithCompression(item.Path, settings, entries, repaired);
                return repaired || optimized ? VRActionOutcome.Changed : VRActionOutcome.Unchanged;
            }, testImportedMemory), unsupported);

            summary = result.Format("Textures") + batch.Details(testImportedMemory);
        }

        void OptimizeParticles(GameObject root)
        {
            var particles = new List<ParticleSystem>(
                root
                    ? (IEnumerable<ParticleSystem>)root.GetComponentsInChildren<ParticleSystem>(true)
                    : VRProjectScanner.SceneObjects<ParticleSystem>());

            Undo.IncrementCurrentGroup();
            int group = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName("Optimize Particles");
            try
            {
                var result = VRActionSummary.Run("Particles", particles,
                    item => item ? item.name : "Missing particle system", item =>
                    {
                        if (!item) return VRActionOutcome.Skipped;
                        return VRParticleOptimizer.Optimize(item, settings)
                            ? VRActionOutcome.Changed : VRActionOutcome.Unchanged;
                    });
                summary = result.Format("Particles") + "\nUse Undo if needed.";
            }
            finally
            {
                Undo.CollapseUndoOperations(group);
            }
        }

        void OptimizeModelImports(GameObject root, bool confirm = true)
        {
            var meshes = VRMeshCompression.Collect(root, out int unsupported);
            int pending = 0;
            foreach (var mesh in meshes)
            {
                var model = AssetImporter.GetAtPath(mesh.Path) as ModelImporter;
                if (!model) continue;
                var desired = StrongerCompression(model.meshCompression, meshLevel);
                if (model.meshCompression != desired || !model.optimizeMeshVertices || !model.optimizeMeshPolygons)
                    pending++;
            }

            if (pending == 0)
            {
                summary = new VRActionSummary { Unchanged = meshes.Count, Unsupported = unsupported }.Format("Imported meshes");
                return;
            }

            if (confirm && !EditorUtility.DisplayDialog(
                "Optimize model imports",
                "Reimport " + pending + " model assets using at least " + meshLevel + " compression and Unity mesh import optimization? " +
                "A stronger existing compression level is preserved. Triangle counts, Read/Write, rigs, animations and blendshapes are left unchanged.",
                "Optimize",
                "Cancel"))
            {
                summary = new VRActionSummary { Cancelled = true, Skipped = meshes.Count, Unsupported = unsupported }.Format("Imported meshes");
                return;
            }

            var batch = new VRImportBatch();
            var result = VRActionSummary.Run("Imported meshes", meshes, item => item.Path, item =>
                batch.Apply(item.Path, "models", "models-v0800:" + meshLevel + ":" + testImportedMemory, () =>
            {
                var importer = AssetImporter.GetAtPath(item.Path) as ModelImporter;
                if (!importer) return VRActionOutcome.Unsupported;
                var desired = StrongerCompression(importer.meshCompression, meshLevel);
                if (importer.meshCompression == desired && importer.optimizeMeshVertices && importer.optimizeMeshPolygons)
                    return VRActionOutcome.Unchanged;

                importer.meshCompression = desired;
                importer.optimizeMeshVertices = true;
                importer.optimizeMeshPolygons = true;
                importer.SaveAndReimport();
                return VRActionOutcome.Changed;
            }, testImportedMemory), unsupported);

            summary = result.Format("Imported meshes") + batch.Details(testImportedMemory);
        }

        static ModelImporterMeshCompression StrongerCompression(ModelImporterMeshCompression current, ModelImporterMeshCompression requested)
        {
            return (ModelImporterMeshCompression)Mathf.Max((int)current, (int)requested);
        }

        void FixExpensiveMaterialSetups(GameObject root, string folder, bool confirm = true)
        {
            var duplicates = VRProjectMaintenance.CollectDuplicateMaterialFixes(root, folder);
            var slots = VRProjectMaintenance.CollectUnusedMaterialSlots(root);
            int replacements = 0;
            int remove = 0;
            foreach (var fix in duplicates) replacements += fix.ReplacementCount;
            foreach (var fix in slots) remove += fix.RemoveCount;

            if (duplicates.Count == 0 && slots.Count == 0)
            {
                summary = "Material cost fix: no exact duplicate references or safe trailing empty slots need changes.";
                issues = null;
                return;
            }

            if (confirm && !EditorUtility.DisplayDialog(
                "Fix material cost issues",
                "Apply safe material fixes in this loaded scope?\n\nExact duplicate references: " + replacements +
                "\nTrailing empty slots: " + remove +
                "\n\nThis does not merge mesh submeshes or alter shader design. Unity Undo is available.",
                "Fix Safe Issues",
                "Cancel"))
            {
                summary = "Material cost fix cancelled.";
                return;
            }

            Undo.IncrementCurrentGroup();
            int group = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName("Fix Material Cost Issues");
            try
            {
                var duplicateResult = VRActionSummary.Run(
                    "Duplicate materials",
                    duplicates,
                    item => item.Renderer ? item.Renderer.name : "Missing renderer",
                    VRProjectMaintenance.ApplyDuplicateMaterialFix);

                var slotResult = VRActionSummary.Run(
                    "Material slots",
                    slots,
                    item => item.Renderer ? item.Renderer.name : "Missing renderer",
                    VRProjectMaintenance.ApplyUnusedMaterialSlotFix);

                summary = "Material cost fixes complete:" +
                          "\nDuplicate references remapped: " + replacements +
                          "\nTrailing empty slots removed: " + remove +
                          "\nChanged renderers: " + (duplicateResult.Changed + slotResult.Changed) +
                          "\nHigh submesh counts that require topology or art changes are left untouched. Use Undo if needed.";
                issues = null;
            }
            finally
            {
                Undo.CollapseUndoOperations(group);
            }
        }

        void DisableRealtimeShadows(GameObject root)
        {
            var lights = new List<Light>(root.GetComponentsInChildren<Light>(true));
            int pending = 0;
            foreach (var light in lights)
                if (light && light.enabled && light.lightmapBakeType == LightmapBakeType.Realtime && light.shadows != LightShadows.None)
                    pending++;

            if (pending > 0 && !EditorUtility.DisplayDialog(
                "Disable realtime shadows",
                "Disable shadows on " + pending + " realtime lights? You can use Unity Undo to revert.",
                "Disable",
                "Cancel"))
            {
                summary = new VRActionSummary { Cancelled = true, Skipped = lights.Count }.Format("Realtime shadows");
                return;
            }

            Undo.IncrementCurrentGroup();
            int group = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName("Disable Realtime Shadows");
            try
            {
                var result = VRActionSummary.Run("Realtime shadows", lights,
                    item => item ? item.name : "Missing light", item =>
                    {
                        if (!item || !item.enabled) return VRActionOutcome.Skipped;
                        if (item.lightmapBakeType != LightmapBakeType.Realtime) return VRActionOutcome.Unsupported;
                        return VRLightOptimizer.Optimize(item, settings)
                            ? VRActionOutcome.Changed : VRActionOutcome.Unchanged;
                    });
                summary = result.Format("Realtime shadows") + "\nUse Undo if needed.";
            }
            finally
            {
                Undo.CollapseUndoOperations(group);
            }
        }

        void DrawImportOptions(bool allowTrial)
        {
            if (!GUILayout.Button(T("batch_options"), compactButtonStyle)) return;

            var menu = new GenericMenu();
            if (allowTrial)
                menu.AddItem(new GUIContent(T("test_import_memory")), testImportedMemory,
                    () => { testImportedMemory = !testImportedMemory; Repaint(); });

            menu.AddItem(new GUIContent(T("protect_detail")), false,
                () => { VRImportHistory.instance.SetProtection(VRImportHistory.SelectedPaths(), true); summary = T("detail_protected"); Repaint(); });
            menu.AddItem(new GUIContent(T("allow_detail")), false,
                () => { VRImportHistory.instance.SetProtection(VRImportHistory.SelectedPaths(), false); summary = T("detail_allowed"); Repaint(); });
            menu.AddItem(new GUIContent(T("reset_selected_history")), false,
                () => { VRImportHistory.instance.Forget(VRImportHistory.SelectedPaths()); summary = T("history_reset"); Repaint(); });
            menu.AddItem(new GUIContent(T("restore_import_batch")), false,
                () => { summary = VRImportHistory.instance.RestoreLastBatch(); Repaint(); });
            menu.ShowAsContext();
        }

        void DrawIssues()
        {
            if (issues == null) return;

            GUILayout.Space(6);
            EditorGUILayout.BeginVertical(panelStyle);
            EditorGUILayout.BeginHorizontal();
            EditorGUILayout.LabelField("Results  " + issues.Count, sectionTitleStyle);
            filter = (Filter)GUILayout.Toolbar((int)filter, new[] { T("all"), T("critical"), T("warning") }, GUILayout.MaxWidth(300));
            EditorGUILayout.EndHorizontal();

            int count = 0;
            foreach (var issue in issues)
            {
                if (filter == Filter.Critical && issue.Severity != VRSeverity.Critical ||
                    filter == Filter.Warning && issue.Severity != VRSeverity.Warning)
                    continue;

                count++;
                EditorGUILayout.BeginHorizontal(EditorStyles.helpBox);
                var severityDot = new GUIStyle(EditorStyles.boldLabel) { fontSize = 12 };
                severityDot.normal.textColor = issue.Severity == VRSeverity.Critical
                    ? new Color(.92f, .24f, .22f)
                    : new Color(1f, .58f, .12f);
                GUILayout.Label("●", severityDot, GUILayout.Width(17));

                EditorGUILayout.BeginVertical();
                EditorGUILayout.LabelField(issue.Message, EditorStyles.wordWrappedLabel);
                if (!string.IsNullOrEmpty(issue.AssetPath))
                    EditorGUILayout.LabelField(issue.AssetPath, mutedStyle);
                EditorGUILayout.EndVertical();

                using (new EditorGUI.DisabledScope(!issue.Target))
                {
                    if (GUILayout.Button(T("select"), GUILayout.Width(78)))
                    {
                        Selection.activeObject = issue.Target;
                        EditorGUIUtility.PingObject(issue.Target);
                    }
                }
                EditorGUILayout.EndHorizontal();
            }

            if (count == 0)
                EditorGUILayout.LabelField(T("no_findings"), mutedStyle);

            EditorGUILayout.EndVertical();
        }

        void DrawResultStrip()
        {
            GUILayout.Space(3);
            EditorGUILayout.BeginVertical(panelStyle);
            EditorGUILayout.LabelField(T("last_result"), sectionTitleStyle);
            EditorGUILayout.LabelField(summary ?? T("ready"), mutedStyle);
            EditorGUILayout.EndVertical();
        }

        void DrawFooter()
        {
            var health = VRUpdateChecker.Health;
            EditorGUILayout.BeginVertical(panelStyle);

            EditorGUILayout.BeginHorizontal();
            var dot = new GUIStyle(EditorStyles.boldLabel) { fontSize = 13 };
            dot.normal.textColor = StatusColor(health);
            GUILayout.Label("●", dot, GUILayout.Width(18));
            GUILayout.Label("v" + VRUpdateChecker.CurrentVersion, EditorStyles.miniBoldLabel, GUILayout.Width(66));

            string stateText;
            switch (health)
            {
                case VRUpdateHealth.Current: stateText = T("up_to_date"); break;
                case VRUpdateHealth.UpdateAvailable: stateText = T("update_available"); break;
                case VRUpdateHealth.FarBehind: stateText = T("update_recommended"); break;
                default: stateText = VRUpdateChecker.Checking ? T("checking") : T("update_unknown"); break;
            }
            GUILayout.Label(stateText, EditorStyles.miniLabel);
            GUILayout.FlexibleSpace();

            using (new EditorGUI.DisabledScope(VRUpdateChecker.Checking || VRUpdateChecker.Installing))
            {
                if (VRUpdateChecker.HasUpdate)
                {
                    string label = VRUpdateChecker.CanUpdateDirectly ? "Update " + VRUpdateChecker.LatestTag : "Update info";
                    if (GUILayout.Button(label, compactButtonStyle, GUILayout.Width(112)))
                        VRUpdateChecker.Update();
                }
                else if (GUILayout.Button(T("check_update"), compactButtonStyle, GUILayout.Width(112)))
                {
                    VRUpdateChecker.Check(true);
                }
            }
            EditorGUILayout.EndHorizontal();

            EditorGUILayout.BeginHorizontal();
            if (GUILayout.Button(T("support"), compactButtonStyle, GUILayout.Width(150)))
                Application.OpenURL("https://www.patreon.com/cw/DedZed");
            GUILayout.FlexibleSpace();
            if (GUILayout.Button("GitHub", EditorStyles.linkLabel))
                Application.OpenURL("https://github.com/dedzedofficial/Optimize-Your-Project");
            GUILayout.Space(10);
            if (GUILayout.Button("Website", EditorStyles.linkLabel))
                Application.OpenURL("https://fishhwb.github.io/");
            GUILayout.Space(10);
            if (GUILayout.Button("Discord", EditorStyles.linkLabel))
                Application.OpenURL("https://discord.gg/wZGxxkk4Jg");
            EditorGUILayout.EndHorizontal();

            if (!string.IsNullOrEmpty(VRUpdateChecker.Message) &&
                (health == VRUpdateHealth.Unknown || VRUpdateChecker.Installing))
                EditorGUILayout.LabelField(VRUpdateChecker.Message, mutedStyle);

            EditorGUILayout.EndVertical();
        }

        static Color StatusColor(VRUpdateHealth health)
        {
            switch (health)
            {
                case VRUpdateHealth.Current: return new Color(.25f, .82f, .38f);
                case VRUpdateHealth.UpdateAvailable: return new Color(1f, .58f, .12f);
                case VRUpdateHealth.FarBehind: return new Color(.92f, .24f, .22f);
                default: return new Color(.55f, .55f, .55f);
            }
        }
    }
}
