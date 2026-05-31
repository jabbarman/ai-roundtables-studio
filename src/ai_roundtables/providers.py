from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.parse import quote
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
            "instructions": provider_instructions(),
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


class AnthropicMessagesAdapter(ProviderAdapter):
    def generate(self, participant: ParticipantConfig, prompt: str) -> ProviderResponse:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return ProviderResponse(
                "[Skipped: no ANTHROPIC_API_KEY found. Add it to the environment or a local .env file to run Anthropic-backed participants.]",
                "skipped_missing_key",
            )

        payload = {
            "model": participant.model,
            "max_tokens": 512,
            "system": provider_instructions(),
            "messages": [{"role": "user", "content": prompt}],
        }
        if participant.temperature is not None:
            payload["temperature"] = participant.temperature

        api_request = request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
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
                f"[Anthropic request failed with HTTP {exc.code}. Details: {detail}]",
                "error_http",
            )
        except error.URLError as exc:
            return ProviderResponse(
                f"[Anthropic request failed before a response was received: {exc.reason}]",
                "error_network",
            )

        text = extract_anthropic_text(response_json)
        if not text:
            return ProviderResponse(
                "[Anthropic returned a response payload, but no text could be extracted.]",
                "error_empty_response",
            )
        return ProviderResponse(text, "completed")


class GeminiGenerateContentAdapter(ProviderAdapter):
    def generate(self, participant: ParticipantConfig, prompt: str) -> ProviderResponse:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return ProviderResponse(
                "[Skipped: no GEMINI_API_KEY found. Add it to the environment or a local .env file to run Gemini-backed participants.]",
                "skipped_missing_key",
            )

        generation_config = {"maxOutputTokens": 2048}
        if participant.temperature is not None:
            generation_config["temperature"] = participant.temperature
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": f"{provider_instructions()}\n\n{prompt}",
                        }
                    ],
                }
            ],
            "generationConfig": generation_config,
        }
        model = participant.model.removeprefix("models/")
        api_request = request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{quote(model, safe='')}:generateContent",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-goog-api-key": api_key,
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
                f"[Gemini request failed with HTTP {exc.code}. Details: {detail}]",
                "error_http",
            )
        except error.URLError as exc:
            return ProviderResponse(
                f"[Gemini request failed before a response was received: {exc.reason}]",
                "error_network",
            )

        text = extract_gemini_text(response_json)
        if not text:
            return ProviderResponse(
                "[Gemini returned a response payload, but no text could be extracted.]",
                "error_empty_response",
            )
        return ProviderResponse(text, "completed")


def provider_adapter_for(provider: str) -> ProviderAdapter:
    if provider == "openai":
        return OpenAIResponsesAdapter()
    if provider == "anthropic":
        return AnthropicMessagesAdapter()
    if provider == "google":
        return GeminiGenerateContentAdapter()
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


def extract_anthropic_text(response_json: dict) -> str:
    fragments = []
    for item in response_json.get("content", []):
        if item.get("type") == "text" and item.get("text"):
            fragments.append(item["text"])
    return "\n\n".join(fragment.strip() for fragment in fragments if fragment.strip())


def extract_gemini_text(response_json: dict) -> str:
    fragments = []
    for candidate in response_json.get("candidates", []):
        content = candidate.get("content", {})
        for part in content.get("parts", []):
            if part.get("text"):
                fragments.append(part["text"])
    return "\n\n".join(fragment.strip() for fragment in fragments if fragment.strip())


def provider_instructions() -> str:
    return (
        "You are writing one turn in an AI roundtable transcript. "
        "Stay in role, stay readable for an intelligent lay audience, "
        "and do not output speaker labels or markdown headings."
    )
