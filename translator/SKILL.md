---
name: translator
description: Three-stage translation: Model B analyzes semantics → Model A translates → Model B evaluates (American colloquial) → Model A revises based on evaluation. Supports Chinese-to-any-language (defaults to English) and any-language-to-Chinese translation.
license: MIT
---

# Translator

## Translation Rules

| Input | Default Target | With Specification |
|-------|---------------|-------------------|
| 中文 | 英文 | 指定语言 |
| 非中文 | 中文 | 忽略，始终翻译为中文 |

## Execution Workflow

When a user provides text to translate, execute the following steps:

### Step 1: Language Detection

```
Check for Chinese characters (unicode \u4e00-\u9fff):
- Contains Chinese → Source=Chinese
- No Chinese → Source=Original language
```

### Step 2: Determine Target Language

```
Parse language specification from user input (patterns: "翻译为XX", "translate to XX", "翻译成XX", "translate into XX"):
- Specified → Target=Specified language (ignore input language type)
- Not specified:
  - Source is Chinese → Target=English
  - Source is non-Chinese → Target=Chinese
```

### Step 3: Extract Text to Translate

```
Remove prefix patterns:
- "翻译为[语言]:"
- "translate to [language]:"
- "翻译成[语言]:"
- "translate into [language]:"
- "请翻译:"
- "翻译:"
- "Translate:"
Get clean text to translate
```

### Step 4: Three-Stage Translation

**Execute using `scripts/translate.py`:**

```bash
python scripts/translate.py "<text>" [--verbose]
```

**Stage 0: Semantic Analysis (Model B GLM-4.6)**
- Analyze core meaning
- Extract key phrases
- Identify context/tone
- Provide translation suggestions

**Stage 1: Translation (Model A Hunyuan-MT-7B)**
- Translate using semantic context
- Output raw translation

**Stage 2: American Colloquial Evaluation (Model B GLM-4.6)**
- Evaluate from American colloquial perspective
- Assess naturalness and fluency
- Check idiomatic expressions
- Provide specific improvement suggestions

**Stage 3: Final Revision (Model A Hunyuan-MT-7B)**
- Revise based on evaluation
- Apply cultural appropriateness
- Output final translated text

### Step 5: Return Result

```
Output final translation
(With --verbose, show all stage results)
```

## Usage Examples

| User Input | Source | Target | Output |
|------------|--------|--------|--------|
| "你好世界" | 中文 | 英文 | "Hello world" |
| "翻译为法语：谢谢" | 中文 | 法语 | "Merci" |
| "Hello world" | 英文 | 中文 | "你好世界" |
| "Translate to Chinese: Thank you" | 英文 | 中文 | "谢谢你" |

## Command Reference

```bash
# Basic translation
python scripts/translate.py "文本"

# Specify target language
python scripts/translate.py "翻译为法语：谢谢"

# Show detailed process
python scripts/translate.py "Hello" --verbose
```

## Configuration

Edit `config.json` to configure API endpoints:

```json
{
  "model_a": {"base_url": "...", "api_key": "...", "model_name": "..."},
  "model_b": {"base_url": "...", "api_key": "...", "model_name": "..."}
}
```