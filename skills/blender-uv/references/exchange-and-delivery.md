# 绘制、烘焙与交换

## 1. 先确认下游到底需要什么

UV 完成只证明布局和硬检查；外观与交换必须单独验收。开始前确认：

- 目标程序/格式、是否需要多 UV、是否保留材质/贴图引用；
- 旧材质实际采样的 UV 层（包括 Texture Coordinate、Image Texture 未连接 Vector、Reroute/Node Group）；
- 目标图幅 W/H、颜色空间、通道、法线约定、边距/扩边；
- 哪些贴图要迁移、哪些重新绘制、哪些保留旧图；
- 外部引擎/绘制器是否实际可运行，是否有授权样例。

“UV 层存在”“导出成功”“`FINISHED`”“图片非空”都不是外观通过。

## 2. 复用现有 blenderctl 协作入口

### 原生工程接回的角点资格

从独立UV工作网格接回原生角色/服装前，核真实基础网格和完整有序角点/面/顶点对应，不能只看同名、同点面数或位置近似。OBJ省略无面引用顶点时，面角点仍可能全部对应；不为迁移删除原生孤点或改拓扑。0.7.4的EXPLICIT可显式给`vertex_domain=FACE_REFERENCED`，只将顶点对应域定为各自面引用顶点，完整角点/面/绕序及引用顶点一一对应仍须成立；默认ALL保持全顶点规则，INDEXED/PROJECTED不接受该选项。报告的全Mesh vertex_bijection可能为false，域内通过和排除索引必须分别说明。

新UV只作为新增候选层；源数据、目标原UV/render、材质、修改器和非目标保护。目标用途/维护规则须重新明确绑定，来源批准不随迁移继承。带SUBSURF时另查实际VIEWPORT/RENDER求值UV；缺rig/形态/动作不能把帧范围或细分平滑叫动作验收。实际T恤案例见`runtime/audit/uv-garment-native-20261114-v001/REPORT.md`与Wiki `procedures/blender-uv-bounded-topology-transfer.md`。

不要为 UV 任务复制第二套材质/烘焙/交换实现。使用已安装的完整 CLI，并先读当前帮助/Schema：

```powershell
& $blenderctl --blender $blender --jobs-dir $jobs texture bake --help
& $blenderctl --blender $blender --jobs-dir $jobs exchange export --help
& $blenderctl --blender $blender --jobs-dir $jobs material run --help
```

### 烘焙

当前 `texture bake` 只接受无modifier、无shape key的单对象，须有材质槽且每槽均有材质，目标为0–1内非退化UV的单图幅自烘焙；输出图像，不自动检查UV重叠。它未提供高模到低模的selected-to-active/cage参数，不是通用角色高低模烘焙器。带绑定/形态键角色需要由材质流程准备明确的烘焙工作副本或选择适用入口，保留原角色与可编辑候选；不能删除源Key/修改器来冒充原资产通过。方法论中的“高模作烘焙源”不表示当前CLI已实现该路线。

`texture bake` 的当前参数结构是：

```text
texture bake <file> --expected-sha256 <sha> --object <name> --scene <name>
  --view-layer <name> --uv-layer <name> --type EMIT|DIFFUSE_COLOR|NORMAL
  [--resolution <px>] [--samples <n>] [--margin <px>] [--frame <n>]
  [--resources <json>]
```

示例（只展示结构，路径/图幅按实际替换）：

```powershell
& $blenderctl --blender $blender --jobs-dir $jobs texture bake $candidate `
  --expected-sha256 $candidateSha `
  --object Product --scene Scene --view-layer ViewLayer --uv-layer UVW_uv_product_v1_angle_based `
  --type NORMAL --resolution 2048 --margin 16
```

- 颜色迁移用 `EMIT` 或明确的 `DIFFUSE_COLOR` 工作副本；不要把完整 Principled 的 DIFFUSE_COLOR 直接当 Base Color。
- `NORMAL` 单独烘焙，记录目标 UV/TBN、实际法线格式、已烘入强度和分辨率；它不是普通彩色图。当前已验路线输出 OpenGL +Y，目标若需 DirectX -Y 或其他切线约定，明确转换并验证，不能把本地输出格式当通用要求。
- 线性颜色转 sRGB 要实际编码 PNG 字节；alpha 不套该转换。保留源 PNG16 的线性精度，OETF 后只在最终 PNG8 量化一次。
- 小数值差、图片比错误对照好、`FINISHED` 都不单独构成外观通过；要在同相机/光照下比较源、迁移版和错误直接改绑对照。

### 交换

`exchange export` 至少需要候选文件、`--manifest` 和 `--expected-sha256`：

```powershell
& $blenderctl --blender $blender --jobs-dir $jobs exchange export $candidate `
  --manifest $exportManifest --expected-sha256 $candidateSha
```

先读 `exchange formats` 与当前 Schema；不同格式的实际支持范围由当前实现决定，不由扩展名决定。

### 材质

材质迁移/重建走 `material run`，通常需要 `--expected-sha256`、`--resources` 与 `--manifest` 或 `--template`；不要手工改 UV 插件内部状态来假装材质已迁移。材质工作改变消费者或材质槽后，人工将旧用途验收视为待重审：重新inspect消费者并独立检查，保留旧记录，需继续修改时可从当前来源层copy_uv新建候选。protection是单次操作前后的保护快照，不是候选持久保存的消费者绑定；adopt/validate不会仅因材质变化自动拒绝，不能以命令接受代替上述审阅。

## 3. 已实测的交换边界

以下只是已记录输入/格式范围内的观察，不外推到任意模型、骨骼/动画/材质：

| 格式 | UV 观察 | 已知损失/限制 |
|---|---|---|
| GLB 静态 | 所测两层完整保留为 TEXCOORD_0/1，V 翻转误差约 ≤2.98e-8 | 重导入层名变 `UVMap`/`UVMap.001`，active/render 选第一层；原 Blender 层名/编辑状态不保真；`materials=NONE` 时无材质 |
| FBX 静态 | 所测两层名称和坐标保持，角点误差 0 | 不据此保证 shader、任意 modifier/骨骼/动画等价 |
| OBJ 静态 | 只保留活动的一层 | 明确不支持多 UV；不要解释为全部 UV 保留 |

交换回执的几何重开 pass 不自动证明多 UV/材质正确。必须按实际格式读取每面角点、层映射、active/render 和有效材质；OBJECT 链接材质覆盖要与 mesh-data 材质分开核对。

UDIM 当前只识别和保护；不制作 UDIM。`<UVTILE>`、SEQUENCE/MOVIE 和未支持动态模板明确拒绝；外部 tile 只按 `image.tiles` 明确成员加资源 SHA，不扫目录猜。

## 4. 旧贴图迁移

推荐顺序：

1. 在专用工作副本中捕获旧 shader 实际使用的 UV 和颜色信号；记录旧层/材质/图像 SHA。
2. 保留旧 UV 层、旧材质和旧依赖；新 UV 候选另建，不覆盖旧层。
3. 新材质另建；需要颜色时先提取/烘焙到新 UV，法线单独处理。
4. 先分清显式层绑定与隐式active-render绑定。未接Vector的Image Texture、Texture Coordinate UV等会随`active_render`改变采样；指定层名的UV Map保持该层。迁移前在工作副本明确绑定旧层/新层并对照，未知时保持旧渲染层，不以切换活动层代替迁移。
5. 在相同相机/光照/分辨率下比较源、迁移版和错误对照；记录各通道和字节/渲染证据。
6. UV 布局/棋盘通过、材质外观通过、外部引擎通过分别签核；未执行写 `not_run`。

### 真实共享颜色图集的有限迁移

本机 RE3 完整静态组合案例：`runtime/audit/uv-aaa-fullasset-20261115-v001/`；详细方法在 Wiki `procedures/uv-color-atlas-migration-and-channel-packed-textures.md`。此例保留面部/装备/发眼原映射，只对共用 Body 图的衣服、皮肤和纽扣制作联合新页，不把整个角色塞进一页。

- 按资源和消费者联合排布，不按材质名合并。已有合格岛形可直接保护并重新排布，无须重复展开；同岛的原量化细缝也可能有真交叠，新层局部修正后仍须完整精确复验。
- **原图迁移与新绘制展开分别选路线。** 保持每岛总面积不保证岛内每三角/每方向的采样预算。此例重展后一个原约30.44px²的小面仅剩0.128px²，出现严重局部颜色损失；为迁移原图，优先保原作者岛形及局部分布，再联合排布。低拉伸指标不能代替原纹理保真，保原形亦不等于新展开质量更高；源量化细缝的局部改动单独披露。
- 原 half UV 只转 float32 保留。游戏/图像 V 约定通过显式采样变换处理；本例为 `(U,1-V)`，不是所有来源通用。不要从“全负绕向”单独推断需翻V。
- `ALBM` 等打包纹理的 alpha 未必是透明度；使用前确认语义。此例 RGB 显示设 `alpha_mode=NONE`；RGB 数据烘焙设 `Non-Color + CHANNEL_PACKED`，避免错误去预乘和重复色彩变换。真正的头发 `ALBA` alpha 另保留，不据此声称已迁移透明度或金属度。
- 可在独立烘焙副本将同一图集对象 join 为一个对象，多材质仍保留，原对象集不变。现有 `texture.bake` 支持多槽共用同一目标图，但只产图像、当前最大2048，EMIT不自动迁移原 alpha。先读当前契约，不能直接承诺4K。
- 显式旧 UV → 采源图 → Emission，新 UV 是烘焙目标。公共材质白名单未允许的节点可用等价已支持节点表达；本例用 Vector Math 的 Multiply `(1,-1,1)` + Add `(0,1,0)` 做翻V，不绕过原安全拒绝。
- 新图作为数据烘出后，最终颜色材质按正确色彩空间解释。编码域插值和原sRGB的线性域插值不交换，此配方不能承诺严格像素等价；需要严格颜色保真时另定线性烘焙/位深/编码流程。原新必须同相机/光照/过滤对照，并保留全三角抽样及最大误差。均值小不掩盖小三角的漏采/边缘损失；重采样非无损，RGB通过不授予Normal/TBN、ATOS、mip、压缩或游戏shader通过。

### 主法线换基与多UV保护

先决定下游需要统一图集，还是允许各通道使用不同UV。允许多UV且只需重新组织颜色时，可让新颜色图读取新UV，原法线图继续读取原采样UV；`NormalMap.uv_map`也显式指定同一原基底层。只在shader里翻V只改变图像地址，不会自动改变计算切线的UV。V变换、翻G、通道打包均按实际源契约处理，不从游戏名或贴图后缀统一推断。

本机RE3主NRMR原例：作者RE Mesh Editor导入UV已经做`(rawU,1−rawV)`，RGB进入NormalMap、Alpha是粗糙度。本次建立新旧采样层承载翻V后的原角点UV，图像和NormalMap共同显式绑定该层，Non-Color/CHANNEL_PACKED、不额外翻G。固定粗糙度0.45隔离主法线；未实现Detail、动态损伤或完整游戏shader。原生resident2K→新2K与streaming4K最高mip分开，不能把2K实验称保住4K全部细节。作者仓库已归档，本机源码身份与读取边界见审计`research/native/`。

若统一图集必须迁移法线，源采样与源基底先明确绑定，公共`texture.bake NORMAL`以新UV为目标；仅EMIT搬运法线RGB是错误控制，不是换基。对照实际世界法线方向，而非图像RGB相等；同几何/相机/姿态记录完整共同前景、均值/分位数/最大误差及极端位置，不能先删缝边或大误差再称通过。小机制实验通过不替代真实资产。

自写误差预测器先对照真实着色器，不能将 `calc_tangents()/MeshLoop.tangent` 自动称为当前Cycles的精确消费基底。本机5.2.1 RE3实证二者在特定面不同；用NormalMap常量输入响应可定位差异，CORNER烘焙可作该输入的实验提取途径，但未知面与过滤混面必须明报。修正预测器不等于修好整图，实际完整前景仍须重验；见 `runtime/audit/uv-two-residual-specialist-20261116-v001/integration/oracle-audit/` 与 `RE3-PHASE2-PARENT-REVIEW.json`。此例不证明所有固定分辨率方案不可达。

用高度信号比较两套UV时，保持同一物体/世界空间 `H(P)` 与物理距离。单用每UV像素高度差分乘固定强度，会混入旋转、密度和尺度变化，不能公平判断UV收益。必要时按实际表面Jacobian与逐点平滑法线求物理梯度，再用对应消费基底编码；先以原生Bump验证方向/尺度，再验曲面实际消费者。PNG位深读实际IHDR，默认byte-buffer `Image.save()` 不能充当RGB16证明；独立平面控制仅证方法，不代签资产近景。校准边界见同批 `integration/bump-control/RESULT.json`。

2026-11-15真实22对象/157039tri静态组合中，3对象/35384tri重烘的受检前后视图均值约1.91°/1.97°，但局部最大约140°/177°，故**单图集主法线保真未通过**。交付改用新颜色UV+原法线显式旧UV；切换active_render至新颜色UV的同机位全共同不透明像素比较，世界法线最大差约0.0000123°，float32分量非逐值无损。独立冷读保护原几何、旧UV和原法线图字节；冷复渲最多1byte差，不能称像素exact。双UV只证明所测Blender静态消费者保持，目标引擎/格式的UV通道及切线选择仍须另验；它不完成单图集法线重烘。

证据：`F:/Blender AI/runtime/audit/uv-normal-transfer-20261115-v001/`的`REPORT.md`、`delivery/PRESERVED-NORMAL.json`、`consumer/DIRECTION-COMPARISON.json`、`COLD-PIXEL-COMPARISON.json`；详细知识统一维护于Wiki `procedures/blender-pbr-baking.md`。实际可用原型包0.7.5仍保持原冻结字节；本节是之后的制作方法补充，未改生产插件/CLI或重建旧包。

#### 单UV极端翻向的有条件原生修补

仅在同几何旧UV主法线迁移出现严重局部反向、且源平滑N与几何Ng可能跨半球时，先核本机Cycles实现和具体极值点。5.2.1随包源码中，默认ABOVE_SURFACE沿smooth N构造烘焙观察方向；ACTIVE_CAMERA分支有Ng-front fail-safe。本例在专用已保存烘焙副本设置ACTIVE_CAMERA并添加明确相机，再经现有公共`texture.bake --type NORMAL`执行；它不是新CLI参数，也不是所有输入的新默认。不要用加margin、全局翻G/Z、增分辨率或删像素掩盖侧向问题。

NORMAL pass还会平均实际BSDF/BSSRDF闭包normal，完整Principled的反射闭包可能包含视向相关修正。需要隔离源法线信号时，只在烘焙副本用已支持Principled作纯diffuse载体：白Base Color，Metallic、Specular IOR Level、Coat/Transmission/Subsurface/Sheen Weight、Thin Film Thickness、Emission Strength均为0；原normal图、采样UV、NormalMap基底/强度、几何/角法线与世界矩阵保持。消费者仍用原Principled材质。独立Diffuse节点在本例被公共入口正确拒绝，失败保留；未扩白名单、未绕过拒绝，也未用EMIT或自写法线烘焙器替代NORMAL。

本机RE3三表面35384tri的2K有限静态研究，公共NORMAL job`107b224cbbfd463cbe14b1a19bce068e`使旧139.8°/176.9°极值降至2.61°/3.04°，旧12处>60°清零；同条件前领口黑裂纹可见消除。但全共同opaque域83424/81602像素最大仍52.974°/28.245°，>10°仍2124/1990，后侧细褶略平，故**严格单UV主法线保真仍fail**。它是另建未adopt的有损研究候选，不抹除上述双UV保原法线可用路线，不凭严重翻向消除宣称全PBR/动作/目标引擎通过，也不为余差作未经验证的唯一归因。

本轮完整22mesh静态GLB的三目标颜色/法线共新UV、文件字段及独立导入/冷读结构链已通过，严格单UV保真仍fail；这不是公共exchange接口扩展或目标引擎通过，见同批`exchange/RESULT.json`及`NORMAL-MAPPING-BRIDGE.json`。

来源与实际输入/对照：`runtime/audit/uv-single-uv-normal-20261116-v001/`的`SOURCE-FINDINGS.md`、`INPUT.json`、`PURE-INPUT.json`、`PURE-RESULT.json`及`visual/VISUAL-REVIEW.md`；本机随包Cycles源码与公开主线参照分别标明。详细知识仍归Wiki `procedures/blender-pbr-baking.md`。旧0.8.4精确插件/CLI/方法三包保持冻结字节；本次仅另供带normal-study-docs标记的方法更新，不把研究候选当软件默认行为。

### 严格保真可以优先保留共同源布局

强制单UV不自动要求使用新重排图集。先检查原颜色与法线的实际采样变换：若两者本来共享同一完整角点UV，可直接用该共同源层，让颜色图像、normal图像及NormalMap基底显式一致，保原图避免不必要的重采样。必须公开放弃新图集的代价，不能把此路线称为“新图集重烘已修好”。

2026-11-16重新授权返修的RE3三目标，在全部106152角点上原颜色`rawUV0→1−V`恰等于`RE3_NormalSamplingUV`。直接以此共同层读取原2K颜色/normal，两个固定全共同opaque视图83424/81602像素的法线最大差约1.2e−5°，源/旧UV与22mesh保持。三目标仍为opaque Alpha常数1；ALBM Alpha与NRMR Alpha是打包数据，不称透明贴图迁移。新颜色图集2K重烘仍fail；不能只为保住它盲增samples/分辨率。

精确版本源码必须追到helper实现：5.2.1的`triangle_smooth_normal_unnormalized_object_space`虽然名称/注释称unnormalized，`triangle.h`实际先`safe_normalize`插值N；bake编码器则用rawN。匹配decoder基可修这部分，但本例2K剩余误差主因是目标texel足迹/双线性重建；基修正没有使新图集严格通过。原先只读caller推断rawN的研究结论须据此更正。证据 `runtime/audit/uv-residual-repair-20261116-v001/re3/`，不是通用法线无损承诺。

共同源布局也须完整检查，不因原图看似正确就忽略源量化缝。本例原布局继承7对、合计约3.98px²正面积交叠；保参考采样版与零交叠版分别交付。在新`UVW_RE3StrictClean`层仅修5角点，按完整有序CORNER provenance/世界位置/rawUV/SourceRenderVertex及SourceTriangle核对应，不能拿不同编辑拓扑的vertex index硬配。全35384tri交叠7→0，旧UV/geometry/角法线/原PNG保持；同两固定全mask前视最大误差0.349248°（8像素>0.01°）、后视约9.44e−6°。实际同机位彩色局部未见新增裂纹，RGB最大变化1byte；这是有限静态取舍，不是字面1e−5°无损、16px独占新图集或新布局重烘通过。Clean GLB须单独报实际导入误差，本例前/后最大1.72°/0.77°，不继承BLEND精度。证据见同批`re3-uv-clean/`、`re3-clean-exchange/`和`final-review/CLEAN-RESULT.json`。

### 保采样格点的重排与连续footprint

允许重新布局、同时要求保留高频法线时，可先验证**保岛形/方向/尺度的整数纹素平移**，直接搬原texel，避免任意缩放旋转的重采样。条件是原图、采样UV和NormalMap基底已资格化；角点不必在纹素中心，但保存后每岛全角点须保持同一整数 `(kx/W,ky/H)` 偏移及边差。需复制连续三角的完整双线性footprint，包括原邻岛/背景texel，目的冲突逐值检查。只按纹素中心命中后扩边可能漏掉细薄三角；可用三角与纹素中心±1支持盒的连续相交检查资格化。单独修原UV微交叠并列出非纯平移角点，随后重验完整方向域；不由mask互斥推断岛内零交叠。基级保证不外推mip或压缩。

本机RE3按Q13改布局后，74分片格点搬图、5角点收口与实际消费者复验达到本轮冻结门，旧固定UV拟合失败保留。方法只对当前三目标/2K有限静态已验，图边2px/岛距3.75px不是引擎mip标准；交付与实证边界见 `runtime/audit/uv-two-residual-specialist-20261116-v001/integration/RE3-ACCEPTANCE.md`。

### GLB文件的UV地址与切线须分别验收

材质显式NormalMap UV不保证导出器用同一层计算TANGENT。Blender5.2.1本机glTF exporter的无参`calc_tangents()`读取活动UV；导出工作副本可把active UV设为法线基底，颜色继续显式用新层，源工程不保存。不要把active、active_render和节点指定层当成同一状态；先核实际版本源码/RNA与输出，不把此行为推广到所有导出器。

独立导入若仅丢极靠边的前景像素，先分开核local POSITION、文件规范定义的变换、实际导入矩阵与相机。近90°的float32矩阵分解/归一化可能丢原小角度，实际读取器又有额外舍入；局部坐标完全相同仍可能改变轮廓。RE3本例以源角度的高精度标准单位四元数恢复原完整83424/81602遮罩，并通过原法线门；BIN与其余JSON保持。该实验patch绑定本输入共同角度，不能泛用硬编码去覆写其他对象旋转。生产复用须逐节点绑定源变换并核真实导入/渲染，不能以改相机、补alpha或缩小遮罩代替修复。证据在同批 `integration/re3-mask-diagnosis/` 和 `RE3-GRID-FINAL-NUMERIC-REVIEW.json`。

解析GLB的baseColor/normal有效texCoord、完整角点UV、NORMAL/TANGENT及图像后，再做实际读取器对照。导入器可能重算切线，使错误文件在重导入时看起来正确；仅重导入图像不签文件TANGENT。需要时直接用文件TBN与真实PNG验证代表性采样，明确插值、双面和mip边界。真实RE3三对象本例中，指定正确活动UV消除了全部角点手性错配；原图字节不变、文件PNG固定点方向误差降至浮点量级。实际Blender重导入仍有局部约1.5°差，不能称无损。

完整组合须另外检查材质语义：前批22对象虽保结构，四个Transparent/Glossy Mix变默认白材质，Hair/Eyelash也未保Alpha，故当时只交Body/Skin/Button三表面；不能删对象或只看其余图签全角色。后续在工作副本把`Mix(white Transparent,原Principled,原PNG Alpha)`表达为原Principled直接读同PNG Alpha；四个低覆盖Glossy层以保原反射色/roughness/覆盖Factor的Principled纯反射近似，声明不保证全角度Fresnel等价。实际GLB六材质BLEND、原RGBA PNG/UV保持、完整22对象和三视图/冷读已作限定验证。当前5.2导出AlphaMode由Alpha节点表达决定，不靠旧Eevee blend_method；Alpha透明不等于折射玻璃。任意引擎排序/overdraw/动画仍另验。

现行公共exchange GLTF_PBR仍是默认UV基础色子集，这些原生工作副本实证不表示公共接口已新增NormalMap或任意Alpha图支持。基底证据：`runtime/audit/uv-aaa-glb-consumer-20261115-v001/REPORT.md`；透明交接：`runtime/audit/uv-aaa-glb-alpha-20261115-v001/REPORT.md`。详细知识在Wiki `procedures/blender-pbr-baking.md`，官方定义见Khronos glTF2规范。

## 5. 交付边界

- UV 插件 ZIP 不包含 blenderctl CLI；使用现有完整 CLI，并让插件 UV 模块与 CLI 的 `tools/uv_workflow_addon/` 来自同一源码身份。具体安装/包内容由父线程冻结和验收。
- 插件 GUI 本身只依赖 Blender 内置 `bpy`/`bmesh`/`mathutils`/`numpy`；完整 CLI 是 AI 公共入口的协作依赖，不是 GUI 安装前提。
- 最终表面/代表姿态用保存盘 `surface` 报告；面板棋盘 frozen VIEWPORT 和未保存 GUI 状态不是最终表面/外观通过。
- 交换/烘焙输出、贴图、模型和用户资产有各自许可；软件 GPL-3.0-or-later 不授予这些内容的分发权。
- 发布、全局安装、联网下载和外部上传不在本技能的默认授权内；需要时由用户明确批准。
- 证据保留源/候选/资源 SHA、请求 manifest、作业报告、独立重开、图像/交换文件和各自状态；不用一个总 `pass` 覆盖未验项。

原生回接若包含零用户原ID，正常保存可能丢失它们。先核落盘，不以RAM保护代替；本地T恤实例用新增辅助Collection的真实ID属性引用保留原Material，原fake与内容不变，用户数明确0→1。引用持有者须随候选保留，并在公共worker保存后冷读核实。这个实例不授予任意ID/任意版本通用保真；详见[服装制作方法](garment-production.md#接回原生工程与细分复审)。
