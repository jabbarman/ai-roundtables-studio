# Series One Calibration QA

| Surface | Check | Evidence | Status |
| --- | --- | --- | --- |
| Models | Direct generation succeeds for all three seats | `evidence/model-slate-validation.md` | Pass |
| Code | Full pytest suite | Command output | Pass |
| Config | Draft and schema validation | `runs/raw/when-should-you-trust-an-ai-answer-draft` | Pass |
| Transcript | Provider completion and structural evaluation | `evidence/transcript-evaluation.json` | Pass |
| Editorial | Clarity, disagreement, evidence, speaker distinction | `evidence/editorial-review.md` | Pass |
| Published | Metadata, provenance, source links, and editorial note | `evidence/published-check.md` | Pass |
| Audio | Script validation, MP3 render, loudness and duration | Pending manifest | Pending |
| Gate | User accepts calibration as series baseline | Sign-off record | Pending |
