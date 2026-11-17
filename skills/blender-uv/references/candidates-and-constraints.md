# 候选、约束与修正

## 1. 生成候选

### 外部三角展开与原四边形回写

使用三角后端时同时检查实际三角逐角对应、同一原loop的多三角UV别名。前者exact仍可能无法表示成原quad；别名冲突须拒绝回写，不能平均或静默加对角线。若用户选择静态三角工作副本，保留原quad，另建与实际目标三角表面一致的新身份并重新验收；角点法线重编码、编辑与变形边界单独披露。

后端实际图幅可能与请求不同，映射回目标图时保实际像素比例。无旧贴图的新UV允许反射**整个一致负向chart**，但必须先证明没有混合折回，并重新排布和全量检查；不能逐三角改方向凑通过。A5生成角色已证实xatlas原loop别名冲突，派生三角对照也仍有自交和断纹；没有将xatlas集成或宣布自动生产通过。详细规则与证据统一见Wiki `procedures/uv-nonplanar-quad-triangulation-and-local-rechart.md`。

### 游戏渲染拆点与静态编辑表示

原游戏render mesh的索引分量数不等于某通道UV chart数。当前核心须共享顶点索引边且两端UV exact，不跨render-index裂缝识别连接。静态目的可保raw并另建明确新identity的编辑工作对象，在无歧义反向二面边上验证位置/decoded normal exact后关联角点，逐corner保全部三角、两套原UV和来源映射；不冒称raw索引不变、原DCC拓扑已恢复或支持完整rig。不能把不同UV通道的连续性互换，也不能通用按距离weld。

同岛内部slit即使不改变岛数，也可造成真实相交；若新UV用途允许简化，要明确是新选缝并核全部受影响aliases、numeric cuts与未选保护，不把原本不同值的收口说成恢复。原负绕向只作诊断，原作微相交不豁免新EXCLUSIVE候选。RE3的7474v静态编辑表示、12loops/四内部缝修正及原区域预算保持已实作；条件步骤与边界见Wiki `procedures/uv-render-vertex-splits-and-static-editing-representation.md`，不把单例升级为通用自动化。

生成导出也可能有渲染拆点，边界数本身不等于破洞。G3小车4880边界全部精确成对，并核反向二面/单顶点闭环fan后才建立新静态身份；G4的28真开口未采用。不同来源角点normal须保CORNER属性与原fan边界，不平均成新点normal；重新编码后比较实际解析法线，来源数组exact不等于着色normal exact。G3独立最大重编码角差约0.02747°仅属该例，原raw/全部有序三角仍保留，非通用weld或生产批准。

本轮同一完整三角输入的原生路线失败后，已有可选xatlas只作为有界外部候选；逐三角/原loop映射、实际图幅比例和全chart朝向核对后，经公共copy_uv→density→pack及独立重开接回。最终66岛/69.02%净覆盖是本例读数，不能把后端utilization或padding当目标图测量。未集成为插件后端；几何/数值/棋盘/新用途批准分开。证据：`F:/Blender AI/runtime/audit/uv-generated-positive-20261115-v001/REPORT.md`及上述Wiki，冻结0.7.5入口不继承后续源码的新方法支持。

`generate` 的候选基名是短 ASCII `candidate`（`[A-Za-z][A-Za-z0-9_-]{0,23}`）；每个方法生成一个记录和层：

- 记录/候选键：`<candidate>_<method 小写>`
- UV 层：`UVW_<candidate>_<method 小写>`
- `copy_uv` / `transfer`：通常为 `UVW_<candidate>`

一次给 1–3 个唯一方法。以下字段与当前 host-safe contract 一致；外层 params 仍需真实 `file`、`expected_sha256`、`resources`。示例中的边索引/面索引只是占位整数，必须换成真实索引。

`width`/`height` 为正整数且最大 16384，`pair_budget` 最大 10,000,000；`margin_px`/`border_px` 非负，且 `2*border_px` 必须小于较短图幅，否则请求在求解前拒绝。

### 自动接缝候选

```json
{
  "version": "1.0",
  "operation": "generate",
  "scene": "Scene",
  "view_layer": "ViewLayer",
  "objects": ["Product"],
  "candidate": "uv_product_v1",
  "methods": ["SMART_ABF", "ANGLE_BASED"],
  "width": 2048,
  "height": 2048,
  "margin_px": 16.0,
  "border_px": 8.0,
  "pair_budget": 2000000,
  "constraints": {
    "Product": {
      "must_cut": [12, 13],
      "must_not_cut": [20],
      "source_uv": "UVMap"
    }
  }
}
```

`SMART_ABF` 可用自动接缝并接受 `must_cut`/`must_not_cut`，但不能带固定点。自动接缝仍是候选；必须与人工/角度展开候选比较。

### 固定点/锁面候选

```json
{
  "version": "1.0",
  "operation": "generate",
  "scene": "Scene",
  "view_layer": "ViewLayer",
  "objects": ["Product"],
  "candidate": "uv_product_fixed",
  "methods": ["ANGLE_BASED"],
  "width": 2048,
  "height": 2048,
  "constraints": {
    "Product": {
      "pins": [0, 2],
      "locked_faces": [7],
      "source_uv": "UVMap"
    }
  }
}
```

固定点/锁面必须有明确的 `source_uv`（或对象已有活动 UV）；索引分别为 loop 和 face 索引。`SMART` 不能承诺接缝/固定约束；`SMART_ABF` 不能带固定点。不要在 `SMART_ABF` 请求里塞 `pins` 再期待自动忽略。

### 方法选择

角色先走[角色制作方法](character-production.md)的消费者/图集/语义接缝流程。下表不是角色自动通过的选项。2026-11-13生产0.7.1的 `ANGLE_BASED/CONFORMAL` 已取消55°自动加缝：源seam/边界及显式约束继续生效。公共折面7项方法结果和独立重开见 `F:/Blender AI/runtime/audit/uv-plan-audit-20261113-v001/PUBLIC-SEAM-ACCEPTANCE.json`。自动路线仍可能增加投影切缝；实际缝集仍须检查。本证据没有验收角色质量，旧0.7.0包亦未更新。

| 方法 | 真实行为 | 选择建议 |
|---|---|---|
| `SMART` | 原生智能投影；无接缝/固定约束保证 | 只用于无硬约束的快速起点/对照 |
| `SMART_ABF` | 智能投影后把岛边界作为 seam，再角度展开；可加 must_cut/must_not_cut | 自动接缝候选；与人工方案比较 |
| `ANGLE_BASED` | 在源seam/边界及显式约束上角度展开；0.7.1不再按角度加缝 | 只有实际缝集与制作计划一致后才用于角色；方法名不构成保证 |
| `CONFORMAL` | 共形展开 | 对照；仍需完整检查 |
| `MINIMUM_STRETCH` | 在源seam/边界及显式约束上执行原生 SLIM 最小拉伸展开（可选 `slim_iterations` 1..100 默认 10、`slim_no_flip` 默认 true）；不在 `generate` 内隐式加缝 | 有机曲面或局部高精度低拉伸对照；仍须检查实际切缝与多方向伸缩 |

候选比较至少看：岛数、岛边界/接缝位置、p95/max 拉伸、密度分布、图边/岛间间距、无效/重叠、方向、可编辑性和人工修改成本。不要只选 p95 最小的候选。

生产自 0.7.0 起 已支持 **local single-user shape keys 写入**：safe scratch 只清临时 Mesh Key，源 shape/weights/target、实际引用 rig/action/attrs 受完整性保护；共享 Mesh 或共享 shape-key datablock 仍拒绝。不要删 Key/减面绕过。普通能力资格最终以 `uv describe` 为准。

完整性快照只证明受表示的 modifier 设置/引用未被普通写路径破坏，不等于最终求值认证；最终表面另用 `surface` 检查。shape 写入支持不等于所有 rig 控制类型、任意约束或任意驱动器结构都受支持；未表示/未认证结构明确拒绝。

## 2. 复制、迁移、规则与配方

- `copy_uv`：把每个对象的当前/指定 UV 复制到新候选，不运行展开；保留源层、pin、活动/渲染层和材质消费者。`source_layers` 必须精确覆盖 `objects`。既有/未解析 UDIM 来源拒绝。
- `transfer`：从显式源对象/源 UV 迁移到目标新候选；`objects` 只列目标，源/目标必须在同一场景/视图层且不相交。`INDEXED` 要求完整同索引拓扑；`EXPLICIT` 要求完整唯一 `corner_map` 与绕序；`PROJECTED` 只支持显式面域、近共面单层和完整裁剪覆盖。源/目标绑定 hash 变化即拒绝，不能偷偷重采样。
- `settings`：记录 `mode`、`reference`、`reuse_groups`、`density`、`directions`，不移动 UV；`EXCLUSIVE` 与 `TILED` 语义不同。声明复用组要求每个成员是完整岛且 UV 面足迹相同；一个岛只能属于一组。
- `recipe`：把 `policy` 与 `binding` 绑定到现有候选；`binding` 精确覆盖对象几何、`BASE_MESH`、单位、W/H。换模型/单位/图幅必须重新审阅并显式重绑；旧 `usage_binding` 不匹配会 `CONFLICT`/`unknown`。该usage指mode/reuse及适用的density；这两种binding均不包含材质/shader/图像消费者，消费者变化需另行inspect和审阅，不会仅凭此绑定自动失效。
- `seams`：`MARK/CLEAR` 改候选或基础网格 seam 计划；`MARK_BY_ANGLE`（按二面角与可选边界标记，可加 `clear_existing`、`sync_sharp`；仅 `MARK_BY_ANGLE` + `sync_sharp=true` 放行 `sharp_edge` 同步变更）与 `MARK_FROM_SHARP`（按锐边写入 `uv_seam`）均须显式调用（可在 `generate` 前无 `candidate` 作用于基础网格，或作用于已有候选）；`REQUIRE_CUT/REQUIRE_JOIN` 改硬约束；`FREE` 解除硬约束但保留计划。它们不会自动切分/焊接 UV；暴露待修布局时保存 `fail`，不能 adopt。
- `lightmap`（0.8.0）：创建或显式 `overwrite=true` 更新非渲染辅助 UV2（默认 `layer="UVMap_Lightmap"`、`width`/`height` 64..8192 默认 1024、`box_div` 1..48 默认 12、`margin_div` 0..0.5 默认 0.1）；要求对象已存在主/`active_render` UV 层并保持原 `active_render`、seam、pin 与非目标 UV 层，同时核验 0 重叠与 `[0, 1]` 边界。

旧候选/旧recipe/旧视觉接受不自动继承新模型或修复后几何。几何/单位/图幅变化须重新inspect、重审和显式重绑；用途/材质消费者变化也须inspect、重审并保留新的消费关系证据，不能把同一binding重新提交当成消费者已验证。

## 3. 局部编辑

`edit` 只修改已有候选并增加 revision；公共入口仍另存新作业文件。`selection` 按对象给出 `domain` 与精确 `indices`：

- `ISLANDS`：索引是原网格**面种子**，扩展为完整数值 UV 岛；不是排序后的岛号。
- `FACES`：精确面索引。
- `LOOPS`：精确角点（loop）索引。

可选 `selection_binding` 绑定 candidate、geometry、uv_hash；过期会拒绝。原生修改后先 `validate` 再重新捕获。

例：对两个面做保边界局部放松。

```json
{
  "version": "1.0",
  "operation": "edit",
  "scene": "Scene",
  "view_layer": "ViewLayer",
  "objects": ["Product"],
  "candidate": "uv_product_v1_angle_based",
  "selection": {
    "Product": {"domain": "FACES", "indices": [12, 13]}
  },
  "action": {"kind": "relax", "iterations": 20}
}
```

动作字段（必须与 `kind` 精确匹配）：

| kind | 必需/可选字段 | 选区与边界 |
|---|---|---|
| `translate` | `delta_px=[x,y]` | 像素位移；未选保持 |
| `rotate` | `angle_degrees`，可选 `pivot_px` | 像素空间逆时针；默认包围盒中心 |
| `scale` | `factors=[sx,sy]`（均 >0），可选 `pivot_px` | 镜像必须显式用 `mirror` |
| `mirror` | `axis=U/V`，可选 `pivot_px` | 用途/重叠仍独立检查 |
| `align` | `axis=U/V`，可选 `value_px` | 省略取选区均值 |
| `straighten` | 无 | 一条开放、不分叉的 UV 边链；端点保持 |
| `density` | `target_px_m` | 仅完整 `ISLANDS` |
| `pin` / `lock` | `enabled` | pin 可用 `LOOPS`；lock 仅面/岛 |
| `relax` | `iterations` 整数 1–1000 | 仅 `FACES`/`ISLANDS`，保边界 |
| `unwrap` | `method=ANGLE_BASED/CONFORMAL/MINIMUM_STRETCH`（选 `MINIMUM_STRETCH` 时可选 `iterations` 1..100 默认 10、`no_flip` 默认 true） | 仅 `FACES`/`ISLANDS`，固定边界 |
| `stitch` | `pairs`、`limit_px`、`seam_mode=KEEP/CLEAR_JOINED` | 仅 `LOOPS` 移动侧；配对须同 mesh 顶点 |
| `pack` | `rotate`、`scale` 布尔，`pin_method=LOCKED` | 仅 `ISLANDS`，全部对象联合 |
| `sync_pins` | 无额外字段 | 显式导入所选范围原生 pin；不改 UV/原生旗标 |
| `split` | `delta_px` 非零 | 仅 `FACES`；平移并切开连续选区边界；不等于零距离拓扑切分 |
| `orient` | `edge_loops=[start,end]`、`angle_degrees` | 一次一个完整岛 |
| `stack` | `reference={object,face}`、`pairs`、`mirrored`、`group_id` | 完整岛显式双射；同对象/跨对象 |
| `unstack` | `offset_px` 非零 | 完整岛按对象/最小面索引顺序分离并更新组 |

硬约束冲突、未选数据改变、候选身份变化、切分后仍连续、pin/lock 被移动等都会拒绝并回滚；普通质量失败可保存候选继续修，但不能 adopt。

`unwrap/relax` 的“局部”是保边界重解，**不能根据新增seam释放边界或改变numeric cuts**。岛边界上的退化若必须移动边界才能修复，先明确需要的是不同操作，不反复增加seam或迭代数。当前可用明确授权的原生编辑在新候选层进行，再`validate`及核非目标exact；这不代表已有公共rechart动作。D05两面折角的有界实证及边界见[硬表面制作](hard-surface-production.md#折角被平面投影压成线时分离真实转折再重展)。

投影在负曲率边界扇也可能折叠：先核问题点的角点别名、完整chart拓扑与实际扇角，不把正面积相交叫浮点细缝。“保切缝/面集”和“固定UV轮廓”不同；固定轮廓可能保留故障。G3释放四完整chart轮廓的CONFORMAL也仍有3对重叠，故停止；释放边界不是无翻转保证，不能因P95改善或少修一对就采用。

## 4. 状态和失败语义

| 状态 | 含义 | 下一步 |
|---|---|---|
| `pass` / `needs_review` | 硬检查和已绑定用途数值通过，视觉未审 | 棋盘/人工审阅；不自动批准 |
| `fail` | 硬检查或用途检查实际违反 | 保留诊断候选；定位并修正；不 adopt |
| `unknown` | 预算不足、测量缺失、缺层、未知修改器、绑定失效等 | 补证据/改路线；不要写成通过 |
| `UNSUPPORTED` / `CONFLICT` | 明确不支持或身份变化 | 按错误定位；不删除约束/源数据绕过 |

关键规则：

- `ok=true` 或 `candidate_edited` 只表示操作完成，不表示质量通过。
- `adopt` 要求 `metrics.status=pass`、候选 UV 指纹未变且无 UDIM 消费者冲突；采用只切换编辑层与 seam 计划，不自动批准外观。
- `restore` 在当前候选采用状态下工作；若检测到原生 seam 改动与记录不一致会拒绝，先 `validate` 记录/保留再恢复。
- 已有候选的 `constraints` 若显式提供，必须与创建时规范化值一致；不能用 `validate`/普通请求改写固定点。变更用受管的 `pin`/`lock`/`sync_pins` 或新建候选。
- `validate` 重新测量并更新检查/UV 指纹，但不会自动吸收原生 pin 意图；用 `sync_pins` 明确导入。
- `unknown` 和失败候选可保留，但不进入可复用成功项。有限尝试：保留通过项、隔离失败项，只重试应重试项；同类失败两次就换方法/路线。

## 5. 批量和恢复

`uv batch` 的顶层是 `{"manifest": {...}, "reuse_job": "可选旧 job id"}`；`manifest` 为 `uv_batch_version="1.0"`、`policy`、`steps`。`steps` 最多 32 项；`command` 仅 `uv.run`/`uv.inspect`；每项有 `id`、`params`、`depends_on`、`bindings`、`limits`、`timeout_seconds`、`reuse`。当前 `max_workers` 固定 1。

后续步骤接续前一步候选时，必须显式声明 `depends_on` 与 `/candidate/file`、SHA 到 `/file`、`/expected_sha256` 的绑定；不要依赖隐藏状态。`uv batch-resume` 只接原 job id 并沿用原 manifest；输入/配方/预算/对象变化时用新的 batch + `reuse_job`。成功项只有在输入、实现、运行时和产物全部未变时才复用。

## 6. 容易犯的错

- 用 `SMART` 带 `must_cut`/固定点，或 `SMART_ABF` 带固定点。
- 把生成候选键 `uv_product_v1_angle_based` 误写成层名/基名；层是 `UVW_` 前缀。
- 在已有候选上用普通请求改 `constraints`，期待静默覆盖；应新建候选或用受管 pin/lock/sync_pins。
- 用 `validate` 后直接改 pin，不 `sync_pins`；锁面/固定点会冲突。
- 把 `split` 当零距离拓扑切分；当前要求非零 `delta_px` 且实际新增 UV 切口。
- 在 TILED 用途下要求图边/岛间间距通过；这两项在该用途检查中不适用。
- 看到 `ok=true` 就 adopt；还要看 `metrics.status`、`purpose_checks`、`uv-reopen`。

## 2026-11-16局部新缝接续实证

已定位边界扇折叠、旧自由轮廓求解仍失败时，可先按部位/完整chart规划真实少量内部切边，再仅重展问题chart、保其他chart原形，接公共copy/pack/seams/validate与冷读。P02四新缝＋局部717面已通过有限静态棋盘；全域同缝重展158对fail和原SMART4/ABF161保持，不称通用自动语义修复。141岛仅draft坐标exact，pack后重定位；新149岛/89微岛与旧xatlas66岛/17微岛不混比。详细条件与证据回读Wiki `procedures/uv-auxiliary-numeric-gates-and-solver-selection.md`，单位/定向图案/mip/生产边界照旧保留。
