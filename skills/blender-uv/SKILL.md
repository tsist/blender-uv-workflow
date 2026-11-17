---
name: blender-uv
description: 制作与检查 Blender UV；遇到未知资产领域或关键机制，先学习并验证适用方法，再制作候选。覆盖用途、材质消费者、接缝、密度、排布、约束、棋盘与姿态复审、保存重开和下游交接；角色、硬表面、场景和生成模型按实际证据与工具支持范围执行。
---

# Blender UV 工作流

以**可编辑、可复查、边界明确的 UV 候选**为交付，而不是以命令跑完或 `ok=true` 为交付。原始工程保持只读；制作写入新候选层和新作业文件；数值通过、棋盘观察和用户用途批准分别记录。

这是一个主入口：先判断用途、输入和风险，再选择最小可行路线。不要从命令清单开始，也不要在每一步重复申请已经覆盖的权限。

插件 GUI/核心可独立安装在 Blender 中，只依赖 Blender 自带的 `bpy`/`bmesh`/`mathutils`/`numpy`；它不要求先安装 blenderctl。需要 `uv describe/run/inspect/batch`、独立重开验证或 AI 公共入口时，另用匹配的完整 blenderctl 与 addon 源码，不能把 CLI 当成 GUI 的运行时前提，也不能只带 UV 的 16 个 CLI 身份文件冒充完整 CLI；其中包括 `uv_saved_protection.py`，其余生产模块、共享 addon 与运行时 Schema 仍须完整提供。

2026-11-17当前工作区UV源码为**0.8.7 / CLI0.88.0**，实现身份从实际入口 `uv describe` 取得。0.8.7要求GUI磁盘报告每个样本的`complete`为显式布尔值，非法类型拒绝并清除旧成功缓存；合法`False`仍按未完成/失败状态显示。运行与隔离包界面证据见 `runtime/audit/uv-software-closeout-20261117-v001/`。0.8.6的限定`SMART_REPAIR`边界扇修复与平移精度修正、0.8.5的`first_mismatch`缺键拒绝、0.8.4批量资格及旧保护合同保持；旧冻结包不改。源码、ZIP与启用模块分别核对；未全局安装或公开发布。数值通过不代签用途或完整生产质量。

## 0. 每次制作前先判断是否准备充分

**遇到未知领域，或已知领域中影响 UV 的未知机制，必须先学习；不得未做准备就开始生产 UV 制作。** 不因为工具能运行、读过文章、已有别的模型通过或自动指标合格而跳过。关键消费者、布局约束或判定依据未知时，停止受影响的生成、重排、替换和采用；允许只读诊断，以及有明确问题、保留原数据的隔离学习实验。

每次任务先从已有证据回答三个问题：当前表面/材质怎样消费 UV？哪些接缝、比例、位置和方向可以改变？准备采用的路线凭什么适用于本输入、怎样发现失败？若已有有效方法覆盖，只引用其适用条件并检查本任务差异，直接推进；不要求每次全面重研或填写大型表格。用户急于开工也不把未知写成已知，可先完成不依赖该未知的部分。

同一已批准用途和仍有效的证据不重复索取批准；新产物完成本次操作合同要求的检查即可，已有独立重开回执可满足重开要求，不另加同义冷读。只有输入、消费者、实现、用途变化或具体反例触发时，才补受影响的研究、复验或必要的新用途确认。

发现缺口时按[学习与制作准备](references/learning-and-readiness.md)执行：查现有 Wiki 原文与技能参考 → 补对应领域的原始资料和代表案例 → 用最小实验解决影响路线的未知 → 形成有条件的方法 → 在当前任务验证。资料、原案例观察、机制验证、制作验证和用途批准分别记录，**学习就绪只允许开始候选制作，不授予质量通过**。

主要游戏资产按[领域学习路径](references/asset-domains.md)逐项推进；它是研究路线，不是已支持能力清单。研究 Trim、UDIM、lightmap 等不解除本期制作边界。详细知识与案例进入本地 Wiki；技能 references 保留可执行方法、关键证据与限制，双向关联；发现反例时同时纠正规则及引用入口。学习过程见[真实研究案例](references/research-cases.md)，未验证领域明确留待研究。

开发改进必须落到一个真实工作问题：案例依据 → 预期操作和可观察失败 → 当前公共入口 → 必要代码改动 → 同输入复验 → 可编辑交付。已有操作能完成就先组合使用；隔离修复要接回实际入口验证，不能只更新研究报告。具体做法见[案例驱动开发](references/case-driven-development.md)。

## 1. 先选用途，再定验收

用途决定布局语义、检查项和能否采用。至少先分清：

| 用途 | 显式语义 | 主要入口 | 不能据此宣称 |
|---|---|---|---|
| 独占单图幅 | `EXCLUSIVE`；不同布局单元不得意外重叠 | `generate` / `copy_uv` / `settings` / `recipe` | 任意模型通用质量、最终外观 |
| 平铺单图 | `TILED`；允许跨岛重复和图幅外重复，同岛折叠仍失败 | `settings` 的 `mode=TILED` | UDIM 制作、材质 REPEAT 自动生效 |
| 多 UV / 既有 UDIM | 保护非目标层与消费者；UDIM 只识别和保护 | `inspect`、`copy_uv` 的层选择 | UDIM 布局制作、跨块岛修复 |
| 同工程联合图集 | 一个工程内多对象共享图集；不自动合并对象/材质 | 一个 `uv.run` 请求中包含多对象，`pack` 为整岛 | 跨文件实时共享图集 |
| 交换 / 绘制 / 烘焙 | UV 完成后的下游协作；UV 与外观分别验收 | 既有 `exchange.export`、`texture.bake`、`material.run` | 所有外部引擎等价、像素无损 |

不要在 `EXCLUSIVE` 与 `TILED` 之间凭坐标范围猜测；不要因为 UV 超出 0–1 就判为 UDIM 或错误。要求用户在用途或下游格式不明确时确认，而不是替用户发明意图。

### 数值标准

已有用户确认的标准只在其精确范围和模型上有效：

- P0 受控基准（固定 328 tri）：`stretch p95 ≤ 1.60`、`stretch max ≤ 2.00`、岛平均密度偏差 `±5%`、2K 图边 `≥8 px`、岛间 `≥16 px`。这是受控基准，不是所有硬表面阈值。
- 沙发 B（本模型 2K 静态绘制接续）：`p95 ≤ 1.10`、`max ≤ 1.80`、密度偏差 `≤5%`、图边 `≥8 px`、岛间 `≥16 px`。只绑定该模型和该用途。

新用途、新模型类别或未确认的标准不得套用上述数字。先给出具体检查图和拟议指标，再请用户确认；确认前只能报告“数值/视觉未获批准”，不能把候选写成生产通过。详细模板见[用途与输入诊断](references/purpose-and-diagnosis.md)。

旧验收仅对当时的**模型、用途、几何、单位、图幅和材质消费者**有效，这是制作结论的适用范围，不是全部由工具自动验证的绑定。当前 `recipe/settings.binding` 只含几何、`BASE_MESH`、单位和W/H；`usage_binding`记录mode/reuse及适用的density，不含材质、shader或图像消费者。换模型/几何/单位/图幅须显式重绑；换用途或消费者即使仍显示binding match，也须重新 `inspect`、人工审阅并独立检查，不能凭旧reference或旧pass继承批准。

硬失败至少包括：非有限 UV、应有效区域退化、独占语义下未声明正面积重叠、硬约束违反、非目标数据被破坏。检查预算不足、缺测量、未知修改器或未完成采样是 `unknown`，不是通过；合法平铺、声明复用和浮点邻接误差也不能混为一类。

带Mirror/Subsurf的输入须区分设计笼和实际涂装表面。基础UV通过后，镜像仍可能复制采样，细分插值仍可能折回；不以改一个UV Smooth选项消去负向计数代签拉伸/重叠改善。若用途允许固定最终形体，可保设计源并另建实际求值涂装网格，再以新身份展开与验收；明确其帧、密度和程序化编辑损失，不称旧笼/游戏LOD已修复。条件流程见[硬表面道具方法](references/hard-surface-production.md#镜像细分与最终涂装网格)。

## 2. 输入诊断

验证行业制作能力时，先选来源可追溯、具有真实生产拓扑和原UV/材质对照的样本；当前用户要求以可靠AAA游戏原包解包资产为主要实证。退化、破损或拓扑差的生成网格可作输入拒绝与鲁棒性反例，不用反复修坏网格代替UV制作验收。运行时三角化、法线/UV分裂点和多LOD本身不等于坏拓扑；按实际目标LOD/材质表面核对，保护原UV，不能先焊点改网格再冒称原版。原始数据及参考入口见[角色证据索引](references/character-evidence.md)。

默认输入是**已保存磁盘快照**，不是 GUI 未保存状态。先运行当前合同发现和只读检查：

```powershell
$blenderctl = 'F:\Blender AI\blenderctl.ps1'   # 使用实际完整 CLI 入口
$blender = 'F:\Blender AI\runtime\blender\releases\5.2.1\blender-5.2.1-windows-x64\blender.exe'
$jobs = 'F:\Blender AI\runtime\audit\<本任务>\jobs'

& $blenderctl --blender $blender --jobs-dir $jobs uv describe
& $blenderctl --blender $blender --jobs-dir $jobs uv inspect --params $inspectParams
```

实际入口、版本、字段和实现身份以 `uv describe` 与当前 Schema 为准；不要凭旧文档假设字段存在。

诊断至少覆盖：

- 目标场景、视图层、对象名、网格 `users`、库链接/覆盖、共享 Mesh、负缩放和世界单位。
- 现有 UV 层、活动/渲染层、材质消费者、pin、seam，以及既有 UDIM/动态图块；不能只数 UV 层数量。
- 形态键、骨骼、权重和修改器；基础网格与最终求值表面分别报告。
- 零面积/退化三角、非流形边、缺面、孔洞和薄层。几何修复不是 UV 工作；带精确对象/面/边定位交接给建模，修复后重新取身份再检查。
- 几何/UV 指纹、源 SHA、资源 SHA 和目标候选身份；几何、单位或图幅变化须重新核对绑定；材质/消费者变化须人工将旧用途验收视为待重审，工具不会仅因材质变化自动使候选失效。

`generate` 在发现应有效三角退化时会要求先修几何；不要减面或放宽检查来绕过。生产自 0.7.0 起 已支持 **local single-user shape keys 写入**：safe scratch 只清理临时 Mesh Key，源 shape/weights/target、实际引用的 rig/action 与 attrs 受完整性保护；共享 Mesh 或共享 shape-key datablock 仍拒绝，不能删 Key 或换无 Key 副本绕过。普通能力资格最终以 `uv describe` 为准。详见[候选、约束与修正](references/candidates-and-constraints.md)。

完整性快照对“受表示的 modifier 设置与引用”的保护通过，不等于最终求值认证；普通/受支持 modifier 的最终结果仍由保存盘 `surface` 的显式帧/模式检查，未表示的形变结构、未认证 modifier 明确拒绝。可做 shape 写入不等于所有 rig 控制类型、任意约束或任意驱动器结构都受支持；未表示/未认证结构拒绝。

需要建模交接时，`inspect` 可加 **inspect-only** 的 `diagnostics`：`{"max_examples": 1000}`（1–10000，默认 1000）。它只读基础网格，返回全量 vertices/edges/faces/triangles 计数、按对象/面/边/点/loop 的有界定位示例、普通 geometry 身份、诊断几何 SHA、`status` 和 handoff 文本；`counts` 是全量，`examples` 可能截断，`mutation="none"`，不做修复或最终求值表面诊断。面板“定位网格问题 / 建模交接”会把结果写入 Text block `UV-Geometry-Handoff.json`。修复后重新诊断并新建候选/约束绑定。

## 3. 有限候选与接缝

角色/有机体先读[角色制作方法](references/character-production.md)，来源与适用边界见[角色证据索引](references/character-evidence.md)。先建面域→材质→实际贴图/UV通道/变换的消费表，再定图集、重点密度和3D接缝。材质数、贴图集合数、UV层数与岛数不能互相替代；不同材质共用atlas时须联合检查。已有贴图的岛位置/方向必须保护，不能独立重排后仍声称保留外观。

角色以实际游戏拓扑为拆分输入；高模作烘焙源，不能拿雕刻/生成高模的自动碎岛总结行业规范。手、脸和衣物按可见性、变形、图案连续性及纹理用途提出语义接缝；不默认智能投影，不设“每手N岛/脸占固定百分比/全身统一密度”的通用门槛。

`generate` 一次接受 1–3 个唯一方法，产生替代候选；它不会自动替你选用。每个候选都保留报告，失败/`unknown` 兄弟候选不能被隐式选中。

| 方法 | 适合 | 关键限制 |
|---|---|---|
| `SMART` | 无固定点、无接缝硬约束的快速投影候选 | 有 `must_cut`、`must_not_cut` 或固定点时拒绝 |
| `SMART_ABF` | 自动接缝候选，再做角度优化 | 不能同时带固定点；自动接缝仍是候选，不是地面真值 |
| `SMART_REPAIR` | 对SMART投影逐完整chart精检，仅将支持的边界扇折叠局部重切/重展 | 仅三角面；拒绝固定UV、锁面和硬cut/join约束；只修可由chart桥边分离的开放扇。未知结构或检查不完整明确拒绝，不保证减少微岛 |
| `ANGLE_BASED` | 人工接缝/边界已明确，需要可控展开 | 0.7.1 已去掉角度自动加缝；仍检查实际切缝与硬约束 |
| `CONFORMAL` | 需要共形展开的对照候选 | 仍需独立检查；不保证比角度展开更适合该用途 |
| `MINIMUM_STRETCH` | SLIM 最小拉伸展开，适合有机曲面/低拉伸对照（0.8.0 新增） | 同样不在 `generate` 隐式加缝；支持 `slim_iterations`（1–100，默认 10）与 `slim_no_flip`（默认 `true`）；须独立核对拉伸与真实切缝 |

0.7.1 起源码已修复、`0.8.0`（对应 CLI `0.88.0` / 插件 `0.8.0`，详见 `uv describe`）保持一致纪律：`ANGLE_BASED` / `CONFORMAL` / `MINIMUM_STRETCH` 均不按 55° 隐式加缝，只保留源 `uv_seam`/边界并应用显式切开/保持连接约束。`SMART` / `SMART_ABF` 仍是自动路线，后者会使用投影边界；它们没有角色语义理解。技术通道可用不等于角色案例获批；仍检查实际切缝，不能绕过共享数据/形态键保护。使用前先用 `uv describe` 核对实际已安装版本与实现身份。

重点预算须区分生成和后续编辑：`generate` 目前没有逐区域目标入口，无固定点时先均匀化再排布；`settings` 只改检查规则，**不会移动UV**。已有候选可显式执行整岛 `edit density`，再用 `pack(scale=false)` 保持绝对密度，并选 `CONFIGURED_TARGETS` 检查完整覆盖。操作后实测；装不下要报告，不暗改目标或阈值。角色的岛内重点渐变并非逐岛缩放能力，按实际需求另研究。

重排前声明是**保持绝对密度、重新分配区域预算，还是保持区域比例填图**。最后一种可用 `pack(scale=true)`，但必须报告实际统一缩放系数、各区域最终密度及事前预算上下限，不能称绝对密度保持；后写维护目标不构成独立质量证明。先明确头/正脸、身体/躯干等面集，分别记录净UV覆盖、包围盒和边距；固定图幅与岛面积时移动/旋转不提高净覆盖。请求默认W/H与候选记录的有效W/H分开核对，所有像素指标以实际消费者和有效尺寸计算。具体口径、容量取舍与同内容清晰度对照见[角色制作方法](references/character-production.md#预算重排与清晰度验收)。

当净覆盖偏低或大量细碎岛占据整排时，先按[排布效率诊断](references/packing-efficiency.md)拆查实际像素间距、碎岛开销、岛形状和预算。把无硬错误的自动候选当诊断起点，继续解决影响当前用途的空间浪费与细节寻址；少岛、高覆盖与清晰度分别验，不用一个百分比代签。

推荐做法：

- 对无语义要求的产品/投影对照，可用 `SMART_ABF`；角色先做有理由的接缝计划，再用已核实际行为的展开入口形成少量可区分候选，必要时加共形对照。
- 比较岛数、接缝位置、拉伸、密度、图边/间距、重叠和可编辑性，不只看一个最小指标。
- 自动接缝失败时保留诊断候选，定位在哪些边/岛；不要反复无界重跑。同类失败两次就换方法或改为人工接缝。
- 人工必须在 3D 模型上能标记/清除 seam；生成候选的 seam 计划与实际 mesh seam 分开记录。`seams` 的 `MARK/CLEAR` 与 `REQUIRE_CUT/REQUIRE_JOIN/FREE` 语义不同。
- `0.8.0` 显式加缝与辅助 UV2：
  - **只读推荐**：`uv.inspect` 支持 `manifest.seam_suggestions`（`angle_degrees` 0..180 默认 60.0、`include_boundaries` 默认 `true`、`max_examples` 1..512 默认 32），按二面角/锐边/开放边界返回建议边及世界坐标定位，绝不修改网格；
  - **显式加缝**：`uv.run` `operation="seams"` 支持 `MARK_BY_ANGLE`（可传 `angle_degrees`、`include_boundaries`、`clear_existing` 与 opt-in `sync_sharp`，且仅当 `operation=="seams"` + `mode=="MARK_BY_ANGLE"` + `sync_sharp==true` 时才显式放行 `sharp_edge` 变更）与 `MARK_FROM_SHARP`，既可先于 `generate` 写入基础网格 `uv_seam`，也可作用于已有候选；
  - **辅助 Lightmap UV2**：`uv.run` `operation="lightmap"` 基于原生 `lightmap_pack` 生成或显式 `overwrite=true` 更新 `active_render=false` 附属层（默认 `layer="UVMap_Lightmap"`、`width`/`height` 64..8192 默认 1024、`box_div` 1..48 默认 12、`margin_div` 为`>0..0.5`默认0.1），要求已有主/`active_render`层。0.8.1候选修复为完整`metrics.status=pass`后才ready，fail/unknown拒绝并回滚；原0.8.0不能仅凭ready认定硬门通过。原层/渲染绑定和非目标数据保留；被显式覆盖的目标UV/pin会更新。非`active_render`层也可能被普通材质显式采样，`overwrite=true`前核对消费者。辅助层数值通过不认证目标引擎烘焙与mip。

同输入优选以测量和实际棋盘决定，不按求解器名称选新结果。本轮影心7930tri沿同边界的SLIM（10迭代）为净64.01%/p95 1.420/max3.956，弱于既有ANGLE_BASED的68.77%/1.194/2.539，因此保留原优选；该反例不否定SLIM在其他输入的用途。详细证据见本轮报告与Wiki `procedures/uv-auxiliary-numeric-gates-and-solver-selection.md`。

候选、接缝和局部编辑的精确字段见[候选、约束与修正](references/candidates-and-constraints.md)。

## 4. 自检、修正与人工接续

每次生成、编辑或原生手改后，读完整报告，不只看退出码：

- `metrics.status`：`pass` / `fail` / `unknown`；硬检查、用途检查和视觉检查分开。
- `quality_acceptance`：通常是 `requires_visual_and_purpose_review` 或 `not_automatically_approved`，不是批准。
- `verification` / `uv-reopen.json`：独立进程重开是否通过；源文件、非目标数据和候选 SHA 是否保持。
- `purpose_checks`：绑定是否匹配、密度 basis、逐项实际值/限值；绑定失效为 `unknown`。
- `surface`（若请求）：显式帧/模式的采样；`RENDER` 是 capture-engine 求值网格，不认证原 Cycles/Eevee 置换、自适应细分、着色器或像素等价。

修正规则：

- 原生改 UV、pin 或 seam 后先 `validate`；需要把原生 pin 纳入管理时用显式 `sync_pins`，不要假装 `validate` 自动吸收全部意图。
- `edit` 的选区是精确面/角点或面种子扩展的完整岛；不要用排序后的岛编号当种子。过期 `selection_binding` 会拒绝。
- 固定点、锁面、硬接缝、UDIM 消费者或几何变化导致的冲突要明确报告并保留原数据；不静默解除 pin、删 seam 或改共享 Mesh。
- 普通质量 `fail` 可保留候选继续修，但不能 `adopt`；`unknown` 也不能当通过。`adopt` 还会核对候选 UV 指纹，未重新 `validate` 的原生改动会被拒绝。
- 采用后用 Blender 原生编辑器继续；具体编辑归原生界面。恢复前若检测到未验证的原生 seam 改动会拒绝，先保留/记录再 `validate`。

面板和棋盘：

- 在 Edit Mode 只做选择捕获；实际生成/复制/采用/局部编辑/接缝执行回到 Object Mode，避免撤销只恢复网格而漏掉候选记录、约束和检查状态。
- 面板棋盘预览（`uvw.preview`）是**当前 VIEWPORT 求值图的 frozen snapshot**，包含当前 live rig/shape 状态；它不会因后续编辑自动刷新，也不是保存盘最终表面报告，不认证配置渲染器置换/自适应细分。用 `surface` 的显式保存盘帧/模式做最终表面检查；代表姿态/帧是离散样本，不等于连续动画或所有姿态。
- `uvw.surface_report` 只读与当前已打开文件 SHA 匹配、包含完整样本且 `controls_restored=true` 的磁盘 `uv-report.json`，上限128MiB；`CANDIDATE_EXACT`的通过样本还须包含候选及完整有限精确身份。读取成功不等于数值通过，fail/unknown如实显示。它只是历史快照，当前 dirty 工作区未保存编辑不算通过；保存后重新检查，独立重开后重新加载报告。
- 用面板棋盘或自建棋盘材质观察实际布局；记录相机、视图、分辨率、帧、所用 UV 层，以及它是 live VIEWPORT frozen 快照还是保存盘 `surface` 报告。
- 数值通过不等于棋盘可接受；棋盘可接受也不等于真实材质或引擎效果通过。新用途的视觉接受必须由用户确认。
- 具体接续步骤见[复审、人工接续与重开](references/review-and-handoff.md)。

## 5. 保存与独立重开

原生Texture Paint等非Object Mode保存的文件，接到CLI前须先切回Object Mode并另存工作副本；插件不会自动退出模式替你刷新原生编辑。0.7.2会在拒绝消息中给出目标和实际模式。若保存文件引用Blender自带画笔资产库，该库也是文件依赖，应按真实路径/SHA声明；贴图已packed不证明所有依赖闭合。本机实际笔刷、冷重开和此接续边界见 `runtime/audit/uv-development-20261113-m5-v003/REPORT.md`。

公共 CLI 的写操作只写新作业文件（通常 `uv-candidate.blend`），源文件有禁写保护；完成后另进程 `uv_verifier.py` 重开并比较候选字节、状态、目标和保护指纹。必须读 `uv-reopen.json` 或报告里的 `verification.status`，不能只信 `ok=true`。

GUI 手工采用/编辑后，另存为**新文件**，再在独立 Blender 进程冷读；不要覆盖源工程。独立重开要核对：

- 场景、视图层、对象、候选层名、候选记录和 UV 坐标；
- 原 UV/活动渲染层、材质消费者、pin、seam 和非目标对象；
- 源 SHA 与候选 SHA，必要时资源 SHA；
- 基础网格与最终求值表面是否分别记录，未测的不要写成通过。

批量只在完整通过项上复用；失败/`unknown` 逐项隔离。0.8.4允许完整 `EXCLUSIVE` 或显式 `CANDIDATE_EXACT` 求值报告进入资格核对；后者必须逐样本具备有序目标、候选、相等的base/evaluated有限精确身份、非空且跨样本一致的合法reuse_groups，以及原数值/预算/恢复证明，不能只凭usage标签通过。`uv batch` 最多32项、当前单worker；跨文件不维护实时联合图集。详见[复审、人工接续与重开](references/review-and-handoff.md)。

基础网格/旧候选通过不等于最终表面或代表姿态通过。最终表面用保存盘 `surface` 检查并单独记录帧/模式；代表姿态要写明实际样本范围和未测姿态。

面板后台作业监控（`job_ui`）只读显式选择的 `status.json`，只接受 `uv.run`/`uv.inspect`；批量作业请用 CLI `job wait/status`。它用 persistent timer 跨文件继续显示 job id、state、源文件、阶段、耗时和心跳；**状态/进度不是 UV 质量，也不代表当前工作区通过**。`unwatch` 只停止查看，后台作业继续。

## 6. 绘制、烘焙与交换

UV 完成不等于外观完成。需要贴图外观时，使用现有完整 blenderctl 的材质/烘焙/交换入口，不在 UV 插件里复制第二套烘焙器。

- 先明确旧 shader 的UV消费者。未连接Vector的Image Texture、Texture Coordinate的UV输出等会隐式读取 `active_render`，切换它会改变旧图取样；显式指定层名的UV Map不随它切换。无法确认时保留旧渲染层。需要迁移则先明确绑定/转换并对照，不能只改 `active_render`。
- 新 UV 保留旧层，新材质另建并保留旧材质/依赖；旧贴图迁移需要显式映射、通道拆分和实际字节/渲染对照。
- `NORMAL` 单独烘焙，记录目标 UV、TBN、实际法线格式和已烘入强度。当前已验烘焙路线输出 OpenGL +Y；这不是所有下游的规定。目标需要 DirectX -Y 或其他切线约定时，由材质/交换流程明确转换并验证；不要把法线图当普通彩色图复制。
- 允许多UV时可保原法线采样与基底；单UV重烘若有严重翻向，先核烘焙视向与闭包normal，仅在专用副本研究，并按全共同域方向/实际画面验收。有条件原生修补仍未通过严格保真，见[主法线迁移条件](references/exchange-and-delivery.md#单uv极端翻向的有条件原生修补)。
- 交换不因“导出成功”就通过：GLB/FBX/OBJ 的 UV 层数、名称、active/render、角点坐标和材质支持分别核对。
- UV 侧与材质/引擎侧分别签核；下游未执行时写 `not_run`，不能据 UV 通过宣称外观保真。

格式与烘焙边界见[绘制、烘焙与交换](references/exchange-and-delivery.md)。

## 7. 硬边界与停止条件

遇到以下情况，明确报告“当前未支持/未验证”，不要静默绕过：

- **共享 Mesh、共享 shape-key datablock、linked/override 目标仍拒绝**；local single-user shape keys 写入是生产自 0.7.0 起 已接入能力，safe scratch 只清临时 Mesh Key。不要删除 Key、减面或改无 Key 副本冒充原资产通过。最终能力资格以 `uv describe` 为准。
- UDIM 制作、Trim Sheet 制作、几何修复/重拓扑、共享 Mesh 直接修改（`0.8.0` 起支持显式 `lightmap` UV2 辅助层创建/更新，不替代下游多消费者绑定验证或目标引擎烘焙验收）。
- 任意异拓扑迁移；`PROJECTED` 只支持显式域、近共面单层、完整裁剪覆盖，不按最近点猜。
- 改变拓扑的求值复用/重点密度对应尚未迁移。0.8.3起显式`CANDIDATE_EXACT`只在完整候选绑定及每次实际eval几何/有序拓扑/UV/岛归属逐值一致时沿用其EXCLUSIVE复用，变化为unknown；不继承密度或批准。0.8.4的batch资格核对支持这类完整证明，未放行改变拓扑的对应。active Bevel不符合时保源另建明确最终静态身份，不能在surface内隐式应用栈。
- 实时 GUI 多帧表面采样未支持；先保存明确工作快照再走 CLI。
- `diagnostics` 是基础网格只读定位，不修复、不保证示例完整；面板棋盘 frozen VIEWPORT 不是最终表面报告，也不认证渲染器等价。
- 零距离拓扑切分、任意单边自动割缝、所有外部绘制器/引擎等价。真实能力资格最终见 `uv describe`，本文不把旧清单当永久接口。

当输入、用途或授权不足以继续时，保留已有成功项、失败候选和诊断，给出下一步最小可执行动作；不要用放宽阈值、删除约束或覆盖源文件来“完成”。

## 8. 按需参考

| 当前问题 | 读取 |
|---|---|
| 新领域、未知消费者/机制、既有方法被反例质疑、判断是否可开始制作 | [学习与制作准备](references/learning-and-readiness.md) |
| 游戏资产分领域研究顺序、代表样本选择、具体待学问题 | [领域学习路径](references/asset-domains.md) |
| 把案例教训转成具体开发、复用旧证据、集成隔离修复 | [案例驱动开发](references/case-driven-development.md) |
| 学会从原案例提炼条件规则、纠正错误归纳 | [真实研究案例](references/research-cases.md) |
| 角色全身拆分、材质/图集/多通道、像素比例与方向、部位技巧及验收 | [角色制作方法](references/character-production.md) |
| 角色规范依据、AAA原样本、工作室规则与通用要求的区别 | [角色证据索引](references/character-evidence.md) |
| 四足皮肤/耳/爪/尾接缝、既有图案、毛发坐标与方向职责 | [四足制作方法](references/quadruped-production.md) |
| 服装纹样方向、裁片/UV缝、原预算保持和方向锁定排布 | [服装制作方法](references/garment-production.md) |
| 道具/武器的标记方向、硬边/UV缝/法线、原图与新涂装用途、完整组件 | [硬表面道具方法](references/hard-surface-production.md) |
| 载具重复构件/独特涂装、UV与车身坐标参照、可动零件的采样稳定 | [载具与机械方法](references/vehicle-production.md) |
| 模块拼接相位、固定trim/独立光照域、独特环境资产与旧共享图集保护 | [建筑与环境方法](references/environment-and-modular-production.md) |
| 岩石/地形的独占与世界投影、树干方向/枝叉、叶atlas与风动覆盖 | [自然表面方法](references/natural-surface-production.md) |
| 序列图换格、UV滚动速度/方向、透明动态图像和错误重排反例 | [动态表面方法](references/animated-surface-production.md) |
| 透明发卡/睫毛/羽片的覆盖链、根梢、atlas复用与生产边界 | [透明卡片方法](references/alpha-cards.md) |
| 用途选择、P0/沙发范围、新用途确认、输入诊断 | [用途与输入诊断](references/purpose-and-diagnosis.md) |
| 生成方法、自动接缝、约束、局部修正、失败语义 | [候选、约束与修正](references/candidates-and-constraints.md) |
| 棋盘/布局复审、面板接续、adopt/restore、独立重开、批量恢复 | [复审、人工接续与重开](references/review-and-handoff.md) |
| 绘制/烘焙、旧贴图迁移、GLB/FBX/OBJ、交换边界 | [绘制、烘焙与交换](references/exchange-and-delivery.md) |

同一个真实任务只读当前需要的参考；不要一次加载全部。交付证据和最终验收记录由父线程/用户签核，技能本身不替代验收。
