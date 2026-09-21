# VTS/OBS 实用交付

Windows 默认推荐 Spout2 输出：安装匹配 OBS 版本的插件；VTS 开启 Spout2；Color Picker Background 选择透明黑并启用 Transparent in capture；OBS 选择 VTubeStudioSpout，Composite mode 为 Premultiplied Alpha。它不会捕获 VTS 操作 UI。不要执行 Resize Output(source size) 改动用户直播画布。

无需插件的备选是 OBS 游戏捕获+允许透明；这不等于隐藏全部 VTS UI。不要用绿幕抠除角色同色头发。只开启实际使用的输出，关闭无用虚拟摄像头/NDI。

以游戏帧率优先时：限制 VTS 渲染 FPS（默认先 60，若支持并接受可试 30）；面捕从 30 FPS、640×480 或 720p 开始；质量等级 3 是可测试起点而不是通用最优值。小窗约 720p、无额外特效。GPU 优先级不是减少占用；不要自动更改系统优先级、驱动或隐私设置。降低物理强度不代表减轻求解成本。

VTS 缩小在 OBS 中的画面不会自动减少 VTS 的渲染工作。用同游戏场景分别记录游戏单独、游戏+VTS、游戏+VTS+OBS，比较平均/低分位 FPS、CPU/GPU 和 OBS 渲染/编码延迟。不宣称“零性能影响”。

执行时核对当前官方说明和应用菜单，版本会变化：
- https://github.com/DenchiSoft/VTubeStudio/wiki/Recording-Streaming-with-OBS
- https://github.com/DenchiSoft/VTubeStudio/wiki/Lag-Troubleshooting
- https://obsproject.com/kb/hardware-encoding

用户只询问操作时给步骤，不擅自开始直播、更改场景或开启摄像头。
