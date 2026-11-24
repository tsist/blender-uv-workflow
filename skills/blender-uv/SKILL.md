---
name: blender-uv
description: 在定稿白模上规划接缝、展开 UV、分配像素密度并完成棋盘与冷重开核验，交付可编辑的 UV 工作副本。接到资产、角色、硬表面或场景的展 UV、重排、局部修补、光照 UV2 生成或拓扑迁移任务时使用。
metadata:
  version: "1.0.0"
---

# Blender UV 制作手册

本技能属于 [UV 与材质部门](https://github.com/tsist/blender-ai-workflow/blob/main/skills/blender-work-methodology/references/departments/surfacing.md)，负责在定稿白模上展开合理、可编辑、可复查的 UV 候选，并交接给下游材质、烘焙或引擎环节。白模先经用户确认再展 UV，避免形体返工连累 UV 重展。原始工程保持只读，所有操作经公共入口写入新的作业目录与工作副本。

## 第一步：查明用途与表面消费者

先看表面怎么消费 UV，再决定怎么切、怎么排。直接运行公共只读入口摸清对象、UV 层、材质连线与几何健康度：

```powershell
$ctl  = './blenderctl.ps1'
$jobs = 'work/audit/<batch>/<批次名>\jobs'

& $ctl discover --product uv
& $ctl uv describe
& $ctl --jobs-dir $jobs uv inspect --params $inspectParams
```

动手前理清五件事：

1. **明确布局用途**：给独立绘制或烘焙用的面选 `EXCLUSIVE`（独占单图幅，确保不同布局单元无意外重叠）；给大面积重复纹理选 `TILED`（单图平铺，允许跨岛重复，保持单岛自身无折叠）；多个对象共用一张图时放进同一个 `uv.run` 请求做联合排布。
2. **核对旧贴图与着色器**：从 `inspect` 报告的 `consumers` 查清哪些图像节点读取 `active_render`（隐式绑定），哪些 `UV Map` 节点指定了层名（显式绑定）。已有成品贴图或既有 UDIM 时，保留原 UV 层与 `active_render` 绑定，另建新候选层操作。
3. **查几何健康度**：需要排查零面积三角、非流形边或重合面时，在 `inspect` 请求里加上 `"diagnostics": {"max_examples": 1000}`。发现几何缺陷时把精确的对象、面、边索引交回建模部门修复，修好后重新计算文件 SHA 再展 UV。
4. **选定像素密度与边距**：按近景镜头和图幅分配纹素预算（线密度提高 2 倍，所需像素面积约为 4 倍）。2K 图幅常规岛边距留 8–16 px，1K 紧凑硬表面或薄边至少留 4–8 px，防止降级采样串色。
5. **处理修改器与形态键**：带 `Mirror` 或 `Subsurf` 的硬表面，先把细分修改器的 `UV Smooth` 设为 `Keep Corners` 锁住边界转角，再对比基础网格与求值表面。本地单用户形态键网格可直接进入 `uv.run`；共享 Mesh 或库链接对象先在工作副本独立单用户化再推进。

## 第二步：规划接缝并生成有限候选

先在三维模型上把接缝藏进遮挡处、真实结构缝或自然转折边，再用 `uv.run` 生成 1–3 个可对比的候选层（层名自动带 `UVW_` 前缀，原层完好保留）。

- **先看只读建议缝**：在 `uv.inspect` 的 `manifest` 里加 `seam_suggestions`（指定 `angle_degrees` 与 `include_boundaries`），拿到按二面角和锐边筛出的建议边索引。
- **显式写入接缝**：运行 `uv.run` 的 `operation="seams"`，用 `MARK_BY_ANGLE`（可选 `sync_sharp: true` 同步锐边）或 `MARK_FROM_SHARP` 写入 `uv_seam`，或用 `MARK`/`CLEAR`/`REQUIRE_CUT`/`REQUIRE_JOIN` 精确控制单条边。
- **从界面选区捕获约束**：在 Blender 里选好边或面并切回 Object Mode 存盘，用 `uv capture-constraints --object <名> --kind must_cut|must_not_cut|locked_faces` 直接生成可复放的请求参数。

按模型特点选 1–3 种展开方法生成对比候选：

| 方法 | 适用场景 | 实操要点 |
|---|---|---|
| `ANGLE_BASED` | 已有清晰人工接缝或结构切边 | 严格沿源 `uv_seam`、开放边界和显式约束展开，保持切缝计划可控 |
| `MINIMUM_STRETCH` | 有机曲面、角色或低拉伸对照 | 调用原生 SLIM 最小拉伸求解，支持 `slim_iterations`（1–100，默认 10）与 `slim_no_flip`（默认 `true`） |
| `CONFORMAL` | 局部保角对照或硬表面平直块 | 与角度展开或 SLIM 并排比对拉伸与岛形 |
| `SMART_ABF` | 无硬约束的快速自动切缝基线 | 接受 `must_cut`/`must_not_cut`，自动分岛后再做角度优化 |
| `SMART_REPAIR` | 静态三角网的边界扇折叠修补 | 在智能投影后逐岛精检，局部重切开放边界扇；保留好岛原形 |
| `SMART` | 无约束快速摸底 | 仅作起点对照，正式交付优先改用显式接缝路线 |

需要给静态烘培光照准备第二套 UV 时，运行 `uv.run` 的 `operation="lightmap"` 生成非渲染附属层（默认 `UVMap_Lightmap`，支持 `width`/`height`、`box_div`、`margin_div` 与显式 `overwrite`），自动核验零重叠与 `[0, 1]` 范围并保持主渲染层不变。

## 第三步：定向、调密度、排布与局部精修

拿到候选后，对照拉伸、岛数、接缝位置与有效像素密度，在已有候选上用 `uv.run` 的 `operation="edit"` 做局部精修，或通过 `uv capture-selection` 接续在 Blender 界面里选好的面、岛或角点。

1. **先锁定方向与复用组**：带文字、木纹、拉丝或布料经纬的面，用 `edit` 的 `orient` 对齐有向边，再用 `settings` 登记方向规则与 `reuse_groups`（重复件声明完整岛复用，避免误报重叠）。
2. **再调重点区域密度**：对近景主面（如正脸、仪表盘、正面标识）执行整岛 `edit density` 设目标 `target_px_m`，把预算落到实处。
3. **按策略执行联合排布**：保持绝对密度时运行 `pack(scale=false)`；按区域比例填满图幅时先记录事前比例和下限，再跑 `pack(scale=true)` 并核对实际缩放系数与边距。有方向锁定的图幅把 `rotate` 设为 `false`。
4. **局部修补与合并微岛**：对局部拉长区域用 `FACES`/`ISLANDS` 做保边界 `relax` 或 `unwrap`（可选 `MINIMUM_STRETCH`），对连续选区用 `split` 切开并标缝，对共享边用 `stitch` 缝合；2K 静态独占三角图集出现大量碎岛时，可用 `merge_micro_islands` 合并相邻微岛并重排。
5. **需要复用规则或迁移 UV 时**：用 `uv export-policy` / `uv import-policy` 导出或重绑 `settings` 与 `recipe`；在同拓扑或近共面模型间迁移 UV，走 `uv transfer-source` → `uv transfer-prepare` → `uv run`（或 `uv transfer-execute`），按需选 `INDEXED`、`EXPLICIT` 或 `PROJECTED`。

## 第四步：棋盘复审、表面采样与冷重开

每次修改后同时核对数值报告、实际棋盘画面和独立重开回执，把硬检查、视觉审阅与用途确认分开记录。

1. **生成棋盘预览**：运行 `uv checker-preview --params $inspectParams --size 2048` 渲出目标候选的带字棋盘图，逐项查看近景主面、转角倒角、文字朝向和背面接缝，确认格块方正、密度均匀、无穿色。
2. **抽查求值与变形表面**：对带细分、镜像或绑定姿态的模型，在 `uv.inspect` 的 `manifest.surface` 指定 1–8 个代表帧和 `VIEWPORT`/`RENDER` 模式，落盘后可用 `uv read-surface-report` 核对同一磁盘快照的表面结论。
3. **确认采用与独立重开**：数值检查与棋盘都过关后，运行 `operation="adopt"` 切换编辑层，检查作业目录下的 `uv-report.json` 与 `uv-reopen.json` 均为通过。在 Blender 界面手工微调完，切回 Object Mode 另存新工作副本，再跑一次 `uv inspect` 或 `operation="validate"` 完成冷重开核对。长作业用 `uv job-progress <job_id>` 或 `job wait` 跟踪。

## 交给下游

把以下内容打包交接给材质、烘焙或资产入库环节：

- **可编辑主工程副本**：带最新 `UVW_*` 候选层、源 UV 层完好保留、Object Mode 存盘路径与小写 SHA256。
- **结构与验收摘要**：`uv-report.json` 与 `uv-reopen.json` 路径、目标图幅与边距、拉伸与密度实测值、棋盘预览图路径，以及已声明的复用组和 UV 层用途清单。
- **贴图与交换衔接**：需要迁移旧贴图或重烘法线时，按 [绘制、烘焙与交换](references/baking-transfer-and-exchange.md) 走公共 `texture bake`、`material projection-bake`、`uv grid-transfer` 或 `exchange export`，分别验收 UV 布局与材质外观。

## 例子：给一件硬表面仪器面板展 2K 独占 UV

接到建模部门交来的定稿白模 `work/panel/dial_panel.blend`（含主体 `PanelBody` 与旋钮 `DialKnob`，带 2 级细分修改器，用途为 2K 独占 PBR 涂装，正面标识须水平正立）。

1. **建批次与摸底**：在 `work/audit/<batch>/` 下算出源文件 SHA256，运行 `uv inspect` 并开启 `diagnostics` 与 `seam_suggestions`（60°）。确认无零面积与非流形边，无旧贴图消费者，SubD 的 `UV Smooth` 设为 `Keep Corners`。
2. **显式打缝与双候选展开**：跑 `uv.run` 的 `seams`（`MARK_BY_ANGLE` 60°，保留主体正面连续、把切口落在倒角背面），随后运行 `generate` 生成 `ANGLE_BASED` 与 `MINIMUM_STRETCH` 两个 2K 候选，设 `border_px: 8`、`margin_px: 16`。
3. **选优、定向与排布**：对比两份报告，`ANGLE_BASED` 岛形更方正（p95 拉伸 1.04，最大 1.28）。用 `edit orient` 把正面面板沿水平边摆正，给正面主岛加高 1.4 倍密度，再运行 `pack(rotate=false, scale=false)` 完成联合排布，实测岛距 16.4 px、图边 8.5 px、零重叠。
4. **棋盘与冷重开核验**：运行 `uv checker-preview` 渲出 2K 棋盘图确认正面文字方向正确、倒角无扭曲；对 `VIEWPORT`/`RENDER` 跑 `inspect` 的 `surface` 检查细分后无折叠；执行 `adopt` 后核对 `uv-reopen.json` 通过。
5. **交接下游**：把 `uv-candidate.blend`、SHA256、UV 层名 `UVW_dial_v1_angle_based`、棋盘图与报告交给材质环节制作面板涂装。

## 参考

- [CLI 命令、参数与现场接续](references/cli-and-workflow.md)
- [接缝规划、像素密度、排布与局部精修](references/seams-density-and-packing.md)
- [角色、生物、服装与透明发卡 UV 工艺](references/character-and-organic.md)
- [硬表面、载具、建筑环境与动态 UV 工艺](references/hard-surface-and-environment.md)
- [绘制、烘焙、迁移与格式交换](references/baking-transfer-and-exchange.md)
- [契约路径、Wiki 索引与历史依据](references/sources.md)
