---
name: prompt-reverse-engineering
description: AI图像生成提示词反向工程技能。此技能用于分析用户上传的图片和主题要求，生成结构化、高质量的AI图像生成提示词，特别强调人物面部一致性保持和主题风格化转换。
license: Complete terms in LICENSE.txt
---

# 提示词反向工程技能

本技能提供AI图像生成提示词的反向工程能力，能够分析用户图片并生成高质量的、结构化的提示词，特别适用于人物主题转换和风格化生成。

## 使用场景

当以下情况时使用本技能：
- 用户上传人物图片并希望生成特定主题/风格的AI图像
- 需要根据原图信息生成高质量的Midjourney/Stable Diffusion/DALL-E提示词
- 需要确保人物面部特征在风格转换中保持高度一致
- 需要按照结构化框架生成提示词，确保格式规范化
- 涉及生日派对、夜店迪厅、恐怖互动、情侣自拍、时尚画报等主题
- 需要融入Roy的风格的高频元素（数字气球、confetti、霓虹字等）

## 核心工作流程

### 第1步：原图分析（必须执行）
仔细分析用户上传的图片，提取以下关键信息：
- **人物基本特征**：性别、年龄段、大致发型、肤色、体型
- **当前穿着风格**：日常/休闲/正式/运动/...
- **当前表情/姿势**：表情状态、动作姿势、情绪基调
- **图片整体氛围**：明亮/暗调/室内/室外/节日感/恐怖感/...
- **现有元素**：背景、道具、灯光特点

### 第2步：主题确认
- 确认用户想要的主题/场景/风格
- 常见主题：生日庆生、夜店迪厅、恐怖互动、情侣自拍、时尚画报、迷你公仔等
- 特定风格：豹纹头盔、运动装备、高定礼服、赛博朋克等

### 第3步：生成结构化提示词
严格按照万能公式框架生成提示词，确保以下要求：
1. **保脸铁律必须开头和结尾都出现**
2. **框架开头宣言**根据主题选最匹配的一个：
   - 时尚画报类：`一副惊艳的时尚画报：`
   - 真实照片类：`A realistic / cinematic / photorealistic [shot/portrait/photo] of the person from the uploaded photo`
   - 人物保持类：`使用上传图片中的人物，按照以下要求完成任务：`
   - 迷你公仔类：`Transform the person into a miniature figurine / A vertical Polaroid photo / ...`
3. **穿着描述**：从原图穿着 → 目标主题的强烈反差升级（日常 → 闪亮/高定/主题装）
4. **其他模块**：
   - 按用户说的主题替换占位符
   - 尽可能保留Roy的风格的高频元素
   - 如果用户没说具体细节，使用默认高频组合填充

### 第4步：输出格式
- 输出完整提示词，不要解释
- 直接输出可复制的文本
- 严格遵循下方万能公式框架

## 万能公式框架（必须严格遵守）

```
Top priority: Strictly ensure the consistency of the character's facial features in the upload images. Strictly reference and restore the person in the uploaded photo, must be the exact same person, keep face shape, facial features proportion, skin tone, vibe highly consistent, do NOT stylize the face, do NOT beautify, do NOT generate a different person.

[框架开头，一句话概述整个图片]
一幅惊艳的时尚画报：
A realistic / cinematic / photorealistic [shot/portrait/photo] of the person from the uploaded photo
使用上传图片中的人物，按照以下要求完成任务：
Transform the person into a miniature figurine / A vertical Polaroid photo / ...

主角 / Subject: 上传图片中的人物 / the person from the uploaded photo

穿着 / Outfit: [日常/素人描述] → [目标风格：闪亮/高定/主题/豹纹/连体衣/sequin gown/运动装备等，越具体越好]

姿势 / Action / Pose: [具体动作 + 表情 + 互动，例如：侧卧地面双手握头盔 / blowing candles / awkward dancing / cheek-to-cheek heart hands / looking intensely at camera / emerging from torn calendar hole]

环境 / Background / Setting: [纯色 + 颜色 / 场景 + 虚化元素 / 桌面/床/镜子/舞池/电影院/豪华公寓夜景 / 玫瑰墙 / 烟雾人群]

道具 / Elements / Key Objects: [气球（数字/心形/foil） / 蛋糕+蜡烛 / confetti falling / 橄榄球头盔 / 霓虹字（HAPPY BIRTHDAY / LOVE / I LOVE YOU） / 激光光束 / 烟雾 / 亮片颗粒 / 玫瑰花束 / 香槟杯 / disco ball / 恐怖角色（Ghostface / Pennywise / Chucky）]

灯光 / Lighting: [cinematic lighting / direct flash / harsh flash / neon cyan+magenta / soft warm studio / rim light / spotlight halo / high contrast / moody / volumetric god rays]

氛围 / Mood / Vibe: [festive / celebratory / romantic / unsettling / horror-core / high-energy / immersive / playful / chaotic / dreamy / 90s thriller / cyberpunk]

[可选：滤镜 & 特效]
Filter / Effect: [cyan/blue hazy overlay / suppress red channel / grainy film / vignette / glitter particles in air / subtle motion blur on background / dewy skin + water droplets / wet look + glistening sweat]

画质 / Technical: 8k resolution, photorealistic, highly detailed, sharp focus on face, cinematic quality, film grain, high detail

严格参考并还原用户上传的照片中的人物，必须与参考图片中的人物为同一人，保持脸型、五官比例、肤色、气质高度一致，不风格化改脸，不美型，不生成不同人物。
```

## Roy的风格高频元素库

### 默认组合元素
- **道具**：数字气球、confetti、玫瑰墙、霓虹字、橄榄球头盔、Ghostface/恐怖角色
- **效果**：dewy skin（带水珠光泽）、direct flash（直闪光）、湿身look
- **画质**：8k resolution、photorealistic、highly detailed、cinematic quality

### 主题专用元素
- **生日主题**：数字气球、蛋糕+蜡烛、party hat、confetti falling
- **夜店主题**：disco ball、激光光束、霓虹色彩、烟雾、亮片颗粒
- **恐怖主题**：Ghostface、Pennywise、Chucky、血滴、阴暗环境
- **时尚主题**：豹纹图案、连体衣、高定礼服、赛博朋克元素
- **情侣主题**：玫瑰墙、霓虹字"I LOVE YOU"、爱心气球、香槟杯

## 参考文件

### 1. 主题模板库 (`references/theme-templates.md`)
提供各类主题的详细模板和推荐元素组合。

### 2. 高频元素库 (`references/frequent-elements.md`)
收集Roy的风格中的高频元素和搭配建议。

## 注意事项

1. **面部一致性是最高优先级**：开头和结尾必须重复保脸铁律
2. **结构必须完整**：确保所有模块都有内容填充
3. **语言灵活性**：根据目标AI平台使用英文或双语格式
4. **细节丰富性**：尽可能使用具体、生动的描述
5. **格式规范化**：严格遵循框架格式，便于复制粘贴使用

## 快速响应模式

当用户提供"图片+主题"组合时：
1. 立即响应"收到，正在分析图片并根据[主题]生成提示词..."
2. 执行4步工作流程
3. 输出完整提示词，不附加解释性文字
4. 确保提示词可直接复制使用