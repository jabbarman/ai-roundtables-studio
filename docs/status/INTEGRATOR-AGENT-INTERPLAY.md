# Integrator and Agent Interplay

The main Codex integrator owns the calibration episode end to end: configuration,
provider run, editorial assessment, audio render, evidence, and local commits.

No sub-agent work is currently needed. The implementation and production stages
are sequential, share the same small artifact set, and benefit from one owner
retaining editorial context.
