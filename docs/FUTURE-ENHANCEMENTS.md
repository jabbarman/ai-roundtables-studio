# Future Enhancements

This document records potential improvements that are outside the current
production scope. Entries are proposals, not commitments. Add further ideas as
separate entries with a status, intended outcome, and enough implementation
context to evaluate them later.

## Automated Podcast Publishing

- **Status:** proposed
- **Target:** a future podcast series
- **Outcome:** after explicit approval, upload a completed episode, populate its
  publishing metadata, schedule or publish it, and record the resulting public
  URL without manually re-entering data in Spotify for Creators.

### Recommended Approach

Use an API-capable podcast host as the publishing system of record and
distribute the show to Spotify through its RSS feed. Transistor is the current
leading candidate because its documented API supports audio upload, episode
metadata, drafts, scheduling, and publication. Before adopting it, reassess
available hosts, API capabilities, pricing, and Spotify migration guidance.

Implement the host integration as a normal Python provider and CLI workflow in
this repository. An MCP server may later expose those commands to an agent, but
MCP should remain the control interface rather than the underlying publishing
mechanism.

### Proposed Workflow

1. Generate a versioned episode release manifest containing the title,
   description, season and episode numbers, episode type, explicit-content
   setting, language, publication time and timezone, and paths to the approved
   audio, artwork, transcript, and episode notes.
2. Run local preflight checks for required fields, placeholders, audio format,
   artwork, checksums, and platform limits.
3. Require listening approval before uploading the episode and creating a host
   draft.
4. Require publication approval before scheduling or publishing the draft.
5. Poll the host feed and Spotify until the episode is available, then record
   the host episode ID, feed URL, Spotify URL, status, and timestamps in the
   repository.

The two approval gates may be combined later if operational experience shows
that a single approval is sufficient.

### Implementation Requirements

- Default to dry-run behaviour and require an explicit publish or schedule
  action.
- Make retries idempotent so they cannot create duplicate episodes.
- Keep provider credentials in local environment variables or CI secrets; do
  not commit them or place them in release manifests.
- Preserve an audit record linking approvals, source artifacts, uploaded
  checksums, provider identifiers, publication status, and public URLs.
- Provide provider-level tests using mocked API responses and an end-to-end
  staging check before enabling real publication.
- Support migration of an existing Spotify-hosted show through Spotify's
  documented RSS redirect process if the future series reuses the current
  show.

### Alternatives Not Recommended for Production

- Automating the Spotify for Creators website with a browser tool such as
  Playwright is possible, but login, MFA, and interface changes make it a
  brittle fallback.
- Undocumented Spotify for Creators endpoints and reverse-engineered APIs rely
  on private implementation details and sensitive browser credentials.
- Existing Spotify MCP servers generally wrap Spotify's public playback and
  library API, which does not provide podcast publishing operations.

### Decision Gate

Revisit this proposal when planning the next series. Confirm the publishing
host, migration strategy, metadata contract, approval policy, and operating
cost before implementation begins.
