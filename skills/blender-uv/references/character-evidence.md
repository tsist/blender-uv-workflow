# 角色 UV 依据与适用范围

核验日期：2026-11-13。用于支持[角色制作方法](character-production.md)的决定，不是宣称全行业存在统一布局。详细网页读取证据和研究争议保存在本批审计目录；商业模型与贴图不随技能分发。

## 首要依据

| ID / 原始来源 | 支持什么 | 不能推出什么 |
|---|---|---|
| E01 [Adobe：Project Creation](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/getting-started/project-creation)；[Texture Set settings](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/interface/texture-set/texture-set-settings) | Painter按导入材质定义建立Texture Set；各set有通道、分辨率、shader；非方分辨率与padding模式 | Painter set与最终游戏材质/atlas一一对应；所有工具相同行为 |
| E02 [Frozenbyte：UV Mapping](https://wiki.frozenbyte.com/index.php/3D_Asset_Workflow:_UV_Mapping) | 明确讨论密度、单大图/多小图、镜像、切碎代价与padding；其项目角色1500px/m、近景头3400px/m体现分用途预算 | 将数值或“只留一UV Set”的该工作室限制套用本项目；镜像绝对禁用 |
| E03 [Funcom：《Conan Exiles》Armor and Clothing Modelling Primer](https://www.conanexiles.com/wp-content/wiki/2693791979.html) | 按镜头关注度分配头颈手/躯干腿/脚；平铺方向、局部alpha分组、重复装饰复用、换装预算 | 所有游戏脚都最低预算、所有alpha都必须独立UV层；其“UV set”措辞须结合具体管线解析 |
| E04 [Alena Dubrovina / Larian：Creating Characters for Baldur's Gate 3](https://80.lv/articles/creating-characters-for-baldur-s-gate-3)（2021） | 具名负责人说明共用头UV、鼻眼重点分辨率、角色模块化、皮肤/纹身/伤痕与shader定制 | 所有角色应使用该头模板；把主动重点分配导致的局部形变一律判坏或一律放行 |
| E05 [Square Enix：Achieving High-Quality, Low-Cost Skin](https://www.jp.square-enix.com/tech/library/pdf/GDC2017_characterskin.pdf)（GDC2017，Adelle Bueno / Eduardo Mosena） | 独占宏观图与共用平铺毛孔细节分层，顶点色控制混合，像素预算不只由主UV决定 | 将2017方案具体尺寸视为现代所有3A预算；本项目已支持相同shader |
| E06 [Blender Studio：A UV Unwrapping Guide](https://studio.blender.org/blog/a-uv-unwrapping-guide/) | 实际读到的指南讨论2D/3D绘制、连续性、拉伸与藏缝的取舍 | 越多缝或越少缝一律更好；本项目自动算法能力并非该文章背书（应查本机实现）；旧文档API直接适用当前版本 |
| E07 [Adobe：Texture dilation or Padding](https://experienceleague.adobe.com/en/docs/substance-3d-painter/using/technical-support/workflow-issues/export-issues/texture-dilation-or-padding) | 扩边与mip串色的机制，padding是贴图内容扩展 | 某固定像素间距可保证所有压缩/过滤/引擎 |
| E08 [Zach Tsiakalis-Brown / Zulubo：Realtime Dynamic Gore Decals](https://www.zulubo.com/blog/realtime-dynamic-gore-decals)（2020） | 具体实现可用第二UV通道解决第一层重叠，记录当时LOD未支持；同模型不同层可有不同拆分理由 | RE3的UV1一定承担同一功能；所有伤口系统同构 |
| E09 [Epic：MetaHuman Assets Overview](https://dev.epicgames.com/documentation/metahuman/assets-overview?lang=en-US) | 明确头/身体/服装资产以及脸身材质/纹理组织 | 所有角色必须分成MetaHuman的资源结构 |
| E10 [Phosphor Games：Optimizing mobile VR character art](https://www.phosphorgames.com/post/optimizing-mobile-vr-character-art)（2017） | 图集象限位置可成为换装接口；创作分辨率与运行时LOD分辨率不同 | 这是现代3A面部质量基线；所有岛位置都可自由更改 |
| E11 [Mariia Zatorska：Real-time Hair Creation Workflow](https://marizatorska.artstation.com/blog/40NN/real-time-hair-creation-workflow)（2022） | 具名作者的发卡UV位置/纹理变化、条带宽度与相机观察经验 | 原文未明说的atlas共享岛规则；三角数范围或特定发卡布局为强制标准 |
| E12 [Ephere / Ornatrix：Hair Cards](https://ephere.com/ornatrix/app/docs/1/Hair_Cards.html) | 共享发卡纹理域与逐卡场景烘焙域不同；原文明确共享texel会复用烘焙结果，展示独占第二通道的实现 | 所有发卡必须UV1或必须逐卡独占；该工具实现等于本项目已实现 |

官方资料说明工具/格式行为，工作室指南说明其项目规定，具名访谈说明作者经验。本方法中的接缝部位候选是这些原则与局部实证的综合建议；没有把每个候选位置包装成国际统一标准。纯数学量纲、2倍线密度约4倍像素面积、整数周期repeat条件属于可检验推导，不伪称来自美术师原话。

## 本机原角色观察

审计根：`F:/Blender AI/runtime/audit/uv-development-20261113-m5-v002/character-research/aaa-corpus/`。

- BG3影心、阿斯代伦：原手掌背两个主岛、五指相连；莱埃泽尔另有指甲岛。三者有相关模板，算同一管线的相关样本，不能算三套独立行业标准。
- RE3吉尔：同一4141tri手域，UV0掌背主岛加五个独立指岛；UV1连续主岛加腕条。层用途未完整执行shader验证，不能以任一层强制规定每手几岛。
- 原数据入口纠错：直接原MESH half2→float32；旧读取器在half精度翻V后逆翻会丢精度，旧`pre_vflip`不应冒充原字节。当前正式图以`analysis/re3-jill-raw-v002`为准。

全身材质/图集补证：`F:/Blender AI/runtime/audit/uv-character-methodology-20261113-v001/local-atlas/OBSERVATIONS.md`。

- Body、Skin、Button不同材质共享Body_ALBM/NRMR；Props、Bag、Holsterparts、Supporter共享Props图。Face另有图；这是逐项原MDF引用与原UV0叠图观察。
- Body/Props/Face所提取streaming首mip均2K，但同图/跨图部位密度明显不同。按同原坐标尺度和整个材质面域，Face/Skin面积平均线密度约2.84倍；不是纯正脸局部指标或通用倍率。
- “UV绝对三角面积和”不等于唯一填充率；可见组和LOD不能全部混算。原资源最高mip不等于运行时驻留mip。
- 商业原资产不是开源；提取器开源也不转授角色版权。只作本地参考，不进插件公开包。

本轮观察不包含完整游戏shader、动画、烘焙或引擎过滤验收，也没有角色候选获得质量批准。详细分项状态随任务证据更新，不因技能新增而自动通过M5。

## 使用时的证据标准

2026-11-15已将真实原包用于制作实证：影心LOD0主头＋耳全7930tri，沿原runtime边界公共ANGLE_BASED重展/联合排布，12岛、净覆盖68.77%、零重叠/反向/越界，原UV与源三角保护及独立重开通过。独审只通过静态既有边界切片，不证明全角色、重新选缝、Rig/动画或材质迁移。吉尔完整Skin_Mat肩胸/双臂/双手14808tri已准备，原UV0/UV1 exact、无几何阻断；runtime拆点保留。详见Wiki `references/aaa-character-uv-references-bg3-re3-2026.md` 和 `F:/Blender AI/runtime/audit/uv-aaa-validation-20261115-v001/REPORT.md`。网页可下载备选另列来源与转换未知项，不能将“有FBX”当原UV/骨架已验。

新项目先确认：样本身份/LOD/可见组合、UV通道、图集消费者、分辨率、制作目标和原始来源。把“直接观察”“作者陈述”“推断”“本机验证”分开记录。只看到搜索摘要、页面导航、截图或视频标题时，不声称读完教程或取得生产规范。

数值门槛必须经具体用途基线确认；现有P0/沙发值不迁移到角色。反例推翻通用说法时，应修正规则及其调用路径，不能保留口号再用备注掩盖。
