#!/usr/bin/env python3
"""
Skill Correction Analyzer

This script helps analyze conversation patterns to identify user corrections
and generates structured feedback for skill optimization.
"""

import re
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class CorrectionPattern:
    """Represents a detected correction pattern."""
    pattern_type: str
    trigger_phrases: List[str]
    severity: str  # low, medium, high
    suggested_action: str


# Common correction patterns
CORRECTION_PATTERNS = [
    CorrectionPattern(
        pattern_type="explicit_denial",
        trigger_phrases=[
            r"\bno\b",
            r"\bwrong\b",
            r"\bincorrect\b",
            r"\bnot what (?:i|i') wanted\b",
            r"\bthat('?s)? not right\b",
            r"\bthis is incorrect\b",
        ],
        severity="high",
        suggested_action="Analyze what was denied and identify the root cause"
    ),
    CorrectionPattern(
        pattern_type="correction_marker",
        trigger_phrases=[
            r"\bactually\b",
            r"\bwait\b",
            r"\blet me clarify\b",
            r"\bi (?:mean|meant)\b",
            r"\bto be clear\b",
            r"\bwhat i (?:really|actually) want\b",
        ],
        severity="medium",
        suggested_action="Extract the clarification and compare with original interpretation"
    ),
    CorrectionPattern(
        pattern_type="dissatisfaction",
        trigger_phrases=[
            r"\bthis doesn'?t match\b",
            r"\bthis is not (?:what|how)\b",
            r"\bi (?:don'?t|do not) like\b",
            r"\bthis (?:isn'?t|is not) (?:good|right|correct)\b",
            r"\btry again\b",
            r"\bthat'?s not it\b",
        ],
        severity="medium",
        suggested_action="Identify the gap between expected and actual output"
    ),
    CorrectionPattern(
        pattern_type="alternative_approach",
        trigger_phrases=[
            r"\binstead\b",
            r"\brather than\b",
            r"\buse (?:a different|another)\b",
            r"\btry (?:using|doing)\b",
            r"\bmaybe\b",
        ],
        severity="low",
        suggested_action="Consider the alternative as a constraint for future iterations"
    ),
]


@dataclass
class DetectedCorrection:
    """Represents a detected user correction."""
    message: str
    patterns_found: List[str]
    severity: str
    suggested_actions: List[str]
    extracted_clarification: Optional[str]


class CorrectionAnalyzer:
    """Analyzes user messages for correction patterns."""

    def __init__(self):
        self.patterns = CORRECTION_PATTERNS

    def analyze_message(self, message: str) -> Optional[DetectedCorrection]:
        """Analyze a single message for correction patterns."""
        message_lower = message.lower()
        patterns_found = []
        severities = []
        suggested_actions = []

        for pattern in self.patterns:
            for trigger in pattern.trigger_phrases:
                if re.search(trigger, message_lower):
                    patterns_found.append(pattern.pattern_type)
                    severities.append(pattern.severity)
                    suggested_actions.append(pattern.suggested_action)
                    break

        if not patterns_found:
            return None

        # Determine overall severity
        severity = "high" if "high" in severities else ("medium" if "medium" in severities else "low")

        # Extract clarification if present
        clarification = self._extract_clarification(message)

        return DetectedCorrection(
            message=message,
            patterns_found=patterns_found,
            severity=severity,
            suggested_actions=suggested_actions,
            extracted_clarification=clarification,
        )

    def _extract_clarification(self, message: str) -> Optional[str]:
        """Extract the user's clarification from the message."""
        # Look for common clarification patterns
        clarification_patterns = [
            r"(?:i (?:mean|meant))\s+(.+?)(?:\.|$)",
            r"(?:actually)\s+(.+?)(?:\.|$)",
            r"(?:to be clear)[,:\s]+(.+?)(?:\.|$)",
            r"(?:what i (?:really|actually) want)[,:\s]+(.+?)(?:\.|$)",
        ]

        for pattern in clarification_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def analyze_conversation(self, messages: List[Dict]) -> List[DetectedCorrection]:
        """Analyze a conversation for correction patterns."""
        corrections = []

        for msg in messages:
            if msg.get("role") == "user":
                correction = self.analyze_message(msg.get("content", ""))
                if correction:
                    corrections.append(correction)

        return corrections


def format_correction_report(correction: DetectedCorrection) -> str:
    """Format a detected correction for display."""
    report = []
    report.append(f"## Detected Correction (Severity: {correction.severity})")
    report.append(f"\n**User Message:** {correction.message}")
    report.append(f"\n**Patterns Found:** {', '.join(correction.patterns_found)}")

    if correction.extracted_clarification:
        report.append(f"\n**Clarification:** {correction.extracted_clarification}")

    report.append("\n**Suggested Actions:**")
    for i, action in enumerate(correction.suggested_actions, 1):
        report.append(f"  {i}. {action}")

    return "\n".join(report)


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze conversation for user correction patterns"
    )
    parser.add_argument(
        "message",
        nargs="?",
        help="A single user message to analyze"
    )
    parser.add_argument(
        "--file",
        help="Path to a JSON file containing conversation messages"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )

    args = parser.parse_args()

    analyzer = CorrectionAnalyzer()

    if args.file:
        # Analyze conversation from file
        with open(args.file, "r", encoding="utf-8") as f:
            messages = json.load(f)
        corrections = analyzer.analyze_conversation(messages)
    elif args.message:
        # Analyze single message
        correction = analyzer.analyze_message(args.message)
        corrections = [correction] if correction else []
    else:
        # Interactive mode
        print("Enter user messages (one per line, empty line to finish):")
        messages = []
        while True:
            line = input("> ")
            if not line.strip():
                break
            messages.append({"role": "user", "content": line})
        corrections = analyzer.analyze_conversation(messages)

    if not corrections:
        print("No correction patterns detected.")
        return

    if args.json:
        output = [asdict(c) for c in corrections]
        print(json.dumps(output, indent=2))
    else:
        for i, correction in enumerate(corrections, 1):
            print(f"\n{'='*60}")
            print(f"Correction #{i}")
            print('='*60)
            print(format_correction_report(correction))


if __name__ == "__main__":
    main()