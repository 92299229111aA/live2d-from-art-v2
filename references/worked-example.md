# 本次项目复用指南

## 案例来源与素材

本仓库来自一次角色原画到可交互Live2D的制作实验。完整角色项目使用Reference.png、分层素材与补绘，生成Character-Runtime.zip和Character-Layers.psd。

仓库只发布工作流、制作代码和第三方MIT序列化器，不包含原角色图像、补绘、音频或专有运行库。继续已有角色时复用自己的完整项目；新角色先准备输入，再适配代码中的坐标和蒙版。

## 快照

`assets/worked-example/character/`保存本轮克制待机版本的制作和预览代码，`tooling/py-moc3/`是相邻路径依赖。文件之间保持原相对目录。以下输入必须另备：

- 原图 `Reference.png`；提取脚本读取的 `Face-underpaint-generated.png`。
- 实际运行网页的vendor：Cubism Core、Pixi、Live2D适配层。
- 若保留对比旧图按钮和语音示例：`Previous-Assembly.png`、`audio-check.wav`；无这些资源时移除对应控件及调用，不放失效按钮。

## 制作顺序

1. `extract_reference.py`：原图蒙版拆件、坐标、皮肤补层与基础layout。
2. `prepare_eyes.py`：独立左右眼遮罩/闭眼线/皮肤。
3. `prepare_mouth.py`：嘴部皮肤、口腔、上下唇。
4. `prepare_expression_hair.py`：眉部补底及发束分组。
5. `build_moc.py`：MOC3、图集、清单、表情、物理、导出待机。
6. `compare_neutral.py`：作者侧中性拼合对比；还需Core实际画面对比。
7. `validate.cjs`：Web Core结构/绑定验证；网页播放作视觉检查。
8. 素材更改后运行`export_psd.py`，最终整理和打包。

`rebuild.py`按上述前五步运行，最后调用`validate_native.py`；运行前通过CUBISM_CORE_LIBRARY指定自己的Core动态库，或改用Web Core验证，不要因为没有VTS就伪造通过结果。原生加载器的内存对齐不可随意去除。

## 迁移前必须适配

这些代码不是通用分割模型。按新角色审查并改写：画布原点/尺寸、颜色阈值、多边形坐标、眼睑曲线、嘴的区间、局部补绘区域、颈部锚点、头部深度近似、发束根梢范围、图集布局、部件名及绘制顺序。不要只替换Reference.png就直接运行。

`export_psd.py`从当前Python环境导入依赖，请在项目虚拟环境安装psd-tools。psd-tools私有_record写入方式针对当时环境验证；迁移版本后重新打开PSD验证。

`index.html/preview.js`保持案例原图/旧图对比、滑块和自然演示；适配新尺寸时同步修改fit计算及参考图显示。`package.py`是原项目的宽泛打包脚本，新项目应改为必要文件白名单。

## 已知范围

案例1086×1448、23网格、14参数、4096图集。源图有限分辨率不是巨幅精绘。保留原眼神但尚未拆出可自由移动的虹膜；`ParamEyeBallX`存在不代表凝视功能已经实现。支持小角度转脸及音量嘴型，不含完整侧面或音素口型；没有cmo3编辑工程。前期VTS曾出现加载失败，后来用户报告可用；最新修改只复查网页/Core，不能声称最新包在VTS已重新验收。
