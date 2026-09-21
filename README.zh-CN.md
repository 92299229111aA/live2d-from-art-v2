# 从原画制作 Live2D 的 Agent Skill

## 本轮升级：一句话启动完整流程

> 使用 $live2d-from-art，把附件角色做成保真半身 Live2D，用于 VTube Studio 和 OBS 直播，自动完成制作与可执行验收。

不再需要逐次粘贴阶段提示。新增开工姿态/构图判断、目标运行时早期测试、直播尺寸下的动作验收、清单白名单打包和证据哈希门禁。真人追踪仍需设备及配合；未实测不能冒充成品。

- [制作流程](references/production-workflow.md)
- [本次项目复盘与改进](references/retrospective.md)
- [验收证据规则](references/acceptance.md)
- [VTS/OBS 与性能设置](references/streaming-performance.md)

工具回归测试：`python scripts/test_pipeline.py`。真实模型打包：`python scripts/pack_runtime.py MODEL.model3.json NEW_PACKAGE_DIR`。验收工具用法见 SKILL.md；机械检查不能替代视觉判断。

这是一次实际制作流程的整理：原画拆件 → 遮挡补绘 → 默认姿态拼回原图 → 网格和参数 → 直接构造MOC3 → 网页调试 → 口型与自然待机 → 验收和打包。

**它是需要Agent按角色适配的实验工作流，不是任意图片一键变成精美Live2D的工具。**

## 安装和调用

```bash
npx skills add fifteen42/live2d-from-art
```

也可以把整个仓库复制到所用Agent的skills目录，保留文件夹名`live2d-from-art`。Codex通常使用`~/.codex/skills/live2d-from-art`。

调用示例：

> 用 $live2d-from-art，把这张角色图做成可交互Live2D。保留原图神态，在网页上并排检查眨眼、嘴型和自然待机。

## 先读什么

- [Skill入口](SKILL.md)：工作顺序和分阶段验收。
- [原画拆分与补绘](references/artwork.md)：对齐、蒙版、隐藏皮肤和接缝。
- [直接MOC3建模](references/direct-moc3.md)：文件类型、序列化约束和参数绑定。
- [网页与自然动作](references/motion-and-preview.md)：避免持续摇摆、音量口型和实际预览。
- [验收与交付](references/validation.md)：结构通过不代表画面好看。
- [示例代码适配指南](references/worked-example.md)：输入要求、运行顺序及需要改写的角色坐标。

仓库附带制作代码和MIT序列化器，不包含角色原画、生成补绘、音频以及Live2D Core等vendor库。依赖和运行步骤见[英文README](README.md)。你需要提供自己的素材及兼容的运行库。

## 当前能力边界

实验路线可生成运行时MOC3，不能生成Cubism Editor的cmo3编辑工程。案例主要覆盖浅转脸、眼嘴眉、呼吸和轻微发丝运动；嘴型按音量驱动。换图需要重做坐标、蒙版和网格适配，不能只替换图片文件。

最新版动作曾在原项目网页中验证；当前剥离素材后的代码仓库做了语法及清单脚本检查，尚不是下载即可播放的独立演示。

第三方序列化器保留原MIT声明，其余内容尚未指定仓库级开源许可证。公开可见不等于已授予所有内容的再分发许可。
