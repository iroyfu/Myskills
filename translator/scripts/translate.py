#!/usr/bin/env python3
"""
Professional Translation Script
Four-stage workflow: Model B analyzes semantics, Model A translates, Model B polishes, Model A checks.
"""

import json
import re
import sys
from pathlib import Path
import requests


def load_config():
    """Load API configuration from config.json"""
    config_path = Path(__file__).parent.parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_language(text: str) -> str:
    """Detect if text contains Chinese characters."""
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]')
    return "chinese" if chinese_pattern.search(text) else "other"


def parse_target_language(text: str) -> str | None:
    """Parse target language from user input."""
    patterns = [
        r'翻译为\s*([^\s]+)',
        r'translate\s+to\s+([^\s]+)',
        r'翻译成\s*([^\s]+)',
        r'translate\s+into\s+([^\s]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip('。！？.!?')
    return None


def filter_punctuation(text: str, target_lang: str) -> str:
    """Filter punctuation when translating to Chinese."""
    if target_lang.lower() == "chinese" or target_lang.lower() == "中文":
        text = text.replace('.', '。').replace(',', '，')
        text = text.replace('!', '！').replace('?', '？')
        text = text.replace(':', '：').replace(';', '；')
    return text


def call_model(config: dict, prompt: str, model_key: str = "model_a") -> str:
    """Call OpenAI-compatible API."""
    model_config = config[model_key]
    headers = {
        "Authorization": f"Bearer {model_config['api_key']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_config['model_name'],
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(
        f"{model_config['base_url']}/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )
    if response.status_code != 200:
        raise Exception(f"API call failed: {response.status_code} - {response.text}")
    return response.json()["choices"][0]["message"]["content"]


def extract_text_to_translate(text: str, target_lang: str | None) -> tuple[str, str]:
    """Extract the actual text to translate."""
    patterns = [
        r'翻译为[^\s]*[：:]\s*',
        r'translate\s+to\s+[^\s]*[：:]\s*',
        r'翻译成[^\s]*[：:]\s*',
        r'translate\s+into\s+[^\s]*[：:]\s*',
        r'请翻译[：:]\s*',
        r'翻译[：:]\s*',
        r'Translate[：:]\s*',
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return text.strip(), "English" if target_lang is None else target_lang


def translate(text: str, verbose: bool = False) -> str:
    """
    Four-stage translation workflow.
    """
    config = load_config()
    source_lang = detect_language(text)
    target_lang = parse_target_language(text)
    text_to_translate, final_target_lang = extract_text_to_translate(text, target_lang)

    if source_lang == "chinese" and target_lang is None:
        final_target_lang = "English"
    elif source_lang == "other":
        final_target_lang = "Chinese"

    source_lang_name = "Chinese" if source_lang == "chinese" else source_lang

    if verbose:
        print(f"\n[Info] Source: {source_lang_name} -> Target: {final_target_lang}")
        print(f"[Info] Text: {text_to_translate}")

    # Stage 0: Analyze semantics (Model B)
    if verbose:
        print(f"\n[Stage 0] Semantic Analysis (Model B)")

    analysis_prompt = (
        f"Analyze the following text in {source_lang_name}. Provide:\n"
        f"1. Core meaning\n"
        f"2. Key phrases\n"
        f"3. Context/tone\n"
        f"4. Translation suggestions for {final_target_lang}\n\n"
        f"Text: {text_to_translate}"
    )

    try:
        semantic_context = call_model(config, analysis_prompt, "model_b")
        if verbose:
            print(f"  Analysis: {semantic_context[:150]}...")
    except Exception as e:
        if verbose:
            print(f"  Analysis failed, using direct translation: {e}")
        semantic_context = ""

    # Stage 1: Initial Translation (Model A)
    if verbose:
        print(f"\n[Stage 1] Initial Translation (Model A)")

    translation_prompt = (
        f"Translate from {source_lang_name} to {final_target_lang}."
        if not semantic_context else
        f"Translate from {source_lang_name} to {final_target_lang}. "
        f"Consider this semantic context for better accuracy:\n{semantic_context}\n\n"
        f"Text: {text_to_translate}"
    )
    translation_prompt += " Output ONLY the translated text, no explanations."

    try:
        stage1_result = call_model(config, translation_prompt, "model_a")
        stage1_result = filter_punctuation(stage1_result, final_target_lang)
        if verbose:
            print(f"  Result: {stage1_result}")
    except Exception as e:
        return f"Translation failed: {e}"

    # Stage 2: Evaluate from American colloquial perspective (Model B)
    if verbose:
        print(f"\n[Stage 2] American Colloquial Evaluation (Model B)")

    evaluation_prompt = (
        f"Evaluate the following translation from American colloquial English perspective. "
        f"Provide assessment on:\n"
        f"1. Naturalness and fluency\n"
        f"2. Idiomatic expressions (if target is English)\n"
        f"3. Cultural appropriateness\n"
        f"4. Specific suggestions for improvement\n\n"
        f"Focus on whether it sounds like what an average American would say in daily conversation.\n\n"
        f"Original text [{source_lang_name}]: {text_to_translate}\n"
        f"Translation [{final_target_lang}]: {stage1_result}\n\n"
        f"Output your evaluation and suggestions clearly."
    )

    try:
        evaluation_result = call_model(config, evaluation_prompt, "model_b")
        if verbose:
            print(f"  Evaluation: {evaluation_result[:150]}...")
    except Exception as e:
        if verbose:
            print(f"  Evaluation failed, using stage 1: {e}")
        return stage1_result

    # Stage 3: Final revision based on evaluation (Model A)
    if verbose:
        print(f"\n[Stage 3] Final Revision based on Evaluation (Model A)")

    revision_prompt = (
        f"Based on the following evaluation and suggestions, revise the translation. "
        f"Make it more natural, idiomatic, and culturally appropriate from American perspective. "
        f"Output ONLY the final revised translation.\n\n"
        f"Original text [{source_lang_name}]: {text_to_translate}\n"
        f"Translation [{final_target_lang}]: {stage1_result}\n"
        f"Evaluation and suggestions:\n{evaluation_result}\n\n"
        f"Final revised translation:"
    )

    try:
        final_result = call_model(config, revision_prompt, "model_a")
        final_result = filter_punctuation(final_result, final_target_lang)
        if verbose:
            print(f"  Result: {final_result}\n[Final] Complete")
    except Exception as e:
        if verbose:
            print(f"  Revision failed, using stage 1: {e}")
        return stage1_result

    return final_result


def main():
    if len(sys.argv) < 2:
        print("Usage: python translate.py \"<text>\" [--verbose]")
        sys.exit(1)
    text = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv

    # Extract clean text for display
    source_lang = detect_language(text)
    target_lang = parse_target_language(text)
    text_to_translate, final_target_lang = extract_text_to_translate(text, target_lang)

    if source_lang == "chinese" and target_lang is None:
        final_target_lang = "English"
    elif source_lang == "other":
        final_target_lang = "Chinese"

    result = translate(text, verbose)

    # Format output: left original, right translation
    print()
    print(f"原文  →  译文")
    print(f"{text_to_translate}  →  {result}")


if __name__ == "__main__":
    main()
