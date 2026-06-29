"""
Provider-agnostic LLM client.

Pick a provider with the LLM_PROVIDER env var (openai | anthropic | gemini).
Set the matching API key. If none is configured, the app still works fully via
the deterministic narrative in narrative.py.

    LLM_PROVIDER=anthropic   ANTHROPIC_API_KEY=...   (ANTHROPIC_MODEL optional)
    LLM_PROVIDER=openai      OPENAI_API_KEY=...      (OPENAI_MODEL optional)
    LLM_PROVIDER=gemini      GOOGLE_API_KEY=...      (GEMINI_MODEL optional)

SDKs are imported lazily so you only need the one you use.
"""
from __future__ import annotations

import os

SUPPORTED = {"openai", "anthropic", "gemini", "google"}


def provider() -> str | None:
    p = os.getenv("LLM_PROVIDER", "").strip().lower()
    return p or None


def is_configured() -> bool:
    p = provider()
    if p not in SUPPORTED:
        return False
    if p == "openai":
        return bool(os.getenv("OPENAI_API_KEY"))
    if p == "anthropic":
        return bool(os.getenv("ANTHROPIC_API_KEY"))
    if p in ("gemini", "google"):
        return bool(os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    return False


def status() -> str:
    p = provider()
    if not p:
        return "No LLM provider set (deterministic mode)."
    if not is_configured():
        return f"Provider '{p}' selected but API key missing."
    return f"LLM provider: {p} (ready)."


def complete(system: str, prompt: str, *, max_tokens: int = 1200,
             temperature: float = 0.2) -> str:
    """Dispatch a single completion to the configured provider."""
    p = provider()
    if not is_configured():
        raise RuntimeError(status())

    if p == "openai":
        from openai import OpenAI

        client = OpenAI()
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return resp.choices[0].message.content.strip()

    if p == "anthropic":
        import anthropic

        client = anthropic.Anthropic()
        msg = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in msg.content
                       if getattr(block, "type", None) == "text").strip()

    if p in ("gemini", "google"):
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY")
                        or os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel(
            os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            system_instruction=system,
        )
        resp = model.generate_content(
            prompt,
            generation_config={"temperature": temperature,
                               "max_output_tokens": max_tokens},
        )
        return resp.text.strip()

    raise RuntimeError(f"Unsupported provider: {p}")
