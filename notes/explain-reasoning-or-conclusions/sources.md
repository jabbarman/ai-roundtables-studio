# Source Packet: Explaining Reasoning vs. Giving Conclusions

These sources are meant to ground the discussion without deciding it in advance.

## NIST AI Risk Management Framework 1.0

- URL: https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-ai-rmf-10
- Kind: framework
- Relevance: Treats transparency, explainability, interpretability, reliability, and accountability as trustworthiness attributes. Useful for asking whether explanations are a property of a model, a product, or a risk-management process.

## OpenAI Model Spec 2025-09-12

- URL: https://model-spec.openai.com/2025-09-12.html
- Kind: model behavior spec
- Relevance: Discusses hidden chain-of-thought messages and why raw reasoning may not be exposed directly. Useful for separating raw reasoning, reasoning summaries, and final answers.

## OpenAI Reasoning Models Guide

- URL: https://platform.openai.com/docs/guides/reasoning
- Kind: API documentation
- Relevance: Describes reasoning models and reasoning summaries. Useful for asking whether "show your reasoning" should mean raw chain of thought, a faithful summary, or task-specific evidence.

## Anthropic: Measuring Faithfulness in Chain-of-Thought Reasoning

- URL: https://www.anthropic.com/research/measuring-faithfulness-in-chain-of-thought-reasoning
- Kind: research note
- Relevance: Raises the problem that stated reasoning may not faithfully represent why a model produced an answer. Useful for challenging the idea that explanations automatically improve trust.

## Google AI Principles

- URL: https://blog.google/technology/ai/ai-principles/
- Kind: principles
- Relevance: Includes commitments around accountability, safety, privacy, and social benefit. Useful for linking explanation design to institutional responsibility.
