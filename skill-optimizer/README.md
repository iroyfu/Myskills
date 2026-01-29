# Skill Optimizer

自动检测用户对skill结果的纠正，并基于上下文分析优化有异议的skill。

## 功能

这个skill能够：

1. **检测纠正信号** - 识别用户消息中的纠正模式
2. **分析问题根源** - 理解skill为什么产生了错误输出
3. **生成优化方案** - 提供针对性的改进建议
4. **持续改进** - 追踪重复出现的纠正模式

## 使用场景

当出现以下情况时，这个skill会自动触发：

- 用户明确纠正："不对"、"错了"、"这不是我想要的"
- 用户表达不满："这不匹配我的要求"
- 用户重新表述请求
- 用户建议替代方案

## 工作流程

```
用户纠正 → 检测模式 → 分析原skill → 生成优化 → 展示改进 → 确认应用
```

## 辅助脚本

### analyze_correction.py

用于分析用户消息中的纠正模式：

```bash
# 分析单条消息
python scripts/analyze_correction.py "不，这不是我想要的，我需要X而不是Y"

# 分析对话文件
python scripts/analyze_correction.py --file conversation.json

# 交互式输入
python scripts/analyze_correction.py
```

输出示例：
```
Correction #1
============================================================
## Detected Correction (Severity: high)

**User Message:** 不，这不是我想要的，我需要X而不是Y

**Patterns Found:** explicit_denial, correction_marker

**Clarification:** 我需要X而不是Y

**Suggested Actions:**
  1. Analyze what was denied and identify the root cause
  2. Extract the clarification and compare with original interpretation
```

## 目录结构

```
skill-optimizer/
├── SKILL.md           # 主要skill定义
├── LICENSE.txt        # MIT许可证
├── README.md          # 使用说明
└── scripts/
    └── analyze_correction.py  # 纠正分析脚本
```

## 集成方式

这个skill会自动在对话中检测用户纠正。当检测到纠正时：

1. 分析最近的用户纠正消息
2. 识别涉及的skill
3. 生成优化建议
4. 等待用户确认后应用更改

## 常见纠正模式

| 类型 | 示例 | 优化方向 |
|------|------|----------|
| 缺少上下文 | "你没考虑到X" | 添加检查X的指令 |
| 错误理解 | "我是指Y，不是X" | 澄清解释规则 |
| 输出不完整 | "缺少Z" | 添加包含Z的步骤 |
| 流程错误 | "应该先A再B" | 调整工作流顺序 |
| 格式问题 | "用[格式]格式" | 更新输出格式规范 |

## 许可证

MIT License