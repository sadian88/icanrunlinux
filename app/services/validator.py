from __future__ import annotations

import html
import re

from app.config import HARDWARE_KEYWORDS

INJECTION_PATTERNS = [
    r"<\s*script[^>]*>",
    r"<\s*/\s*script\s*>",
    r"on\w+\s*=",
    r"javascript\s*:",
    r"<[^>]+on\w+\b[^>]*>",
    r"<\s*iframe[^>]*>",
    r"union\s+select",
    r"'\s*or\s+'1'\s*=\s*'1",
    r"drop\s+table",
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+(all\s+)?(prior|above)\s+instructions",
    r"(system\s*prompt|override\s*prompt)",
    r"(disregard|forget)\s+(all\s+)?previous",
    r"you\s+are\s+now\s+(a|an)",
    r"dan\s+(mode|prompt)",
    r"pretend\s+you\s+are",
]


def sanitize_input(text: str) -> str:
    text = html.escape(text, quote=False)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = text.strip()
    return text


def detect_injection(text: str) -> bool:
    text_lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def validate_hardware_query(text: str) -> tuple[bool, str]:
    if not text or not text.strip():
        return False, "Input must not be empty."

    sanitized = sanitize_input(text)

    if len(sanitized) < 10:
        return False, "Input too short. Please describe your PC specs (min 10 characters)."

    if len(sanitized) > 1000:
        return False, "Input too long. Max 1000 characters."

    if detect_injection(sanitized):
        return False, "Invalid input detected. Please describe your hardware specifications only."

    text_lower = sanitized.lower()
    match_count = 0
    for kw in HARDWARE_KEYWORDS:
        if kw in text_lower:
            match_count += 1
            if match_count >= 2:
                break

    if match_count < 2:
        return False, (
            "Input must describe a computer's hardware. Please include specs like RAM, CPU, GPU, storage, etc."
        )

    return True, sanitized
