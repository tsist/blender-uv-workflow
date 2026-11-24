# 契约路径、Wiki 索引与历史依据

本文件集中存放 UV 技能对应的源码与契约路径、本地共享 Wiki 知识条目、行业原始资料链接及历史审计证据目录。正文与工艺参考保持精简，溯源和复查时在此查找。

## 源码、契约与公共入口

- 公共 CLI 入口：`./blenderctl.ps1`（通过 `discover --product uv` 与 `uv describe` 实时查询当前宿主、插件版本、CLI 版本与实现 SHA256）
- UV 契约定义：`tools/uv_workflow_addon\contract.py`
- UV 插件核心目录：`tools/uv_workflow_addon\`
- CLI 适配与独立重开校验：`tools/blenderctl\uv_workflow.py`、`uv_verifier.py`、`uv_batch.py`、`uv_grid_transfer.py`、`uv_saved_protection.py`
- UV 与材质交接指南：`<PROJECT_ROOT>/docs\cli\workflows\uv-material-handoffs.md`
- 材质高低模烘焙说明：`tools/material_workflow_addon\README.md`
- 跨部门工序与审看节点：`./.agents/skills\blender-work-methodology\references\departments\surfacing.md`

## 本地共享 Wiki 知识库索引

查阅以下专题可获取完整推导、正反例数据与实验细节（通过 `wiki_get` 或 `wiki_query` 读取）：

- **学习路径与制作准备**：`procedures/uv-domain-learning-and-production-readiness.md`、`references/game-asset-uv-learning-curriculum.md`、`references/uv-learning-cases-materials-channels-and-failed-inference.md`
- **角色、生物与服装**：`procedures/character-uv-materials-atlas-and-production-methodology.md`、`references/aaa-character-uv-references-bg3-re3-2026.md`、`procedures/quadruped-uv-consumers-seams-and-fur-coordinates.md`、`references/blender-studio-autumn-quadruped-rig-benchmark.md`、`procedures/garment-uv-grain-direction-and-preserved-allocation.md`
- **透明发卡与薄面采样**：`procedures/alpha-card-uv-consumers-and-root-tip-validation.md`、`procedures/uv-thin-surface-pixel-budgets-and-shared-base-consumers.md`
- **硬表面、载具与环境动态**：`procedures/hard-surface-uv-lettering-and-normal-consumers.md`、`procedures/vehicle-uv-coordinate-consumers-and-rigid-parts.md`、`procedures/uv-environment-modular-interfaces-and-atlas-protection.md`、`procedures/uv-natural-surfaces-trunk-leaf-and-world-consumers.md`、`procedures/uv-animated-flipbook-and-panner-consumers.md`
- **排布效率、求解器与拓扑处理**：`procedures/uv-packing-efficiency-and-physical-pixel-gaps.md`、`procedures/uv-auxiliary-numeric-gates-and-solver-selection.md`、`procedures/uv-nonplanar-quad-triangulation-and-local-rechart.md`、`procedures/uv-render-vertex-splits-and-static-editing-representation.md`
- **迁移、烘焙与批量恢复**：`procedures/blender-uv-bounded-topology-transfer.md`、`procedures/uv-color-atlas-migration-and-channel-packed-textures.md`、`procedures/blender-pbr-baking.md`、`procedures/blender-uv-batch-recovery-and-qualification.md`

## 行业原始参考来源

- Adobe Substance 3D Painter：[Project Creation](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/getting-started/project-creation) · [Texture Set settings](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/interface/texture-set/texture-set-settings) · [Texture dilation or Padding](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/technical-support/workflow-issues/export-issues/texture-dilation-or-padding)
- Blender Studio：[A UV Unwrapping Guide](https://studio.blender.org/blog/a-uv-unwrapping-guide/)
- Frozenbyte：[3D Asset Workflow: UV Mapping](https://wiki.frozenbyte.com/index.php/3D_Asset_Workflow:_UV_Mapping)
- Funcom：[Conan Exiles Armor and Clothing Modelling Primer](https://www.conanexiles.com/wp-content/wiki/2693791979.html)
- Epic Games：[MetaHuman Assets Overview](https://dev.epicgames.com/documentation/metahuman/assets-overview?lang=en-US) · [Groom Materials in Unreal Engine](https://dev.epicgames.com/documentation/en-us/unreal-engine/groom-materials-in-unreal-engine)
- Ephere Ornatrix：[Hair Cards](https://ephere.com/ornatrix/app/docs/1/Hair_Cards.html)
- 工作室技术分享：Alena Dubrovina / Larian [Creating Characters for Baldur's Gate 3](https://80.lv/articles/creating-characters-for-baldur-s-gate-3)；Square Enix GDC2017 [Achieving High-Quality, Low-Cost Skin](https://www.jp.square-enix.com/tech/library/pdf/GDC2017_characterskin.pdf)；Zach Tsiakalis-Brown [Realtime Dynamic Gore Decals](https://www.zulubo.com/blog/realtime-dynamic-gore-decals)；Phosphor Games [Optimizing mobile VR character art](https://www.phosphorgames.com/post/optimizing-mobile-vr-character-art)；Mariia Zatorska [Real-time Hair Creation Workflow](https://marizatorska.artstation.com/blog/40NN/real-time-hair-creation-workflow)

## 历史审计与实证目录（供复查溯源）

下列目录位于 `work/audit/<batch>/`，保存各阶段能力验证、受控基准与反例报告：

- 公共入口与最新实证：`uv-grid-transfer-public-20261119-v001/`、`uv-micro-island-public-20261119-v001/`、`uv-software-closeout-20261117-v001/`、`self-plugin-action-map-20261120/asset-build/coverage.md`
- 求解器、报告校验与界面验收：`uv-ui-acceptance-20261116-v001/`、`uv-report-integrity-20261116-v001/`、`uv-job-monitor-20261114-v002/`、`uv-performance-20261115-v001/`、`uv-plan-audit-20261113-v001/`
- 角色与有机资产实证：`uv-development-20261113-m5-v002/`、`uv-development-20261113-m5-v003/`、`uv-character-methodology-20261113-v001/`、`uv-repack-20261114-v001/`、`uv-hand-refine-20261114-v001/`、`uv-orange-thumbsplit-20261115-v001/`、`uv-aaa-validation-20261115-v001/`、`uv-knowledge-d02-20261114-v001/`
- 服装与发卡实证：`uv-d02-next-20261114-v001/`、`uv-garment-native-20261114-v001/`、`uv-cloth-stretch-repair-20261114-v001/`、`uv-cloth-seam-freedom-20261114-v001/`、`uv-d04-cards-20261114-v001/`、`uv-d04-real-cards-20261114-v001/`、`uv-d04-scale-filter-20261114-v001/`
- 硬表面、载具、建筑与排布效率：`uv-d05-prop-20261114-v001/`、`uv-d05-surface-20261114-v001/`、`uv-d05-seams-20261114-v001/`、`uv-d05-followup-20261114-v001/`、`uv-d05-closure-20261115-v001/`、`uv-d06-vehicle-20261115-v001/`、`uv-efficiency-20261115-v001/`、`uv-edge-marks-20261115-v001/`、`uv-scene-intake-20261116-v001/`、`uv-reuse-scaling-20261116-v001/`、`uv-final-surface-20261116-v001/`、`uv-domain-stage8-20261115-v001/`
- 贴图迁移、法线与交换实证：`uv-aaa-fullasset-20261115-v001/`、`uv-normal-transfer-20261115-v001/`、`uv-single-uv-normal-20261116-v001/`、`uv-residual-repair-20261116-v001/`、`uv-two-residual-specialist-20261116-v001/`、`uv-aaa-glb-consumer-20261115-v001/`、`uv-aaa-glb-alpha-20261115-v001/`、`uv-generated-positive-20261115-v001/`、`uv-closeout-20261116-v001/`
