# Model Slate Validation

Validated on 2026-06-15 using the API credentials configured on this host.

| Provider | Model | Result |
| --- | --- | --- |
| OpenAI | `gpt-5.5` | Completed direct Responses API smoke request |
| Anthropic | `claude-opus-4-8` | Completed direct Messages API smoke request |
| Google | `gemini-3.1-pro-preview` | Completed `generateContent` smoke request with required thinking enabled |

The Google model rejected a zero thinking budget, then completed successfully
with a 256-token smoke-test budget. The production config reserves 512 thinking
tokens and 2,048 total output tokens.

The existing repository suite also passed: `48 passed`.
