# 用途与输入诊断

## 1. 用途矩阵

先从用户目标反推 UV 语义，而不是从当前 UV 形状猜意图。

| 用户目标 | 必须显式记录 | 实际入口 | 失败/边界 |
|---|---|---|---|
| 单图幅独占绘制 | 图幅 W/H、活动/渲染 UV、材质消费者、边距 | `EXCLUSIVE`；`generate` / `copy_uv` / `edit` / `recipe` | 不同布局单元的未声明正面积重叠是硬失败；合法声明复用需完整岛足迹 |
| 单图平铺/重复 | 真实世界尺度、重复方向、是否跨岛重复、材质是否 REPEAT | `settings.mode=TILED`；密度/方向/明确重复布局 | 不制作 UDIM；不改材质节点/extension；图边/岛间间距在用途检查中不适用 |
| 多 UV 层 | 每层用途、活动/渲染层、消费者、交换格式 | `inspect`、`copy_uv`、`transfer`、`lightmap` | 共享 Mesh、层名冲突、层数不足、既有/未解析 UDIM 来源拒绝；`lightmap` 仅在已有 `active_render` 主层前提下追加/更新非渲染 UV2 |
| 既有 UDIM | tile 列表、模板、图像 source=TILED、消费者 | 只读 `inspect`；保护后另做普通层候选 | 本期不制作 UDIM；不把平铺坐标范围当 UDIM |
| 同工程联合图集 | 对象清单、材质/贴图分组、自定组、是否固定岛 | 一个多对象 `uv.run` + 整岛 `pack` | 不自动合并对象/材质；不维护跨文件实时图集 |
| 绘制/烘焙接续 | 旧 shader 用的 UV、通道、目标图幅、旧/新材质关系 | 既有 `texture.bake` / `material.run` / `exchange.export` | UV 通过不替代外观；引擎/像素等价未证 |
| 同拓扑/条件迁移 | 源/目标身份、对应模式、是否完整双射/显式域 | `transfer` 的 `INDEXED` / `EXPLICIT` / `PROJECTED` | 任意异拓扑、薄层歧义、非完整覆盖明确拒绝 |

`settings` 的完整字段是 `version=1.0`、`binding`、`mode`、`reference`、`reuse_groups`、`density`、`directions`；它与数值配方 `recipe` 是两种记录。`settings` 描述布局意图，`recipe` 把数值 policy 绑定到精确几何/单位/图幅。二者都不能凭旧模型自动重绑。

**旧候选通过不等于新模型用途通过。** 旧验收只适用于当时的模型、用途、几何、单位、图幅和消费者。工具的 `recipe/settings.binding` 仅含几何、BASE_MESH、单位、W/H；`usage_binding`仅记录mode/reuse及适用的density，不绑定材质/shader/图像消费者。换几何/单位/图幅须重审并显式重绑；换用途或消费者也须重新 `inspect`并审阅，即使工具仍显示binding match。旧reference、旧pass和旧视觉批准不能复制成新用途资格。

## 2. 已确认数值标准的精确范围

| 名称 | 适用范围 | p95 | max | 密度 | 图边（2K） | 岛间（2K） |
|---|---|---|---|---|---|---|
| P0 受控基准 | 固定 328 tri 受控正反例 | ≤1.60 | ≤2.00 | 岛均 ±5% | ≥8 px | ≥16 px |
| 沙发 B | 该真实沙发、2K 静态绘制接续 | ≤1.10 | ≤1.80 | ≤5% | ≥8 px | ≥16 px |

这些数字不是通用阈值。尤其不要把沙发/ P0 数字套到角色、场景、生成模型、其他硬表面、平铺用途或最终求值表面。

新用途未获用户确认时，提交一份**具体提案**，而不是先跑完再宣称通过：

1. 用途、模型类别、目标图幅 W/H、UV 层与材质/下游格式；
2. 必须保留的人工 seam、pin、锁岛、方向、重点区域和不可动区域；
3. 代表视图/相机/帧/棋盘图，包含最差区域和隐藏面/背面；
4. 建议指标：p95/max 拉伸、密度相对偏差、图边 px、岛间 px、无效/退化/重叠定义；
5. 哪些指标不适用（如 TILED 图边/间距）以及未知项；
6. 由谁确认、确认的是模型+用途+图为一体，而不是一个孤立数字。

提案中的 `reference` 只是调用方声明，不是已经认证的用户批准；`purpose_checks` 的 `visual` 仍是 `not_reviewed`，除非另有明确人工签核记录。

## 3. 输入检查

先保存工作快照，再走只读检查。不要依赖 GUI 未保存编辑。

```powershell
& $blenderctl --blender $blender --jobs-dir $jobs uv inspect --params $inspectParams
```

至少记录：

- `scene`、`view_layer`、精确对象名；对象/网格 `users`；库链接、覆盖、共享 Mesh。
- 每个对象的 UV 层、活动层、`active_render`、pin、seam；材质槽和实际 UV 消费者。
- 图像 `source=TILED` 的 UDIM、tile 列表、外部资源绝对路径与 SHA；不扫描目录猜 tile。
- 世界变换、单位 `scale_length`、负缩放、修改器、形态键、骨骼/权重/动画。
- 基础网格三角数、零面积/退化三角、非流形边、孔洞/薄层；带对象/面/边索引的交接件。
- 现有候选、`adopt` 状态、旧 recipe/settings 绑定和旧视觉批准范围。

### 只读表面检查的 manifest

下面的字段与当前 `surface_contract` 一致。`layers` 必须精确覆盖对象；`frames` 为 1–8 个不同整数；`modes` 显式选择 `VIEWPORT`/`RENDER`；`triangle_limit` 为 1–2,000,000。示例没有用途 policy，数值/硬检查通过不代表生产用途批准。

```json
{
  "version": "1.0",
  "operation": "inspect",
  "scene": "Scene",
  "view_layer": "ViewLayer",
  "objects": ["Product"],
  "candidate": "uv_product_v1",
  "pair_budget": 2000000,
  "surface": {
    "layers": {"Product": "UVW_uv_product_v1_angle_based"},
    "frames": [1],
    "modes": ["VIEWPORT", "RENDER"],
    "triangle_limit": 200000,
    "usage": "EXCLUSIVE"
  }
}
```

外层 params 还需要真实 `file`、`expected_sha256`、`resources`；示例不是可执行请求。`surface.policy` 可选，但 `density_basis` 只支持 `ISLAND_AREA_REFERENCE`；求值网格不会自动继承基础岛的复用/重点密度对应。

### 基础网格诊断与建模交接（inspect-only）

> 说明（0.8.0）：若需要在 `generate` 前先按二面角、锐边或开放边界定位建议切缝边，可在只读 `uv.inspect` 的 `manifest` 中传入 `seam_suggestions`（`angle_degrees` 0..180 默认 60.0、`include_boundaries` 默认 `true`、`max_examples` 1..512 默认 32），返回只读建议边索引与世界坐标，不写网格、不隐式改 seam。

`manifest.diagnostics` 只用于 `operation=inspect`，字段严格为 `max_examples`（1–10000，默认 1000）。它读取全基础网格，不读取修改器最终表面，不修复：

```json
{
  "version": "1.0",
  "operation": "inspect",
  "scene": "Scene",
  "view_layer": "ViewLayer",
  "objects": ["Product"],
  "diagnostics": {"max_examples": 1000}
}
```

返回/交接要点：

- `status`：`fail` / `needs_modeling_review` / `no_blocker_found`；`mutation="none"`。
- 每对象全量 `counts`：vertices、edges、faces、triangles。
- `issues`：如 nonfinite_vertex、zero_length_edge、coincident_face_vertices、invalid_triangle、loose_edge、boundary_edge、nonmanifold_edge、loose_vertex、empty_surface；每类 `count` 全量，`examples` 受 `max_examples` 限制，`examples_complete` 明确指出是否截断。
- 定位示例含对象/面/边/顶点/loop 索引；`geometry` 是普通候选几何身份，`diagnostic_geometry_sha256` 保留诊断输入（含非有限值），两者不能互相替代。
- `handoff` 说明建模拥有修复；只有几何身份仍匹配时才能沿用面/边/顶点/loop 索引。修复后重新 `inspect` 并新建候选/约束。
- 限制：开边界/松元素只报告不自动拒绝；重合面只比较精确世界顶点集，不认证部分相交/近重合；不做事后拓扑、流形修复或求值修改器诊断。

面板“定位网格问题 / 建模交接”会把同一结果写入 Text block `UV-Geometry-Handoff.json`；它不修改网格、材质或 UV。

完整性快照对受表示的 modifier 设置/引用和实际引用 rig 的受支持状态做保护，不等于最终求值认证；普通 modifier 的配置保护通过仍需保存盘 `surface` 单独检查。shape 写路径可做也不等于所有 rig 控制类型、任意约束或任意驱动器结构都受支持；未表示/未认证结构拒绝。

### 解读边界

- `VIEWPORT` 使用实际视口求值图，隐藏目标拒绝。
- `RENDER` 由临时 capture engine 取得真实 RENDER depsgraph，报告 `configured_renderer_equivalence=not_verified`；不认证原 Cycles/Eevee 的着色器置换、自适应引擎细分、材质、像素或过滤。
- 帧是离散样本，不能证明整段动画；完成/异常路径会恢复帧、相机、引擎、分辨率等控制，核对 `controls_before/after`。
- 超过 `triangle_limit` 返回 `unknown/triangle_limit`；它是在求值后限制测量规模，不是求值前内存硬上限。
- 代表姿态/代表帧必须显式记录；未覆盖的姿态、连续动画和引擎最终效果保持 `not_run`/unknown。基础网格或旧候选通过不自动继承最终表面/姿态。

面板棋盘 `uvw.preview` 是当前 **VIEWPORT 求值图的 frozen snapshot**（含当前 rig/shape 状态），不是保存盘 `surface` 报告；后续编辑不自动刷新，不认证配置渲染器置换/自适应细分。`uvw.surface_report` 只读取与当前文件 SHA 匹配、样本完整且控制恢复的磁盘 `uv-report.json`，不会把未保存编辑当通过。

## 4. 保护与交接

默认只改明确目标 UV 层、接缝和允许区域。以下情况先停：

- 共享 Mesh、库链接/覆盖、目标对象不唯一；
- 共享 Mesh 或共享 shape-key datablock；local single-user shape keys 写入在生产自 0.7.0 起 已支持（safe scratch 只清临时 Key，源 shape/weights/target、引用 rig/action/attrs 受保护；最终能力见 `uv describe`）；
- 既有 UDIM 消费者或未解析绑定；
- 应有效三角退化/零面积、非流形等几何问题；
- 原生 pin/seam 与候选记录不一致且尚未 `validate`/`sync_pins`；
- 目标几何、单位、图幅、材质或活动 UV 在使用旧候选后发生变化。

几何诊断交建模时保留对象名、面/边/loop 索引、世界坐标和 `changes_made=none`；修复后重新取几何指纹和 SHA，不能沿用旧候选/旧批准。UV 专项不承担修几何、重拓扑或骨骼动画修改。
