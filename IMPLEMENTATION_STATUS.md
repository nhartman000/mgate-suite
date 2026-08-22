# mgate-suite Implementation Status — Historical Profile

**Historical implementation snapshot:** April 2, 2026  
**Canonical-boundary note added:** August 22, 2026

> This file describes an **earlier implementation profile**. The executable code and schemas documented below are preserved as development/provenance material, but their older file-role assignments are not the current canonical MG8 standard.

## Canonical mapping

Before using the historical status tables, apply this mapping:

| Historical profile | Current canonical baseline |
|---|---|
| `.mg8` = orchestration/project file | `.mg8` = bounded execution unit/container; `.ork` = orchestration |
| `.gitson` = embedded gate graph | auxiliary/legacy; not in the current core family |
| `.gst` = context modifiers | structured state/context/constraints with prior/current continuity |
| `.g8son` = individual Boolean gate | bounded conditional gate/operator file; 1–3 gates per file |
| `.qson` = audit trace | retained as event-level trace with distinct run/gate/trace identities |
| `.zipson` = domain/package | package/composition role is now `.mg8pk` |

Current canonical repositories are linked from the root README.

---

## Historical completed components

### 1. File specifications implemented in this repository

| Historical file type | Historical status | Historical location / meaning |
|---|---|---|
| `.mg8` | implemented | project/orchestration profile used by this engine |
| `.gitson` | implemented | gate-graph container used by this profile |
| `.gst` | implemented | gestalt/context profile |
| `.g8son` | implemented | gate definitions including Boolean operators |
| `.qson` | implemented | audit trace profile |
| `.zipson` | implemented | package/domain experiment |

These schemas remain useful for reproducing the historical engine. They are **not a substitute for the current dedicated canonical specs**.

### 2. Historical engine modules

| Module | Status | Location | Role in this profile |
|---|---|---|---|
| Loader | implemented | `engine/loader.py` | relative path / project loading |
| Validator | implemented | `engine/validator.py` | profile contract validation |
| Executor | implemented | `engine/executor.py` | DAG ordering, cycle checks, gate routing |
| Audit Log | implemented | `engine/audit.py` | run/trajectory trace generation |
| Model Adapter | implemented | `engine/model_adapter.py` | Vertex/Gemini adapter plus historical mock behavior |

### 3. Executable components

| Component | Status | Path |
|---|---|---|
| CLI runner | implemented | `cli/run_project.py` |
| CI workflow | implemented | `.github/workflows/validate.yml` |

### 4. Historical examples

- Basic photosynthesis project — `examples/project.mg8`
- Boolean-gate branch example — `examples/boolean/logic.mg8`

These should be read using the historical schemas in this repository.

---

## Historical trace model

This profile implemented:

```text
RUN_{uuid}  — execution-level identity
TRJ_{uuid}  — generated per gate execution attempt
```

It also included parent-trace relationships and duplicate-trace rejection. The current QSON repository retains the event-identity principle but provides the current public trace specification.

## Historical gate/runtime model

The profile implemented operators and routing such as:

```text
Gate types: AND / OR / NAND / NOR / BOOLEAN
Operators: = / != / > / < / >= / <= / contains
Routing: on_true / on_false
Failure policy: halt / continue / human_verify
```

These capabilities remain implementation evidence; they should not be interpreted as the complete or mandatory operator catalog of current G8SON.

## Historical validator behavior

The implementation included checks for conditions such as:

- UTF-8 BOM handling/rejection;
- absolute path restrictions;
- required fields/profile keys;
- contract mismatches;
- duplicate trace IDs;
- DAG cycles.

Some of these remain useful implementation techniques, while canonical file contracts should now be taken from the dedicated repositories.

## Historical model adapter

The April 2026 profile referenced Vertex/Gemini configuration and included a mock fallback when credentials were unavailable.

A mock fallback should **not** be interpreted as evidence that a real model provider executed. New runtime work should label simulated/mock execution explicitly and avoid silently substituting it for a requested live provider.

## Historical run commands

For reproduction of this repository's older profile:

```bash
pip install -r requirements.txt
python cli/run_project.py examples/project.mg8
python cli/run_project.py examples/boolean/logic.mg8
```

Output behavior follows this repository's historical implementation, not necessarily the newer dedicated QSON schema.

## Known unimplemented items in the historical snapshot

At the April 2026 snapshot, items documented as incomplete included:

- ZIPSON multi-MG8 orchestrator;
- human-verify failure mode;
- persisted state between gate executions;
- dynamic value passing between gates;
- standalone CLI validator;
- complete unit-test suite;
- multi-parent join nodes;
- threshold-confidence evaluation for atomic requirements.

## Current development guidance

For new work:

1. treat this repository as a historical/experimental implementation profile;
2. use the dedicated MG8/GST/G8SON/QSON repos as the public interface authority;
3. use `.ork` for orchestration in new canonical work;
4. use `.mg8pk` for the package/composition role rather than extending `.zipson` as if it were the current standard;
5. do not silently fall back from real providers to mocks when reporting a real execution result.
