from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from urllib.parse import quote
from urllib import error, request

from .models import ParticipantConfig

RETRYABLE_HTTP_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
RETRY_DELAYS_SECONDS = (1.0, 2.0, 4.0, 8.0)


@dataclass(slots=True)
class ProviderResponse:
    text: str
    status: str


class ProviderAdapter:
    def generate(self, participant: ParticipantConfig, prompt: str) -> ProviderResponse:
        raise NotImplementedError


def request_json(
    api_request: request.Request,
    provider_name: str,
    timeout: int = 120,
) -> tuple[dict | None, ProviderResponse | None]:
    for attempt in range(len(RETRY_DELAYS_SECONDS) + 1):
        try:
            with request.urlopen(api_request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8")), None
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if (
                exc.code in RETRYABLE_HTTP_STATUS_CODES
                and attempt < len(RETRY_DELAYS_SECONDS)
            ):
                time.sleep(RETRY_DELAYS_SECONDS[attempt])
                continue
            return None, ProviderResponse(
                f"[{provider_name} request failed with HTTP {exc.code}. "
                f"Details: {detail}]",
                "error_http",
            )
        except error.URLError as exc:
            return None, ProviderResponse(
                f"[{provider_name} request failed before a response was received: "
                f"{exc.reason}]",
                "error_network",
            )

    raise AssertionError("Provider retry loop exited unexpectedly")


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
            "max_output_tokens": participant.output_tokens or 512,
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
        response_json, request_error = request_json(api_request, "OpenAI")
        if request_error:
            return request_error

        assert response_json is not None
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
            "max_tokens": participant.output_tokens or 512,
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
        response_json, request_error = request_json(api_request, "Anthropic")
        if request_error:
            return request_error

        assert response_json is not None
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

        generation_config = {
            "maxOutputTokens": participant.output_tokens or 2048,
            "thinkingConfig": {
                "thinkingBudget": participant.thinking_tokens
                if participant.thinking_tokens is not None
                else 512
            },
        }
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
        response_json, request_error = request_json(api_request, "Gemini")
        if request_error:
            return request_error

        assert response_json is not None
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
