# Methodology

## Purpose

This repo treats AI roundtables as a hybrid form:

- part editorial project
- part prompt and orchestration system
- part comparative artifact

The aim is not to prove scientific claims through transcripts alone. The aim is to produce readable conversations whose provenance, prompting, and editorial shaping are visible enough to audit.

## Layers

### Published

Reader-facing roundtables live in `published/`.

These should be shaped for flow and readability.

### Transcript

Intermediate transcripts live in `transcripts/`.

These can be cleaned for formatting and obvious noise, but should preserve the substance of the run.

### Run

Raw run artifacts live in `runs/`.

These should preserve:

- config used for the run
- prompt materials
- participant order
- turn outputs
- timestamps
- model identifiers

## Conversation Formats

Supported formats should include:

- `roundtable`
- `debate`
- `delphi`
- `consensus_dissent`
- `paper_response`

Different topics suit different formats. Defaulting everything to a gentle roundtable tends to flatten disagreement.

## Provenance Rules

Each published piece should disclose:

- date of run
- models used
- whether browsing or external retrieval was used
- whether raw outputs were merged or reordered
- degree of human editing

## Evidence Rules

Not every conversation needs citations in every paragraph. But technical or empirical claims should be grounded through one or more of:

- a source packet
- benchmark results
- linked references
- editor's notes after the transcript

## Evaluation

Useful transcript evaluation questions include:

- Did participants actually disagree?
- Did any participant dominate the conversation?
- Were claims supported with examples?
- Did the transcript drift into repetition or abstract filler?
- Was the final published piece more readable without becoming misleading?
