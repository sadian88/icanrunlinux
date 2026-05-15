import json

import httpx

from app.config import LLM_API_KEY, LLM_API_URL, LLM_MODEL


SYSTEM_PROMPT = """You are an expert Linux distribution recommender with deep technical knowledge.

Based on the user's hardware specs and use-case description, recommend the BEST existing Linux distributions.

Return ONLY a valid JSON object with this exact structure (no markdown, no explanations outside JSON):

{
  "distros": [
    {
      "name": "Ubuntu",
      "slug": "ubuntu",
      "description": "A beginner-friendly Debian-based distro with great community support.",
      "based_on": ["Debian"],
      "origin": "Isle of Man",
      "architectures": ["x86_64", "aarch64"],
      "desktop": ["GNOME"],
      "category": ["Desktop", "Beginners"],
      "difficulty": 1,
      "min_ram_gb": 4,
      "min_storage_gb": 25,
      "use_cases": ["desktop", "development"],
      "recommended_for": ["beginners", "desktop", "development"],
      "package_manager": "apt",
      "init_system": "systemd",
      "release_model": "LTS / 6-month cycle",
      "technical_notes": "Uses apt/deb packages, systemd init. Strong NVIDIA driver support via third-party repos. Large community with extensive documentation. Snaps are integrated but can be removed.",
      "why": "Excellent hardware detection out of the box, extensive package availability, and strong community support make it ideal for this configuration."
    }
  ]
}

Rules:
- Recommend ONLY real, well-known distributions that actually exist.
- The "why" field must explain SPECIFICALLY why this distro fits the user's hardware and use-case with TECHNICAL reasoning (driver support, memory usage, init system, package manager, release model).
- "technical_notes" should briefly describe technical characteristics: package manager, init system, driver/NVIDIA support, kernel version policy, desktop compositor, filesystem defaults.
- "package_manager" should be the primary package manager (apt, pacman, dnf, zypper, etc).
- "init_system" should be the init system (systemd, openrc, runit, s6, etc).
- "release_model" should describe the release type (rolling, LTS, fixed, semi-rolling).
- difficulty is 1 (beginner) to 5 (expert).
- Keep descriptions concise (1-2 sentences).
- Return up to the requested limit of distros, sorted by relevance.
"""


def call_llm(user_query: str, limit: int = 10) -> list[dict]:
    """Ask DeepSeek (via OpenRouter) for distro recommendations.

    Returns a list of distro dicts parsed from the JSON response.
    """
    user_prompt = (
        f"User request: {user_query}\n\n"
        f"Please recommend up to {limit} Linux distributions. "
        f"Return ONLY the JSON object described in your instructions."
    )

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://icanrunlinux.local",
        "X-Title": "I Can Run Linux",
    }

    payload = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 2048,
        "response_format": {"type": "json_object"},
    }

    resp = httpx.post(LLM_API_URL, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    content = data["choices"][0]["message"]["content"]
    parsed = json.loads(content)
    return parsed.get("distros", [])
