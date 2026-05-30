from __future__ import annotations

import json

from ai_roundtables.models import ParticipantConfig
from ai_roundtables.providers import (
    OpenAIResponsesAdapter,
    PlaceholderProviderAdapter,
    extract_openai_text,
    provider_adapter_for,
)


def participant(provider: str = "openai") -> ParticipantConfig:
    return ParticipantConfig(
        name="Test",
        provider=provider,
        model="test-model",
        prompt_file="prompts/participant.md",
        stance="Test stance.",
    )


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


def test_placeholder_provider_reports_missing_configured_key(monkeypatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    adapter = PlaceholderProviderAdapter("anthropic", "ANTHROPIC_API_KEY")

    response = adapter.generate(participant("anthropic"), "Prompt")

    assert response.status == "skipped_missing_key"
    assert "ANTHROPIC_API_KEY" in response.text


def test_placeholder_provider_reports_unimplemented_when_key_exists(
    monkeypatch,
) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    adapter = PlaceholderProviderAdapter("anthropic", "ANTHROPIC_API_KEY")

    response = adapter.generate(participant("anthropic"), "Prompt")

    assert response.status == "skipped_unimplemented_provider"
    assert "not wired" in response.text


def test_provider_adapter_selects_openai_adapter() -> None:
    assert isinstance(provider_adapter_for("openai"), OpenAIResponsesAdapter)


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

    response = OpenAIResponsesAdapter().generate(participant(), "Prompt text")

    assert response.status == "completed"
    assert response.text == "Generated turn"
    assert captured["url"] == "https://api.openai.com/v1/responses"
    assert captured["timeout"] == 120
    assert captured["body"]["input"] == "Prompt text"
    assert captured["auth"] == "Bearer test-key"
