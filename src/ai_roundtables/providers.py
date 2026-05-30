from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib import error, request

from .models import ParticipantConfig


@dataclass(slots=True)
class ProviderResponse:
    text: str
    status: str


class ProviderAdapter:
    def generate(self, participant: ParticipantConfig, prompt: str) -> ProviderResponse:
        raise NotImplementedError


class PlaceholderProviderAdapter(ProviderAdapter):
    def __init__(self, provider: str, env_var: str | None) -> None:
        self.provider = provider
        self.env_var = env_var

    def generate(self, participant: ParticipantConfig, prompt: str) -> ProviderResponse:
        if self.env_var and not os.getenv(self.env_var):
            return ProviderResponse(
                (
                    f"[Skipped: no {self.env_var} found. This participant remains "
                    "a placeholder until that provider is configured.]"
                ),
                "skipped_missing_key",
            )
        return ProviderResponse(
            f"[Skipped: provider '{participant.provider}' is not wired into the orchestrator yet.]",
            "skipped_unimplemented_provider",
        )


class OpenAIResponsesAdapter(ProviderAdapter):
    def generate(self, participant: ParticipantConfig, prompt: str) -> ProviderResponse:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return ProviderResponse(
                "[Skipped: no OPENAI_API_KEY found. Add it to the environment or a local .env file to run OpenAI-backed participants.]",
                "skipped_missing_key",
            )

        payload = {
            "model": participant.model,
            "instructions": (
                "You are writing one turn in an AI roundtable transcript. "
                "Stay in role, stay readable for an intelligent lay audience, "
                "and do not output speaker labels or markdown headings."
            ),
            "input": prompt,
        }
        api_request = request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(api_request, timeout=120) as response:
                response_json = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            return ProviderResponse(
                f"[OpenAI request failed with HTTP {exc.code}. Details: {detail}]",
                "error_http",
            )
        except error.URLError as exc:
            return ProviderResponse(
                f"[OpenAI request failed before a response was received: {exc.reason}]",
                "error_network",
            )

        text = extract_openai_text(response_json)
        if not text:
            return ProviderResponse(
                "[OpenAI returned a response payload, but no text could be extracted.]",
                "error_empty_response",
            )
        return ProviderResponse(text, "completed")


def provider_adapter_for(provider: str) -> ProviderAdapter:
    if provider == "openai":
        return OpenAIResponsesAdapter()
    return PlaceholderProviderAdapter(provider=provider, env_var=provider_env_var(provider))


def provider_env_var(provider: str) -> str | None:
    return {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "google": "GEMINI_API_KEY",
    }.get(provider)


def extract_openai_text(response_json: dict) -> str:
    output_text = response_json.get("output_text")
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    fragments: list[str] = []
    for item in response_json.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text" and content.get("text"):
                fragments.append(content["text"])
    return "\n\n".join(fragment.strip() for fragment in fragments if fragment.strip())
