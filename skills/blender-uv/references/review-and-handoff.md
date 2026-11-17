# 复审、人工接续与独立重开

## 1. 棋盘与布局复审

UV 专项的主要视觉证据是棋盘格和布局，不是最终材质。至少观察：

- 岛分布、接缝位置、明显拉伸/压缩、翻折、重叠、越界、图边与岛间空隙；
- 重点区域密度、方向、锁岛/固定点、平铺重复的跨岛连续性；
- 多对象联合图集的对象/材质关系和固定岛；
- 基础网格与最终求值表面的差异；代表姿态/帧要写明范围。

面板的 `UVW_OT_preview`（`uvw.preview`）会渲染当前候选的棋盘图到 Blender 临时目录，并尝试在图像编辑器打开。它取的是当前 **VIEWPORT 求值图**，并把当时的 rig/shape 状态复制成一个 **frozen snapshot** 再渲染；后续编辑不会自动更新这张图。它不是保存盘 `surface` 的最终表面报告，也不认证配置渲染器置换/自适应细分。背景/无法打开编辑器时以实际生成的文件为准：

```text
uvw.preview -> uvw-checker-<id>.png
```

记录图片实际路径、相机/视图、分辨率、帧、所用 UV 层、日期，以及它是 live VIEWPORT frozen 快照还是保存盘 `surface` 样本。不要只说“已渲染”；文件缺失、空白或视图不对都不算视觉证据。

为局部近景另建显示网格时，保留源顶点索引表，先核每个局部顶点等于对应源或同姿态求值顶点，并核面连接、绕序、角点UV和世界变换。完整坐标数组用源索引，预压缩数组才用局部索引；点面数量相等不能证明对应正确。先实际看一张正常预览，再扩展相机/姿态批次。显示副本出错只作废受影响图像，不自动否定原候选的独立数值结论，也不能把坏图记作UV算法无收益。Orange本机V2的398/408错点及V3逐点零差修复见 `runtime/audit/uv-two-residual-specialist-20261116-v001/integration/hand-physical-review-v2/` 与 `hand-physical-review-v3/`；不影响此前已核正确的显示工程。

局部修复的机位须实际覆盖原缺陷面和当前待改善区域，不能只按骨名、手部整体或点重心选图。先投影面角点，必要时用实际渲染的源face-ID/深度核可见性；投影在框内不证明未被遮挡。Orange旧峰值901/1803虽已降畸变，既有0.13m指近景将其重心裁在画外；补原0.08m根视并实际first-hit确认可见后，仍须独立判断材质收益，不能因数值已改或补了镜头就签视觉。证据见同批 `integration/hand-local-priority-audit/` 与 `integration/hand-root-closeup/FACE-VISIBILITY.json`。

视觉通过必须区分：

- **数值/硬检查通过**：metrics 完整且无违反；
- **棋盘观察通过**：在指定视图/帧/图幅下可接受；
- **用户用途批准**：用户对具体模型+用途+图幅+图的确认；
- **下游材质/引擎通过**：由材质/烘焙/交换流程单独验收。

新用途或新模型没有用户确认时，只能写“待确认”或 `not_reviewed`。P0/沙发数字不能替代这个确认。

旧候选、旧视觉接受和旧 recipe/settings 不自动继承新模型或新用途；换模型/用途/几何/单位/图幅后重新检查并显式重绑。

## 2. 面板与原生接续

推荐顺序：

1. 保存工作快照；在 Object Mode 选择明确对象。
2. 面板生成/复制候选（`0.8.0` 起生成与局部重展可选 `MINIMUM_STRETCH` + SLIM `iterations`/`no_flip`，亦可在生成前通过 `UVW_OT_suggest_seams` / `UVW_OT_seams` 按二面角或锐边显式标记接缝，或用 `UVW_OT_lightmap` 创建非 `active_render` 辅助 `UVMap_Lightmap` 层）；查看候选 ID、图幅、指标和状态。
3. 选择候选并 `adopt`（仅当硬检查/用途数值 pass 且指纹未变）。
4. 在 Blender 原生 UV 编辑器继续移动/旋转/缝合/改 seam；具体编辑归原生工具。
5. 回到 Object Mode；需要重验时先 `validate`，再记录当前选区；继续局部编辑或重新生成。
6. 若原生 pin 与记录不一致，先 `validate`，再用 `sync_pins` 显式导入所选范围；不要期待 `validate` 自动吸收。
7. 需要恢复原编辑层时 `restore`；若检测到未验证的原生 seam 改动会拒绝，先保留/记录并重验。
8. 另存新 `.blend`，在独立 Blender 进程冷读。

0.8.1新增控件的实际GUI接续已于2026-11-16在私有配置验证：菜单选SLIM、只读建议、角度/锐边标缝、生成、辅助UV2创建/同名拒绝/显式覆盖、Ctrl+S与冷读。受控立方体只证明控件行为，不作AAA质量样本；证据见`runtime/audit/uv-ui-acceptance-20261116-v001/REPORT.md`。本轮辅助层完整数值pass仍报告12个负向UV三角，不能把pass写成零镜像；方向/切线与目标光照烘焙按实际用途另验。该新方法记录未回写旧0.8.1冻结ZIP。

冷读核世界矩阵时，库追加的参考对象先链接到独立Scene并更新依赖图；未链接对象的`matrix_world`可能仍是未求值的identity。本例顶点/loops/法线/UV与matrix_basis均相同，只有未求值world矩阵造成假失败，建立正确求值上下文后精确通过；不要为消除这种测试错误去改工作模型。

### 基础网格诊断交接

面板“定位网格问题 / 建模交接”（`uvw.geometry_diagnostics`）是只读 `inspect`，默认 `diagnostics.max_examples=1000`，把结果写入 Text block `UV-Geometry-Handoff.json`。交接时保留：

- 每对象全量 vertices/edges/faces/triangles 计数；
- 问题类型、`count`、`severity`、有界 `examples` 和 `examples_complete`；
- 对象/面/边/点/loop 索引、`geometry` 与 `diagnostic_geometry_sha256`；
- `mutation="none"`、`handoff`、`limitations`。

示例可能截断，`counts` 仍为全量。该报告不修网格、不诊断修改器最终表面；建模修复后重新检查并新建候选/约束，不能沿用旧几何身份。

`adopt`/`restore`/`validate` 的最小 manifest 结构相同：`version`、`operation`、`scene`、`view_layer`、`objects`、`candidate`。例如：

```json
{
  "version": "1.0",
  "operation": "adopt",
  "scene": "Scene",
  "view_layer": "ViewLayer",
  "objects": ["Product"],
  "candidate": "uv_product_v1_angle_based"
}
```

实际外层 params 仍需 `file`、`expected_sha256`、`resources`。`adopt` 只切换编辑层/seam 计划；不自动把贴图切到新 UV，也不继承旧视觉批准。

### 最终表面报告与 `surface_ui`

最终表面后台检查用 `uv.inspect` 的 `manifest.surface`，显式列出保存盘 `frames`/`modes`。`RENDER` 是 capture-engine 求值网格，不等于原配置 Cycles/Eevee 的像素/置换/自适应细分。代表姿态/帧是离散样本；未测姿态和连续动画不能写成通过。

面板 `uvw.surface_report` 只读取不超过128MiB的磁盘 `uv-report.json`，并核对：

- 报告 source 与当前已打开文件 path 一致；
- 当前文件 SHA 与报告 source SHA 一致；
- `uv_report_version=1.0`、`status=inspected`、无保存、完整样本集合、controls restored；
- 0.8.7起，各样本`complete`须显式为JSON布尔值；缺键、数字、字符串、列表或对象均拒绝并清除旧成功缓存。合法`false`可表示未完成，不因此改签通过；这项类型门不等于完整schema或报告防伪认证。
- 汇总状态与样本一致。
- 用途一致；`CANDIDATE_EXACT`通过样本具有明确候选、完整有限精确身份和相等的base/evaluated SHA；顶层与每对象的 `first_mismatch` 均须显式存在且为null。0.8.5起缺键报告拒绝并清除先前成功显示，不能把缺证据当“没有差异”。

它只显示历史快照；读取成功不等于表面通过，fail/unknown如实显示。当前dirty工作区、未保存编辑、后续编辑不会自动刷新；保存改变文件SHA后须重新inspect，独立重开后须重新加载报告。直接调用operator的execute不证明按钮点击或文件选择器路径已经实测。视觉和引擎效果另审。

报告展示与batch复用分别验收：前者核报告与当前磁盘快照及完整对应证明，后者另核数值预算、对象顺序、reuse_groups和资源/产物闭包。0.8.5缺键修补不把界面读取当batch资格或完整生产批准；本机复现/修复与打包接续见 `runtime/audit/uv-report-integrity-20261116-v001/`。

## 3. 公共 CLI 的保存与重开

写操作走 `uv run`：

```powershell
& $blenderctl --blender $blender --jobs-dir $jobs uv run --params $paramsFile
```

典型产物在作业目录：

```text
request.json
status.json
result.json
uv-report.json
uv-reopen.json
uv-candidate.blend
```

验收顺序：

1. 进程退出码与 `ok`；
2. `uv-report.json` 的 `status`、`metrics`、`purpose_checks`、`protection`、`support`；
3. `verification` / `uv-reopen.json` 的 `status=passed`、候选 SHA、源 SHA、非目标保护；
4. 候选文件独立打开，核对候选层/记录和实际 UV；
5. 只有以上满足，才讨论视觉/用途批准。

`ok=true` 只表示请求完成；`verification` 失败或 `uv-reopen.json` 缺失时不能把候选当通过。批量报告里的 `hard_pass_needs_review` 也只表示至少一个候选数值硬检查通过，仍需视觉/用途审阅。

### 复制/检查作业的性能定位

真实工程较慢时，先区分UV计算、非目标全场景保护、文件保存和冷读子进程，不能仅按目标三角数估时。保留超时终态及未通过质量结果；延长等待是有界诊断，不是性能修复。优化保护读取须保持完整字段/数值/JSON语义，验证旧新完整指纹一致、非有限仍拒绝、非目标修改仍能检出；不跨操作复用快照或减少检查换速度。本机AAA复制的批读修订及实际公开入口对照见Wiki `procedures/blender-uv-batch-recovery-and-qualification.md`，证据 `runtime/audit/uv-performance-20261115-v001/`；单例耗时不成为所有输入保证。源码包不包含Python/Blender，使用已有匹配运行时，并从实际 `uv describe` 核对新实现身份，不能用旧ZIP的相同版本号替代字节身份。

## 4. GUI 手工保存的冷读

如果通过面板采用并手工编辑：

- 另存到新文件（例如 `<asset>_uv_work_v001.blend`），不覆盖源工程；
- 关闭该 Blender 进程，或至少用另一个独立进程打开；
- 检查场景/视图层、对象、候选 `UVW_*` 层、`uv_workflow_state_v1` 记录、原 UV/材质/render 绑定和 seam；
- 对保存后的新文件重新跑只读 `inspect`，必要时再用 `uv run` 的 `operation=validate` 生成新作业副本；
- 记录文件 SHA、Blender 版本/构建和实际打开路径。

独立重开不是“在同一进程点一下打开”。同一进程的未保存状态、临时选择、撤销栈和活动视图都不算。

## 5. 批量、取消与恢复

`uv batch` 适合多对象/多文件/有序步骤，但不是无界队列：

- 最多 32 步，当前单 worker；
- 每步显式 `depends_on` 和 `bindings`；接续候选用 `/candidate/file`、SHA；
- `failure=continue` 保留成功项，失败/`unknown` 逐项隔离；`fail_fast` 按策略停止；
- 只复用输入、实现、运行时、产物全部未变的成功项；失败项重新执行；
- 源/资源 SHA 变化、产物被手改或后续人工修改会使旧缓存失效；保留手改文件，另开子作业；
- `--async` 后用 `job status/result/wait`；`--compact` 保留完整报告链接；
- 取消只作用于本批自有进程树；`cancel_requested` 不是取消完成，需观察终态；
- 恢复不承诺从原求解中途续算，保存中取消/断电/任意求解点未验。

0.8.4的求值表面batch资格支持`EXCLUSIVE`和显式`CANDIDATE_EXACT`，均要求请求的全部样本完整pass，并核对对象/层、模式、三角数、预算和controls恢复。`CANDIDATE_EXACT`还必须逐样本提供`reuse_used=true`、同一候选、与请求一致的有序对象、`finite_numeric_values_no_tolerance`及逐对象相等有效的base/evaluated SHA、match=true/first_mismatch=null；reuse_groups须非空、组ID/对象岛成员合法且不重复，并在样本间一致。usage标签、基础候选pass或缺失证明不能获得复用资格；unknown继续隔离。此资格不继承视觉、密度配置或用途批准。

面板后台作业监控（`job_ui`）只读用户显式选择的公共 UV 作业 `status.json`，只接受 `uv.run`/`uv.inspect`；批量请用 CLI `job wait/status`。使用 persistent timer，切换当前 `.blend` 后仍可继续显示 job id、state、源文件、阶段、阶段耗时和心跳。它是**只读状态显示**：作业状态/进度不是 UV 质量，也不代表当前工作区通过；`unwatch` 只停止查看，作业继续。不要按进程名或创建时间猜作业/进程所有权。

0.7.3起“停止查看”位于动态进度信息之前，状态变化时操作位置保持稳定，并在清除监视后请求3D视图刷新。验收后台继续时，须先实际执行运行中的停止查看，再用同一job ID核对之后仍在运行及最终结果；只看到面板清除或自然终态都不够。可用只读事件记录及时采集状态，不能为便于截图改状态、延迟后台或增加无关输入规模。具体本机证据见`runtime/audit/uv-job-monitor-20261114-v002/REPORT.md`；操作符直接接入不冒充文件选择器路径已验。

## 6. 证据清单

一次可交接的 UV 结果至少保留：

- 输入 `.blend` 绝对路径、源 SHA、Blender 版本/构建、场景/视图层/对象；
- 请求 params/manifest、候选 ID、方法/图幅、约束和 recipe/settings；
- 作业 `uv-report.json`、`uv-reopen.json`、候选文件 SHA；
- `diagnostics` 交接报告（若有）：全量计数、有界示例、`examples_complete`、两个几何身份、`mutation=none`；
- 最终表面 `surface` 报告：帧/模式、是否代表姿态、RENDER capture-engine 边界、`controls_restored`；
- 关键指标（p95/max、密度、图边、岛间、无效/重叠、岛数）和不适用项；
- 棋盘/布局图路径、相机/帧/分辨率/UV 层；
- 视觉审阅范围与签核人；下游材质/烘焙/交换结果及各自状态；
- `pass/fail/unknown/not_run/not_applicable` 分开，不用一个“完成”覆盖。

## 7. 交接失败项

失败/`unknown` 不是垃圾数据。保留：

- 失败候选和报告；
- 失败阶段（求解/检查/重开/材质/交换）；
- 可定位对象/面/边/岛/预算/绑定；
- 已尝试方法和次数；
- 哪些成功项已保留、哪些未动；
- 下一最小动作（换方法、补图幅、人工接缝、修几何、重新烘焙）。

只有通过项进入可继续列表；不要把失败兄弟候选隐式选中。
