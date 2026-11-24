# CLI 命令、参数与现场接续

本参考汇总 `blenderctl.ps1 uv` 全部公共子命令、请求结构、局部编辑动作与面板现场接续步骤。实时命令签名与支持清单随时以 `uv describe` 和各子命令 `--help` 为准。

## 公共子命令速查

全局参数（如 `--jobs-dir`、`--compact`、`--human`）放在 `uv` 子命令前面。

| 子命令 | 用途 | 关键参数 |
|---|---|---|
| `uv describe` | 只读查询当前插件契约、支持操作与实现身份 | 无（无需启动 Blender） |
| `uv inspect` | 只读检查对象、UV 层、消费者、几何诊断、建议缝与最终表面 | `--params <json>` |
| `uv run` | 在工作副本执行单步 UV 写操作并独立重开验证 | `--params <json>` |
| `uv batch` | 串行编排最多 32 步 `uv.run` / `uv.inspect`，按依赖自动传递产物 | `--params <json>` |
| `uv batch-resume` | 沿用原 manifest 续跑中断的批量作业 | `--params <json>` |
| `uv grid-transfer` | 逐岛整数纹素搬移切线法线 PNG，零重采样且保持源工程不变 | `--params <json>` |
| `uv capture-selection` | 从 Edit Mode 存盘选区生成可复放的 `uv.run` 编辑参数 | `--params <json> [--snapshot <blend>] [--output <json>]` |
| `uv capture-constraints` | 从 Object Mode 选边/选面生成带约束的 `generate` 参数 | `--params <json> --object <名> --kind must_cut\|must_not_cut\|locked_faces\|clear --output <json>` |
| `uv checker-preview` | 渲染指定候选的带字棋盘图并验证工作副本 | `--params <json> [--size 64..2048]` |
| `uv read-surface-report` | 读取与当前快照 SHA 一致的 `uv-report.json` 表面结论 | `--params <json>` |
| `uv job-progress` | 单次查询已有 `uv.run` / `uv.inspect` 作业状态与阶段 | `<32位小写十六进制 job_id>` |
| `uv export-policy` | 导出候选绑定的布局规则 `settings` 或数值配方 `recipe` | `--params <json> --kind settings\|recipe --output <json>` |
| `uv import-policy` | 把审阅过的规则 JSON 以新候选形式应用到目标工程 | `--params <json> --kind settings\|recipe --policy <json> --expected-policy-sha256 <sha>` |
| `uv transfer-source` | 绑定源对象与源活动 UV 层，输出 `source_record` | `--params <json> [--output <json>]` |
| `uv transfer-prepare` | 组装目标对象与 `INDEXED`/`PROJECTED` 迁移参数 | `--params <json> [--output <json>]` |
| `uv transfer-execute` | 执行工程内已保存的迁移草稿并输出验证后的新候选 | `--params <json>` |
| `uv transfer-export` | 导出工程内的原生迁移草稿 JSON | `--params <json> --output <json>` |
| `uv transfer-import` | 将原生迁移草稿写入新工作副本（只记录草稿、独立验证） | `--params <json> --output <blend>` |

## 外层请求与核心操作

`uv inspect` 和 `uv run` 的外层 UTF-8 JSON 统一包含四个必填键：`file`（绝对 `.blend` 路径）、`expected_sha256`（源工程小写 SHA256）、`resources`（外部资源 `{file, expected_sha256}` 数组，无外部依赖时传 `[]`）与 `manifest`（业务载荷，可选 `implementation_sha256`）。未知字段会被直接拒收，写请求前先用 `uv describe` 核对。

### 只读检查 `inspect`

在 `manifest` 里设置 `"version": "1.0"`、`"operation": "inspect"`、`"scene"`、`"view_layer"`、`"objects"`，按需开启以下只读扩展：

- **几何诊断与建模交接**：加入 `"diagnostics": {"max_examples": 1000}`（1–10000），返回全量点/边/面/三角计数，以及零面积三角、非流形边、重合面、松散元素的定位索引。界面上点「定位网格问题 / 建模交接」会把同一结果写入 Text block `UV-Geometry-Handoff.json`。
- **只读建议缝**：加入 `"seam_suggestions": {"angle_degrees": 60.0, "include_boundaries": true, "max_examples": 32}`，返回建议切缝边与世界坐标，源网格保持原样。
- **求值与姿态表面采样**：加入 `surface` 段，显式声明 `layers`（对象到 UV 层映射）、`frames`（1–8 个离散整数帧）、`modes`（`VIEWPORT` / `RENDER`）、`triangle_limit`（1–2,000,000）与 `usage`（`EXCLUSIVE` 或 `CANDIDATE_EXACT`）。`CANDIDATE_EXACT` 用于已声明完整复用组的受管候选，逐样本核对有限精确拓扑与岛归属。

### `uv.run` 写操作清单

所有写操作把结果写入新作业目录（通常产出 `uv-candidate.blend`、`uv-report.json`、`uv-reopen.json`），源文件与已声明资源全程只读保护：

1. **`generate`**：一次传入 1–3 个唯一 `methods`（`SMART`、`SMART_ABF`、`SMART_REPAIR`、`ANGLE_BASED`、`CONFORMAL`、`MINIMUM_STRETCH`）。候选基名 `candidate` 为短 ASCII 字符串，自动生成 `<candidate>_<method>` 记录与 `UVW_<candidate>_<method>` 层。支持 `width`/`height`（最大 16384）、`margin_px`/`border_px`（满足 `2*border_px < min(width, height)`）、`pair_budget`（最大 10,000,000）以及 `constraints`（`must_cut`、`must_not_cut`、`pins`、`locked_faces`、`source_uv`）。选 `MINIMUM_STRETCH` 时可传 `slim_iterations`（1–100，默认 10）与 `slim_no_flip`（默认 `true`）。
2. **`seams`**：按显式边索引或几何规则更新接缝计划。模式包括 `MARK`、`CLEAR`、`REQUIRE_CUT`、`REQUIRE_JOIN`、`FREE`、`MARK_BY_ANGLE`（支持 `angle_degrees`、`include_boundaries`、`clear_existing` 及显式开关 `sync_sharp`）与 `MARK_FROM_SHARP`。其中 `MARK_BY_ANGLE` 与 `MARK_FROM_SHARP` 既可在生成前直接作用于基础网格，也可作用于已有候选。
3. **`lightmap`**：为已有 `active_render` 主层的对象创建或显式 `overwrite: true` 更新非渲染光照层（默认 `layer: "UVMap_Lightmap"`、`width`/`height` 64–8192 默认 1024、`box_div` 1–48 默认 12、`margin_div` 0–0.5 默认 0.1），自动核验零重叠与 `[0, 1]` 范围，保持原渲染层与接缝完好。
4. **`copy_uv`**：按 `source_layers` 把已有 UV 层原样复制为新候选，保护原层、pin 与 `active_render` 绑定。
5. **`settings`**：记录布局用途（`EXCLUSIVE` 或 `TILED`）、`reuse_groups`（完整岛复用声明）、逐岛 `density` 与有向边 `directions`，用于后续检查与排布约束，自身保持 UV 坐标不变。
6. **`recipe`**：把数值阈值 `policy`（含 `density_basis`: `ISLAND_AREA_REFERENCE` 或 `CONFIGURED_TARGETS`、拉伸、密度偏差与边距限值）显式绑定到当前几何、单位与图幅。换模型、单位或图幅后重新审阅并显式重绑。
7. **`edit`**：在已有候选上执行受管局部修改并递增版本号（详见下表）。
8. **`validate` / `adopt` / `restore`**：原生手改 UV 或接缝后先跑 `validate` 刷新测量与指纹；硬检查与用途数值通过后用 `adopt` 切换编辑层与接缝计划；需要退回原编辑层时运行 `restore`。

## `edit` 局部编辑动作表

`selection` 按对象指定 `domain` 与精确索引：`ISLANDS` 传面种子（按数值连续性扩展为完整岛，避免用排序岛号）、`FACES` 传面索引、`LOOPS` 传角点索引。带 `selection_binding` 时会核对候选与 UV 指纹。

| `action.kind` | 核心参数 | 适用选区与要点 |
|---|---|---|
| `translate` | `delta_px: [x, y]` | 像素空间平移，未选区域保持原位 |
| `rotate` | `angle_degrees`, 可选 `pivot_px` | 像素空间逆时针旋转，默认绕选区中心 |
| `scale` | `factors: [sx, sy]`（均大于 0）, 可选 `pivot_px` | 缩放选区；需要镜像时改用 `mirror` |
| `mirror` | `axis: "U"\|"V"`, 可选 `pivot_px` | 显式翻转并独立重检重叠与手性 |
| `align` | `axis: "U"\|"V"`, 可选 `value_px` | 省略坐标值时对齐到选区均值 |
| `straighten` | 无 | 拉直单条开放、无分叉的 UV 边链，端点固定 |
| `density` | `target_px_m` | 仅完整 `ISLANDS`，按真实世界面积缩放岛密度 |
| `pin` / `lock` | `enabled: bool` | `pin` 支持 `LOOPS`；`lock` 面向面与完整岛 |
| `relax` | `iterations`（1–1000） | `FACES`/`ISLANDS`，保外边界松弛内部拉伸 |
| `unwrap` | `method`（`ANGLE_BASED`/`CONFORMAL`/`MINIMUM_STRETCH`），SLIM 可选 `iterations`、`no_flip` | `FACES`/`ISLANDS`，固定外边界局部重展 |
| `stitch` | `pairs`、`limit_px`、`seam_mode`（`KEEP`/`CLEAR_JOINED`） | `LOOPS` 移动侧，配对角点须同源网格顶点 |
| `pack` | `rotate`、`scale` 布尔、`pin_method: "LOCKED"` | 完整 `ISLANDS` 跨对象联合排布；含复用组时整组同选 |
| `sync_pins` | 无 | 在 `validate` 后显式导入所选范围的原生 pin |
| `split` | 非零 `delta_px` | 仅 `FACES`，平移选区、切开连续边界并标缝 |
| `orient` | `edge_loops: [start, end]`、`angle_degrees` | 每次定向一个完整岛，使有向边对准目标角度 |
| `stack` | `reference: {object, face}`、`pairs`、`mirrored`、`group_id` | 完整岛显式角点双射堆叠并登记复用组 |
| `unstack` | 非零 `offset_px` | 按对象与最小面索引顺序分离堆叠岛并更新复用组 |
| `merge_micro_islands` | 无 | 面向 2K 静态独占三角单对象未采用候选，合并相邻微岛并重排 |

## 现场接续、批量作业与冷重开

- **面板与原生编辑往返**：在 Edit Mode 选中面、边或角点后，切回 Object Mode 再存盘（例如从 Texture Paint 退出到 Object Mode 并另存工作副本），防止撤销栈遗漏受管状态。随后用 `uv capture-selection` 或 `uv capture-constraints` 导出参数文件交给 `uv run`。
- **棋盘快照与磁盘报告**：面板 `uvw.preview` 生成的是当前视口求值状态的静态棋盘截图（含当前绑定姿态），改完模型后重新触发预览；正式求值结论以保存盘的 `uv inspect`（带 `surface`）为准，再通过 `uv read-surface-report` 或面板 `uvw.surface_report`（上限 128 MiB，核对文件 SHA、`controls_restored: true` 与完整布尔 `complete` 标记）查阅。
- **批量与中断续跑**：`uv batch` 顶层传 `manifest`（`uv_batch_version: "1.0"`、`policy`、`steps`，最多 32 步、单 worker）与可选 `reuse_job`。后续步骤用 `depends_on` 与 `/candidate/file`、SHA 显式接续前一步输出。遇失败或 `unknown` 时逐项隔离保留诊断，修好输入后用 `uv batch-resume` 续跑未完步骤。
- **作业监控与交付核验**：长作业用 `uv job-progress <job_id>` 或 `job wait` 查看阶段与心跳；面板 `job_ui` 可跨文件跟踪单步 `uv.run`/`uv.inspect` 状态。每次交付同时核对退出码、`ok`、`uv-report.json` 的 `metrics.status` 与 `purpose_checks`、以及 `uv-reopen.json` 的独立冷重开通过状态。
