# Blender UV Workflow

Blender UV 插件与配套 AI 工作技能：保留原 UV，制作可编辑候选，检查排布、拉伸、密度与约束，再由实际材质和目标消费者验收。

**0.8.9 源码预览 · GPL-3.0-or-later · Blender 5.2.1 LTS / 5.3.0**。插件界面主要为中文。English overview: [README.en.md](README.en.md).

## 下载与安装

从 [v0.8.8 发行页](https://github.com/tsist/blender-uv-workflow/releases/tag/v0.8.8)下载已发布的安装包。要体验 0.8.9，请按下文从源码构建。

| 文件 | 用途 |
| --- | --- |
| `uv-workflow-0.8.8.zip` | Blender 扩展安装包，不需要 blenderctl |
| `blender-uv-skill-20261117.zip` | 完整 `blender-uv` 技能、20 篇参考方法与 UV 工作流文档 |
| `SHA256SUMS.txt` | 两份安装包的 SHA-256 校验值 |

插件安装：Blender「编辑 → 偏好设置 → 获取扩展 / Extensions → 从磁盘安装 / Install from Disk」，选择插件 ZIP 并启用。打开 3D 视图右侧栏（`N`）中的 **UV Workflow**。不要把 GitHub 自动生成的整个仓库 Source code ZIP 当作扩展安装包。

技能安装：解压技能 ZIP，将 `skills/blender-uv` 整个目录复制到你的代理支持的技能目录（例如 `~/.agents/skills/blender-uv`），并将 ZIP 根目录的 `LICENSE`、`NOTICE.md` 一并保留到安装后的技能目录。复制前备份已有同名目录；只复制 `SKILL.md` 会丢失参考资料。此技能提供制作判断与操作指导，不是独立 UV 求解器。

## 工作方式

1. 在工程副本中选择目标网格，先明确独占图集、平铺或保留既有 UV 等用途。
2. 在侧栏选择展开方法与图幅，生成新候选；也可将当前 UV 复制为候选。
3. 检查拉伸、交叠、岛距、图边和密度；按用途修正接缝、预算与排布。保留原层，支持原生 UV 编辑后重新检查。
4. 用实际材质、近景及必要姿态比较，再保存并在目标消费者复核。数值通过不代替画面质量或用途确认。

已有工作流包括显式接缝辅助、Blender 原生展开路线、有限 `SMART_REPAIR`、候选保护与复查、密度/打包、使用规则、UV 迁移和辅助 Lightmap UV2。具体支持与拒绝条件见[主技能](skills/blender-uv/SKILL.md)与[工作流文档](docs/cli/UV工作流.md)。自动路线没有角色语义理解，也不保证任意模型通过。

0.8.9 增加「合并微岛并排布」。该入口处理单个静态三角网格的未采用候选，要求 2048×2048 独占图集、全选面，以及无固定点、接缝限制、锁定岛或复用。检查通过后才写入候选。详见[操作与验证](docs/VALIDATION.md#合并微岛并排布)。

## 插件、技能与 CLI 的关系

GUI 插件仅使用 Python 标准库和 Blender 随附的 `bpy`、`bmesh`、`mathutils`、NumPy。无网络服务、额外求解器、wheel 或付费插件依赖。

插件可独立使用。AI/CLI 协作需要在 [tsist/blenderctl](https://github.com/tsist/blenderctl) 取得匹配的 CLI 入口。逐岛格点法线迁移由 CLI 调用共享算法。使用前运行对应入口的 `uv describe` 核对插件版本与组合实现摘要。

## 验证与限制

0.8.8 在 Windows 上验证 Blender 5.2.1 LTS 与 5.3.0 的扩展安装、SMART 展开、新候选验证和保存重开。原 UV 坐标保持逐值相同。七个打包夹具核对方形和长方形边距、锁定岛保护、密度保持及部分选择的重叠判定。运行时更新版本声明并沿用既有求解器。[验收与复跑说明](docs/VALIDATION.md)

0.8.7 修复磁盘表面报告中 `sample.complete` 的类型判断，只接受 JSON 布尔值。非法值会拒绝并清除旧成功缓存。

本地已完成 33 项报告类型用例、7 项报告完整性用例、14 项 CLI 回归，以及实际 GUI「合法 → 非法整数拒绝并清缓存 → 合法恢复」观察。详情和可复现范围见[验证说明](docs/VALIDATION.md)。这不是完整报告 schema/防伪认证，也不是完整游戏生产认证。

技能原文保留本地制作案例与失败记录。其中 `F:/Blender AI/...`、`runtime/audit/...` 和 Wiki 条目是原环境的历史证据指针，**没有随仓库上传，也不是安装依赖**；使用者须替换命令示例中的本机路径。商业游戏模型、贴图、用户工程和私有审计均不分发，其权利不会随插件许可转授。

微岛修改的结果需要按材质和用途审阅。逐岛格点法线迁移限于已核验 UV 对应关系、整纹素位移和基础级采样条件。目标引擎、其他通道及各级 mip 需要分别验证。

## 开发与打包

```text
tools/uv_workflow_addon/   插件生产源码及有限测试
skills/blender-uv/         主技能与完整参考方法
docs/                     原工作流文档及公开发布说明
tests/                    报告类型运行回归入口
scripts/build_release.py  仅使用标准库的确定性打包脚本
```

运行 `python scripts/build_release.py --output <一个尚不存在的目录>` 构建当前源码的插件和技能包。以构建目录里的 `SHA256SUMS.txt` 校验。[发布说明](docs/PUBLISHING.md)记录来源与测试前提。

## 许可

源码、技能与本仓库配套文档按 **GPL-3.0-or-later** 分发，完整文本见 [LICENSE](LICENSE)。依赖与来源说明见 [NOTICE.md](NOTICE.md)。不随包分发的 Blender、Python、NumPy 及用户资产保留各自许可。
