# mgate-suite — Historical / Pre-Canonical MG8 Implementation Profile

`mgate-suite` is an experimental implementation lineage for Nicholas Hartman / American Milestone Inc.'s MGate, Nych, Kadmon, gated execution, trace, and recursive-agent work.

> **Status note — August 2026:** this repository predates the current canonical MG8 file-family specifications. Its code and historical documents are preserved as implementation/provenance material, but older file meanings in this repository must not be treated as the current MG8 standard.

## Current canonical MG8 baseline

The current public file-family baseline is:

```text
.mg8pk   package / composition layer
.mg8     bounded execution unit / container
.ork     orchestration / ordering / branching / loops
.gst     structured state / context / constraints
.g8son   bounded conditional gates/operators (1–3 gates per file)
.qson    auditable event-level execution trace
```

Canonical repositories:

- MG8 / `.mg8`: https://github.com/nhartman000/mg8
- GST / `.gst`: https://github.com/nhartman000/gst
- G8SON / `.g8son`: https://github.com/nhartman000/g8son
- QSON / `.qson`: https://github.com/nhartman000/qson-
- MG8 reference runtime: https://github.com/nhartman000/mg8-engine
- TCTA: https://github.com/nhartman000/TCTA-

## What this repository contains

This repository preserves a broader experimental suite, including:

- Nych symbolic-protocol work;
- ADSR multi-state gating experiments;
- recursive trait / agent experiments;
- Kadmon architecture and installation material;
- earlier DAG/gate execution code;
- earlier `.mg8`, `.gitson`, `.gst`, `.g8son`, `.qson`, and `.zipson` schemas;
- implementation-status and rebuild documents;
- Mobius transport / invariant material;
- historical examples and UI/export work.

These artifacts are useful as development provenance and as evidence of earlier implementation directions. They are not all mutually current.

## Historical-to-current terminology map

| Earlier `mgate-suite` usage | Current canonical position |
|---|---|
| `.mg8` described as the orchestration file | `.mg8` is the bounded unit/container; orchestration belongs to `.ork` |
| `.zipson` as the package/domain container | package/composition role is now `.mg8pk` |
| `.gitson` as a gate-graph container | auxiliary/legacy format; not part of the current core MG8 file family |
| `.g8son` as one Boolean gate | `.g8son` is a bounded gate/operator file containing 1–3 gates |
| `.gst` as gestalt modifiers/context only | `.gst` is the structured state/context/constraint layer, including prior/current continuity |
| `.qson` audit log | concept retained and hardened as event-level auditable trace with separate run/gate/trace identity |
| gate ordering embedded in older project structures | ordering/routing is assigned to `.ork` |

## NychForge / Kadmon profile

The NychForge/Kadmon material in this repository is an implementation profile built around concepts such as:

- Nych symbolic representation;
- ADSR/Pan control surfaces;
- recursive or timeline-based experimentation;
- DAG execution;
- model adapters;
- trace generation.

Those mechanisms may be useful extensions or experimental profiles. They should not be read as mandatory requirements of the canonical MG8 file formats.

## Running the historical implementation

The current historical implementation status document describes the code paths that existed in the April 2026 profile:

- [`IMPLEMENTATION_STATUS.md`](IMPLEMENTATION_STATUS.md)
- [`REBUILD_SPEC.md`](REBUILD_SPEC.md)
- [`MASTER_SPEC_HANDOFF.md`](MASTER_SPEC_HANDOFF.md)

When executing old examples, use the matching historical schemas/code from this repository. Do not assume an old example automatically conforms to the newer dedicated MG8/GST/G8SON/QSON specifications.

## Repository hygiene note

Earlier versions of this README contained shell commands instructing a future developer to reorganize the repository (`rm`, `mkdir`, `mv`). Those scaffolding instructions have been removed from the landing page. The repository is now documented as the historical implementation it actually contains.

## Development direction

New standards work should target the dedicated canonical repositories. New runtime work should target or interoperate with `mg8-engine` unless a separate implementation profile is intentionally being maintained here.

This separation preserves the historical work without allowing an older prototype vocabulary to overwrite the current public specification baseline.
