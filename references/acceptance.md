# 验收证据契约

使用 PASS / WARN / FAIL / NOT_TESTED / NOT_IMPLEMENTED。报告以下全部项目：STATIC_FIDELITY、CORE_LOAD、PARAMETER_BINDING、BLINK、EYE_TRACKING、MOUTH、HEAD、BODY、HAIR、RABBIT_EARS、TWIN_TAILS、SLEEVES、ACCESSORIES、PHYSICS、BROWSER_RUNTIME、VTS_RUNTIME。不存在的部件标 NOT_IMPLEMENTED 并说明不适用，不影响本来没有这些部件的角色。

qa/review.json 格式：

```json
{
  "schema_version": 1,
  "target": "vts",
  "required": ["STATIC_FIDELITY", "CORE_LOAD", "PARAMETER_BINDING", "BLINK", "EYE_TRACKING", "MOUTH", "HEAD", "BODY", "PHYSICS", "BROWSER_RUNTIME", "VTS_RUNTIME"],
  "package_sha256": {"Character.model3.json": "actual digest"},
  "checks": {
    "CORE_LOAD": {
      "status": "PASS", "scope": "native Core version ...",
      "reviewer": "actual reviewer", "reviewed_at": "ISO timestamp",
      "evidence": ["core-load.json"], "notes": "actual findings"
    }
  }
}
```

证据路径相对 review.json，文件必须存在；截图、视频、日志应对应当前构建。可以由同一段录像覆盖多个检查，但写清时间段与具体发现。截图存在不自动证明 PASS，执行者必须实际查看。reviewer 区分助手与用户，不伪造用户确认。

VTS_RUNTIME PASS 必须覆盖实际应用加载、贴图、映射、导出物理、构图、所实现表情与五分钟真人追踪。记录开始/结束、追踪信心/帧率、快速头 XYZ、连续眨眼/单眼、凝视、说话/笑说、表达切换、急停耳尾衰减以及错误日志。只测加载时写 WARN，scope="application load only"。未实现的命名表情独立列出，不用空 exp3 占位。

可恢复阶段门禁：静态未通过不继续 rig；Core 未通过不继续动画；参数未绑定不评运动；任何视觉故障先中性复位。验收范围必须与所用运行时一致。

release_gate.py 只对声明和文件哈希做机械检查；不会分析图片、验证报告真实性或替代真人测试。所有 required PASS 且证据/哈希有效才输出 PRODUCTION_READY；Browser PASS 但 VTS 未 PASS 时输出 BROWSER_VALIDATED_VTS_UNVERIFIED；有 FAIL 为 NEEDS_FIXES。仅浏览器目标输出 BROWSER_VALIDATED，不宣称 VTS 成品。
