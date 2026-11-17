# 透明卡片UV：先核消费者，再核方向与复用

2026-11-14，D04有限学习。详细来源与证据见Wiki `procedures/alpha-card-uv-consumers-and-root-tip-validation.md`；尚无真实游戏卡片生产交付。本地toon发块、SDF阴影和无材质发物理代理不替代alpha card。

## 先建立覆盖链

记录卡片面集、实际材质、图像/通道、显式或隐式UV层及变换、透明输出、分辨率/过滤/地址方式，再核**这些UV实际采样域**内的覆盖。RGBA.A或独立灰度图Color都可能控制透明；检查可达组内的Alpha/Transparent混合，不只搜索ImageTexture.Alpha连线。4通道、黑背景、BLENDED标志或文件名不是透明证明。

固定同几何/UV/图像做真实透明与强制不透明对照，观察外轮廓和孔隙透见后景；显示灰度的实心Emission不算。实际渲染引擎、透明方法及背面/后层须记录。Cycles结果不认证EEVEE或游戏排序；目标引擎mip/压缩/LOD/风动未测则保留未验。

源图覆盖通道与最终合成Alpha分开读：后景不透明时，PNG输出A全1仍可以包含正确的前层透明。不能据最终Alpha推断卡片不透明；应核真实接线及能识别的后景透出。

## 根梢与方向分工

Root标量用于沿长度的变化，Flow/Tangent按各自编码控制方向，Alpha/Depth/ID另有职责；不要互接或用世界Z猜根梢。先核附着端/梢端，再用不对称图案或已知Root图观察。180°旋转可能保足迹、密度与畸变，却把已绑定轮廓/根梢倒置；不能仅靠数值放行。Epic UE4.27的自动根上梢下与masked/TAA是其shader约定，不升级为全行业/Blender通则。

## atlas复用与独占烘焙

可明确读取相同内容的卡片允许有意共享texel；每卡独立绘制或全发型遮挡烘焙另需可独立寻址域。共享UV、3D相交、透明排序分别判断。当前UV0.7.4用真实完整岛`reuse_groups`表达合法重叠，按schema选EXCLUSIVE；TILED不接受非空复用组。不要因计数或模式名字重排固定atlas、放宽阈值。

## 当前实证边界

本地三源仅得到输入资格负例：全root/nested组及替代覆盖路径已核，但未建立可核覆盖链；源SHA不变。原初把无材质代理泛化为全部睫毛的判断已纠正，实际上下睫毛有材质但未证明覆盖消费；未实渲原工程，不断言所有最终行为。详情：`F:/Blender AI/runtime/audit/uv-d04-cards-20261114-v001/input/INPUT-QUALIFICATION.md`。

继续解码该真实睫毛PNG，2048²全4,194,304像素Alpha=255；当前render UV的上/下睫毛域1,137,771/189,906个像素中心也全为1。该图没有可恢复的非恒定A覆盖信号；彩色RGB不能凭猜测改作遮罩。它可以服务另一种轮廓/着色设计，不据此称原资产错误。其余两UV层塌到单点，面积域为0，更不能任取旧层当有效映射。这里是像素中心域检查，不认证细分最终采样、边缘过滤或root-tip。原图不改；另做原创试件与原生消费者恢复明确分开。

官方/原作者依据为Epic《Photorealistic Character》Hair段与Ephere Ornatrix《Hair Cards》atlas/channels/baking段；Blender5.2页直接访问402，实际接口仍按本机RNA核，不用旧教程字段猜测。隔离自制机制试件须明确标记，不冒称成熟游戏发卡样本、完整发型或生产验收。原文链接、核验日期及试件证据由上述Wiki统一维护。

本轮原创两片试件经公共`copy_uv→settings→rotate`后，两坐标阶段均在声明完整岛复用下数值pass；旋转仅右片180°，密度、p95/max和足迹不变，实际六图却显示根梢/渐细端倒置。`directions=[]`的方向检查pass只是无规则违例，不代表自动识别根梢。Alpha override=1的独立对照露整矩形，真Alpha对照孔隙透棋盘；独立cold核几何/UV/packed/接线，并复渲解码像素零差。最终绑定材质后的A/B另作公共surface，因该入口不继承复用对应而两者raw overlap fail，保留原状态。零图边/默认数值通过只属这个机制试件，非图集padding或游戏画质标准；不要继承旧坐标阶段回执冒签后绑材质工程。实际图与审核见本批`consumer-probe/REPORT.md`、`review/PROBE-VISUAL-REVIEW.md`。

已知根梢时可把语义落实为规则：先核真实同面相邻角点与物理附着端/梢端，再用`settings.directions`表达有向UV边角度，保留完整现有settings与几何绑定。本试件loops0→3、4→7定义root→tip，事前目标+V/90°±0.01°；只设规则不动UV，数值及公共cold通过。随后右片旋转180°被公共入口以方向偏差180°的CONFLICT拒绝，未落盘候选、未执行新cold；合法分支/旧图/源SHA保持。该角度与容差仅为此已知试件，不强加给未知图集；一个方向锚也不证明整束流向/扭转/物理切线。证据`direction-guard/DIRECTION-GUARD.md`。拒绝即停止这次编辑，不换入口或删规则凑通过。

## 真实原例：材质名、通道和原值都要对上

RE3原安装包的主发/睫毛例（本地研究，不授素材分发或原引擎认证）显示：同一ATOS纹理A全1，Red却可能才是覆盖。主发44742原点/41809三角的UV0离散域有1,402,335像素，Red非恒定；头部睫毛对应4314像素域却全255，因此后者不能只凭名字当alpha卡片。不要从整图或普通低mip的变化推断当前高分辨率采样域有覆盖。

按**材质实名**连接mesh槽与MDF，而不是假设序号相同：此例睫毛mesh材质0对应MDF1；主发为0→0。主发的BaseShiftMap引用ALBM，睫毛的BaseMetalMap引用ALBA，不能按邻近路径/同角色混贴。社区读取器0.66的ATOS.Red、UV2/Blue遮挡及hair clipping旁路是有版本的实现解释，不能当Capcom运行shader已证明，更不能仅凭AlphaTestRef照搬阈值。

原half UV先直接解码保存，再在诊断shader显式做图像行序的`V_sample=1−V_raw`桥接；两套原UV均不改。半精度parser翻V后再翻回会丢原值：本例UV0首点V的原half为0.01189422607421875，旧反翻值0.01171875。half→float32只精确保留已量化值，不恢复作者量化前float。逐层原offset/bit、实名材质、TEX压缩载荷与完整像素域的独立核对见`F:/Blender AI/runtime/audit/uv-d04-real-cards-20261114-v001/input/INPUT-QUALIFICATION.md`、`independent-input-review/REVIEW.md`。当前原游戏层选择、根梢/Flow、实际mip/LOD、完整绑定仍unknown；不因本地查看器可见就重排固定atlas或签生产。

真实原例现已做六图单变量诊断：A用原UV0读ATOS.R，B只改读原UV1，C只强制不透明。条束/末端和发片边缘可见差异，只证明本Blender消费者响应，不能靠“更像头发”判原游戏UV选择。完整原几何、两层125427角点UV、ID及packed PNG均独立cold保持，代表图全RGBA复渲零差；基本几何公共诊断通过不等于全空间/着色通过，开边是发片结构信息，不自动补洞。一次剪白曝光修正有独立旧/新工程，最终六图统一参数；偏暗、32采样噪点/空腔保留，不能把每个黑区都说成透背景。详细证据在同批`diagnostic/REPORT.md`与`independent-visual-review/REVIEW.md`。

核复渲时比较解码后**全部RGBA元素**。本机Pillow的RGBA差值图默认`getbbox()`可能只看差值Alpha，Alpha差为0时会漏掉RGB变化；不能单用它判像素一致。新批`PARENT-VERIFICATION.json`以全通道数组核对本原例及上批原创试件，两者均确实零差；历史证据保留，修正验证盲点不改图片。

## 屏幕尺度与插值：覆盖总量不能代替细节

要判断远景透明边缘，先把照明与覆盖分开：在单用户网格/材质和**独立Camera数据块**的隔离场景，用固定白Emission与Transparent混合、透明Film做覆盖pass；另做只强制不透明的控制。保留原UV、图像、采样变换与透明链，其结果不是原游戏shader或Beauty复现。

按完整几何投影确定屏幕高度和固定ROI，记录相机RNA写入后的实际连续跨度；不要用Alpha支持域反算尺寸或自适应选ROI。以实际FLOAT32 EXR读回Alpha计算`M=sum(alpha)`、`m=M/h_geom²`及相对不透明控制的`rho=M/M_opaque`；分母0时未定义。PNG仅展示，EXR须核真实chlist的Alpha像素类型，不凭`is_float`推断32位。ROI外覆盖非零先检查隔离/范围，不能为达标扩大分母。这里的ROI留边不是atlas padding。

同尺度、相位、ROI和采样条件比较Linear/Closest，用同ROI平均绝对差；有Monte Carlo波动时，把两种插值差与各自跨seed差按**同一范数**比较。本例32px两插值差约0.000480/0.000455，而跨seed差约0.001540/0.001546，未被这次有限对照分离；不继续加样本凑赢家，两seed也不证明收敛或时间抗闪烁。未来不同输入/用途需要自己的对照，不强制复刻本例矩阵/种子。

真实RE3原例在512/128/32px的`m`约0.6256、相对不透明`rho`约0.908，原图近看有细丝、缩小后细节消失；总覆盖量相近不代表细节足够、边缘稳定或质量更好。展示采用实际透明PNG同尺度固定裁剪、明确最近邻放大倍数；放大不新增细节。该正交实验只比较屏幕尺度与Image Texture插值，不能认证物理距离、游戏mip/各向异性/压缩/LOD、斜视、动画或目标引擎。

本机11张EXR32/PNG/Alpha数据与预定指标、父独立复算和审核见`F:/Blender AI/runtime/audit/uv-d04-scale-filter-20261114-v001/REPORT.md`。本次没有重排UV、修改生产插件或分发商业素材。原生冷开后非活动Scene的matrix缓存可能尚未求值；保护比较先以该Scene的view layer更新求值，再与原RNA/磁盘快照核对，不能把缓存差当成获准修改相机。
