from __future__ import annotations

from io import BytesIO
import json
from urllib.error import HTTPError

from ai_roundtables.models import ParticipantConfig
from ai_roundtables.providers import (
    AnthropicMessagesAdapter,
    GeminiGenerateContentAdapter,
    OpenAIResponsesAdapter,
    PlaceholderProviderAdapter,
    extract_anthropic_text,
    extract_gemini_text,
    extract_openai_text,
    provider_adapter_for,
)


def participant(
    provider: str = "openai",
    output_tokens: int | None = None,
    thinking_tokens: int | None = None,
) -> ParticipantConfig:
    return ParticipantConfig(
        name="Test",
        provider=provider,
        model="test-model",
        prompt_file="prompts/participant.md",
        stance="Test stance.",
        output_tokens=output_tokens,
        thinking_tokens=thinking_tokens,
    )


def header_value(api_request, header_name: str) -> str | None:
    for key, value in api_request.headers.items():
        if key.lower() == header_name.lower():
            return value
    return None


def test_extract_openai_text_supports_known_response_shapes() -> None:
    assert extract_openai_text({"output_text": " Direct text "}) == "Direct text"
    assert (
        extract_openai_text(
            {
                "output": [
                    {
                        "type": "message",
                        "content": [
                            {"type": "output_text", "text": "First"},
                            {"type": "output_text", "text": "Second"},
                        ],
                    }
                ]
            }
        )
        == "First\n\nSecond"
    )


def test_extract_anthropic_text_supports_content_blocks() -> None:
    assert (
        extract_anthropic_text(
            {
                "content": [
                    {"type": "text", "text": "First"},
                    {"type": "text", "text": "Second"},
                ]
            }
        )
        == "First\n\nSecond"
    )


def test_extract_gemini_text_supports_candidate_parts() -> None:
    assert (
        extract_gemini_text(
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {"text": "First"},
                                {"text": "Second"},
                            ]
                        }
                    }
                ]
            }
        )
        == "First\n\nSecond"
    )


def test_placeholder_provider_reports_unimplemented() -> None:
    adapter = PlaceholderProviderAdapter("other", None)

    response = adapter.generate(participant("other"), "Prompt")

    assert response.status == "skipped_unimplemented_provider"
    assert "not wired" in response.text


def test_provider_adapter_selects_provider_adapters() -> None:
    assert isinstance(provider_adapter_for("openai"), OpenAIResponsesAdapter)
    assert isinstance(provider_adapter_for("anthropic"), AnthropicMessagesAdapter)
    assert isinstance(provider_adapter_for("google"), GeminiGenerateContentAdapter)


def test_openai_adapter_posts_to_responses_api(monkeypatch) -> None:
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return None

        def read(self) -> bytes:
            return json.dumps({"output_text": "Generated turn"}).encode("utf-8")

    def fake_urlopen(api_request, timeout):
        captured["url"] = api_request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(api_request.data.decode("utf-8"))
        captured["auth"] = api_request.headers["Authorization"]
        return FakeResponse()

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("ai_roundtables.providers.request.urlopen", fake_urlopen)

    response = OpenAIResponsesAdapter().generate(
        participant(output_tokens=768), "Prompt text"
    )

    assert response.status == "completed"
    assert response.text == "Generated turn"
    assert captured["url"] == "https://api.openai.com/v1/responses"
    assert captured["timeout"] == 120
    assert captured["body"]["input"] == "Prompt text"
    assert captured["body"]["max_output_tokens"] == 768
    assert captured["auth"] == "Bearer test-key"


def test_anthropic_adapter_posts_to_messages_api(monkeypatch) -> None:
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return None

        def read(self) -> bytes:
            return json.dumps(
                {"content": [{"type": "text", "text": "Anthropic turn"}]}
            ).encode("utf-8")

    def fake_urlopen(api_request, timeout):
        captured["url"] = api_request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(api_request.data.decode("utf-8"))
        captured["key"] = header_value(api_request, "x-api-key")
        captured["version"] = header_value(api_request, "anthropic-version")
        return FakeResponse()

    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setattr("ai_roundtables.providers.request.urlopen", fake_urlopen)

    response = AnthropicMessagesAdapter().generate(
        participant("anthropic", output_tokens=768), "Prompt text"
    )

    assert response.status == "completed"
    assert response.text == "Anthropic turn"
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    assert captured["timeout"] == 120
    assert captured["body"]["max_tokens"] == 768
    assert captured["body"]["messages"] == [{"role": "user", "content": "Prompt text"}]
    assert captured["key"] == "test-key"
    assert captured["version"] == "2023-06-01"


def test_gemini_adapter_posts_to_generate_content_api(monkeypatch) -> None:
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return None

        def read(self) -> bytes:
            return json.dumps(
                {"candidates": [{"content": {"parts": [{"text": "Gemini turn"}]}}]}
            ).encode("utf-8")

    def fake_urlopen(api_request, timeout):
        captured["url"] = api_request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(api_request.data.decode("utf-8"))
        captured["key"] = header_value(api_request, "x-goog-api-key")
        return FakeResponse()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("ai_roundtables.providers.request.urlopen", fake_urlopen)

    response = GeminiGenerateContentAdapter().generate(
        participant("google", output_tokens=768, thinking_tokens=128), "Prompt text"
    )

    assert response.status == "completed"
    assert response.text == "Gemini turn"
    assert (
        captured["url"]
        == "https://generativelanguage.googleapis.com/v1beta/models/test-model:generateContent"
    )
    assert captured["timeout"] == 120
    assert captured["body"]["generationConfig"]["maxOutputTokens"] == 768
    assert captured["body"]["generationConfig"]["thinkingConfig"] == {
        "thinkingBudget": 128
    }
    assert "Prompt text" in captured["body"]["contents"][0]["parts"][0]["text"]
    assert captured["key"] == "test-key"


def test_gemini_adapter_retries_temporary_http_errors(monkeypatch) -> None:
    attempts = 0
    delays = []

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, traceback):
            return None

        def read(self) -> bytes:
            return json.dumps(
                {"candidates": [{"content": {"parts": [{"text": "Recovered"}]}}]}
            ).encode("utf-8")

    def fake_urlopen(api_request, timeout):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise HTTPError(
                api_request.full_url,
                503,
                "Unavailable",
                {},
                BytesIO(b'{"error":{"status":"UNAVAILABLE"}}'),
            )
        return FakeResponse()

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("ai_roundtables.providers.request.urlopen", fake_urlopen)
    monkeypatch.setattr(
        "ai_roundtables.providers.time.sleep", lambda delay: delays.append(delay)
    )

    response = GeminiGenerateContentAdapter().generate(
        participant("google"), "Prompt text"
    )

    assert response.status == "completed"
    assert response.text == "Recovered"
    assert attempts == 3
    assert delays == [1.0, 2.0]


def test_gemini_adapter_does_not_retry_non_transient_http_errors(monkeypatch) -> None:
    attempts = 0

    def fake_urlopen(api_request, timeout):
        nonlocal attempts
        attempts += 1
        raise HTTPError(
            api_request.full_url,
            400,
            "Bad Request",
            {},
            BytesIO(b'{"error":{"status":"INVALID_ARGUMENT"}}'),
        )

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr("ai_roundtables.providers.request.urlopen", fake_urlopen)

    response = GeminiGenerateContentAdapter().generate(
        participant("google"), "Prompt text"
    )

    assert response.status == "error_http"
    assert "HTTP 400" in response.text
    assert attempts == 1
