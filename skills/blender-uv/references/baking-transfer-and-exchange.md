# 绘制、烘焙、迁移与格式交换

本参考覆盖 UV 完工后的下游衔接：保护旧贴图消费链、迁移共享颜色与切线法线、在模型间迁移 UV、调用公共烘焙与材质入口，以及核对 GLB/FBX/OBJ 交换结果。UV 布局与贴图外观分开验收，确保每一环都有可复查的证据。

## 先查旧贴图消费链与 `active_render`

改布局或换 UV 层前，先理清现有着色器如何取样：

- **隐式绑定**：未连 `Vector` 的 `Image Texture` 节点和 `Texture Coordinate.UV` 输出默认读取 `active_render` 层；切换 `active_render` 会立刻改变这些节点的采样结果。
- **显式绑定**：指定了层名的 `UV Map` 节点始终读取该层，不受 `active_render` 切换影响。
- **保护做法**：保留原 UV 层、原 `active_render` 绑定与原材质；新建候选 UV 层与新材质副本，用显式 `UV Map` 节点分别对比旧版与新版渲染画面。

## 旧贴图迁移与切线法线处理

### 共享颜色图集迁移

1. **保原岛形优先于重展**：若目标是把已有成品颜色图搬到新排布图集，优先通过 `copy_uv` 保留原作者岛形与内部三角比例，再做联合排布，避免重展把原小面压扁导致局部细节丢失。
2. **核对 V 轴与通道语义**：原半精度 UV 转 `float32` 保留；游戏贴图若需翻 V，在着色器用显式矢量运算表达。打包贴图（如 `ALBM`、`NRMR`）的 Alpha 常存粗糙度或金属度，数据烘焙时设为 `Non-Color` 与 `CHANNEL_PACKED`，避免错误去预乘或重复色彩转换。
3. **颜色烘焙走 `EMIT` 或清晰工作副本**：用 `blenderctl` 的 `texture bake` 把源图经 `Emission` 烘到新 UV，保持线性精度，最后在目标色彩空间编码输出，并在同机位同灯光下与原版逐像素对比。

### 主法线换基、双 UV 保护与逐岛整纹素搬移

切线空间法线绑定着三角化、顶点法线、UV 方向与切线手性，按下面三条路线择优处理：

1. **允许多 UV 时优先双 UV 保护**：新颜色图读新 UV 层，原法线图和 `Normal Map` 节点继续显式绑定原采样 UV 层，零重采样即可完整保住原始高频法线细节。
2. **允许整纹素平移重排时走 `uv grid-transfer`**：针对已配对的静态三角网格和打包 `Non-Color` RGBA8 切线法线，运行公共 `uv grid-transfer --params <json>`。工具逐岛核验精确几何、TBN、整数纹素偏移与双线性覆盖足迹，零重采样直接搬移原纹素并输出 `grid-transfer/normal.png` 与 `receipt.json`，源工程与原图保持不变。
3. **必须统一单图集重烘法线时**：
   - 运行 `texture bake --type NORMAL`（或静态高低模投射走 `material projection-bake`），记录目标 UV 层、TBN 约定（默认输出 OpenGL `+Y`，目标需要 DirectX `-Y` 时显式翻绿通道并复验）、分辨率与扩边像素。
   - 遇到源平滑法线与几何面法线跨半球引起局部极端翻向时，可在专用烘焙副本将采样视向设为 `ACTIVE_CAMERA` 并使用纯漫反射承载的 `Principled BSDF`（金属度、高光、清漆、次表面等均置 0）隔离法线信号，再在完整共同前景域对比世界空间法线角度误差，确认画面无黑裂纹与细节平塌。

## 模型间 UV 迁移（`transfer`）

在同源或近共面模型间把 UV 从源对象迁到目标新候选，走公共命令链：

```powershell
# 1. 绑定源对象与源活动 UV
& $ctl --jobs-dir $jobs uv transfer-source --params $srcParams --output $sourceRecord

# 2. 组装目标迁移参数（INDEXED 或 PROJECTED）
& $ctl --jobs-dir $jobs uv transfer-prepare --params $prepParams --output $runParams

# 3. 执行并验证新候选（或直接 uv transfer-execute 执行工程内草稿）
& $ctl --jobs-dir $jobs uv run --params $runParams
```

三种迁移模式按拓扑对应关系选：

- **`INDEXED`**：源与目标顶点数、面序、角点索引完全一致时使用，精确一一对应。
- **`EXPLICIT`**：传入显式 `corner_map` 与绕序映射；遇到源/目标含未引用孤立顶点（如 OBJ 导出省略孤点）时，传 `vertex_domain: "FACE_REFERENCED"`，在完整保留原几何与孤点的前提下完成面引用顶点与角点双射迁移。
- **`PROJECTED`**：用于显式指定面域、近共面单层且完整覆盖的局部投射，配置 `max_distance_m`、`normal_degrees` 与 `uv_tolerance_px`。

迁移后的新候选保留源数据与目标原 UV/pin，按目标的新用途重新绑定 `settings`/`recipe` 并做棋盘与冷重开核验。若原生工程里存在零用户原材质，另存前建辅助集合属性持有引用，确保冷重开后数据块完好落盘。

## 公共烘焙与格式交换协作

下游烘焙与材质重建直接复用公共 `blenderctl` 入口：

```powershell
# 单对象自烘焙（颜色 EMIT / 切线法线 NORMAL）
& $ctl --jobs-dir $jobs texture bake $candidate --expected-sha256 $sha `
  --object Product --scene Scene --view-layer ViewLayer `
  --uv-layer UVW_uv_product_v1_angle_based --type NORMAL --resolution 2048 --margin 16

# 静态高低模投射烘焙与材质装配
& $ctl material projection-bake --help
& $ctl material run --help

# 格式导出（先查 exchange formats 核对当前支持项）
& $ctl --jobs-dir $jobs exchange export $candidate --manifest $exportManifest --expected-sha256 $sha
```

导出后逐格式核对实际 UV 层、角点坐标与切线手性：

| 导出格式 | 实测 UV 行为 | 交付前核对要点 |
|---|---|---|
| **GLB / glTF** | 完整保留多层为 `TEXCOORD_0` / `TEXCOORD_1`（V 轴按规范翻转） | 重导入后层名会重置为 `UVMap`/`UVMap.001`；导出器按当前活动 UV 计算 `TANGENT`，含法线贴图时在导出副本把活动 UV 切到法线基底、颜色继续显式指向新层，并核对节点旋转精度与透明材质映射 |
| **FBX** | 完整保留多层名称与角点 UV 坐标 | 另行核对目标引擎里的法线手性、缩放单位与材质连线 |
| **OBJ** | 导出当前单层活动 UV | 需要多层 UV 时改用 GLB 或 FBX |

导出完成后另起进程重新导入并抽查角点 UV、法线方向与贴图绑定，把 UV 布局、材质外观与目标引擎验证分别登记交付状态。
