---
name: live2d-from-art
description: 从角色原画或分层 PNG/PSD 制作、修复可交互 Live2D 角色，涵盖保真拆件、补绘、网格与参数绑定、实验性直接生成 MOC3、网页预览、口型及自然待机。用于用户要求把图片做成 Live2D、优化现有模型或复用代码建模流程时。
---

# 从原画制作可交互 Live2D

## 一句话端到端制作

用户无需重复四阶段长提示。收到“把这张图做成可直播的半身 Live2D”时，按 [生产工作流](references/production-workflow.md) 检查素材、姿态、构图与工具，再自主推进到实际可验证的交付；用户的阶段限制和暂停要求优先。默认保留原画身份与姿态，目标 VTube Studio + OBS、浅角度头身动作、独立眼球与自然次级运动。

这是代理制作流程，不是通用图像自动转换器。新角色的 masks、coordinates、geometry、parameters、atlas、draw order、部件名必须重新适配。不承诺在没有视觉判断或无人配合面捕时自动成为成品。

先读 production-workflow.md，各阶段按需读专业参考。质量声明用 [证据契约](references/acceptance.md)，直播连接与性能用 [直播设置](references/streaming-performance.md)。改进依据见 [项目复盘](references/retrospective.md)。

### 可重复执行的交付工具

```bash
python scripts/check_runtime.py PROJECT/runtime/Character.model3.json
python scripts/pack_runtime.py PROJECT/runtime/Character.model3.json PROJECT/release/build-001
python scripts/record_review.py PROJECT/release/build-001 PROJECT/qa/review.json --target vts
# 实际执行并审阅测试，填写 review.json 后：
python scripts/release_gate.py PROJECT/qa/review.json PROJECT/release/build-001
```

初始化 review 不产生 PASS；包和 review 不覆盖旧版本。record_review 在包全部定稿后执行；补充 VTS 配置后重新记录资产，重测相关项目，不能只更新哈希复用失效结论。pack_runtime 只收 model3 引用；vtube.json 等额外配置显式审核后加入。

目标是保留角色辨识度并让动作可信。可加载、会动、好看是三个不同验收层级，分别报告。过去案例曾通过结构检查但因歪眼、拼接和持续摇晃被用户否定；不能用技术测试替代画面判断。

## 选择路径

先检查用户已有素材和项目，确定目标是网页、VTube Studio（VTS）、还是可继续编辑的 Cubism 工程。复用已有原图、授权素材和项目约定，不自行换脸或扩大到 TTS/Agent 平台。

- 有成熟模型：先修现有资源和参数映射，不重做拆图。
- 有 PSD/分层 PNG：检查默认拼合，再做网格与形变。
- 单张图片：先保真拆件和遮挡补绘。生图工具可辅助局部补绘，不能把一张“部件展示图”直接当作已对齐的建模素材。
- 用户要求不用 Cubism Editor：可采用本 Skill 的实验性 MOC3 代码路线。其局限及格式细节见 [直接建模](references/direct-moc3.md)。不要把它描述成官方编译器或通用一键转换器。

## 工作顺序

1. **建立基准**：保存不可覆盖的原图、画布、透明通道、部件清单和检查点。先读 [素材处理](references/artwork.md)。明确正脸、转脸范围与可见动作，分辨率沿用真实素材质量，放大不等于新增细节。
2. **静态重组**：将部件按坐标和层级拼回原图，解决眼形、眉形、脸宽、发际线、领口及接缝。默认姿态像原图后再加动作。
3. **模型构造**：先静态 MOC3 加载，再逐个增加眼、嘴、眉、头、身体和发丝参数；各阶段保留可回退版本。读 [直接建模](references/direct-moc3.md)。
4. **网页验证**：用实际 Cubism Core 渲染目标 MOC3，原图并排、同尺度、支持脸部放大、参数滑块和复位。读 [动作与网页](references/motion-and-preview.md)。
5. **动作润色**：先单参数，后组合；检查遮挡、拉伸、图层贯穿及姿态停顿。待机不能用持续摆动掩盖模型问题。用户说“像鬼”“纸片”“歪眼”时，先停自动动作、回到中性姿态，定位后再演示。
6. **交付**：按 [验收与交付](references/validation.md) 检查运行包、分层源文件、制作代码与预览。区分已测平台与未测平台；用户要求 VTS 时实际加载验收，网页通过不能冒充 VTS 通过。

## 可复用资源

- [本次案例与代码导航](references/worked-example.md)：原项目位置、复建顺序、已验证环境、哪些常量必须按新角色改写。
- `assets/worked-example/`：实际使用的制作脚本、网页和 MIT 序列化库快照。是需要适配的案例，不含原画、生成补绘、专有 Core 或其他 vendor 库，不是开箱即用工程。
- `scripts/check_runtime.py MODEL.model3.json`：检查模型清单引用、纹理/MOC 文件存在性和 JSON 可解析性。不会证明 MOC 二进制有效或画面好看。

不要覆盖唯一原图；无需为每个可逆调整重复询问用户。涉及生成图片时使用当前环境可用的图像工具及其规范；没有图像工具时说明所缺补绘，继续能独立完成的代码和结构工作。
