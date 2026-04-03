# mgate-suite — Rebuild Specification (from user instructions)

> Verbatim user description:
>
> This is what it is mgate file is the orchestration file it's like a project file like a dot whatever the name of the app is this is Dot m gate The M gate file holds one gitson file one .gst file it creates a dot qson file which is our audit log comprehensive audit log we're doing trace logging so we're having an ID trace every single gate every single time of an operation is performed we need an ID generated trace ID. The gitson file holds the g8son files however many there are they will all be held in contained inside the gets on file and he code related to stringing the gates on files together will be inside the gets on file The GST file is the gestalt file that's going to be the modifiers this is for deterministic AI this is a system inside of systems this this system is the deterministic modular system the way it works is prompt then after the prompt damn gate file is loaded and gate file contains to gets on file which has the gate files in it first it loads the GST file That's going to tell it what the environment is like broad generalized modifiers then it's going to apply the gate file and gate files are going to give it deterministic hurdles to jump through after it jumps through those hurdles it's going to return a result and produce a cuson file The whole thing is going to be packaged inside the M gate file that's going to be akin to one prompt prompt get each prompt gets an M gate file and then multiple m gate files get zipson file so that whatever the context is enlarge and looking for working on contracts you can have multiple behaviors programmed into the contract so this is also an executable program this is not just a file system so it is our execution architecture The zip sun is not compression artifact it is equal to operational domain package each M gate is a distinct deterministic reasoning pipeline fully specified single purpose deterministic reasoning program not a project container it made constraints it must solve one task class must reference exactly one gets on it must reference exactly one GST must write to exactly one cuson to get some reuse important shift You now have powerful pattern multiple m gate can use the same gitson The QSON file is per M gate not per zips on and gate must be executable in isolation no cross dependencies this now should be a system of systems zips on composed of deterministic subsystems M gate East can executing constrained logic crafts which is gets on under under contacts control that's GST which with full trace accountability that's qsun Don't forget that the gets on file is a executing a constrained logic graph check the files in the repository a lot of this stuff should be in the coding that's there but then add whatever is left who needs to be done

---

# Purpose
This document is the authoritative rebuild spec for mgate-suite. It transforms the user's description into a strict, implementable spec for a deterministic, traceable, DAG-driven execution engine using Vertex AI (Gemini) as the runtime model.

---

# Terminology (canonical)
- MG8 (.mg8): The orchestration/executable project file. Single-purpose deterministic reasoning program.
- GITSON (.gitson): Gate orchestration file containing embedded G8SON gate definitions and the DAG (graph) that strings them together.
- GST (.gst): Gestalt/context modifiers (environmental constraints, interpretation posture).
- QSON (.qson): Per-MG8 comprehensive audit log (trace log); produced by execution.
- ZIPSON (.zipson): Operational domain package (bundle of multiple MG8s, not compression).
- G8SON (.g8son): Gate definition object (embedded inside GITSON.gates[]).

---

# High-level invariants (non-negotiable)
- Each MG8:
  - Must reference exactly one GITSON.
  - Must reference exactly one GST.
  - Must specify exactly one QSON output path (relative).
  - Must be executable in isolation (no cross-MG8 runtime dependencies).
- Each GITSON:
  - Must embed all required G8SON gate definitions for that graph.
  - Describes the DAG (nodes, edges). The DAG can be a general DAG (not limited to linear).
- QSON:
  - One QSON per MG8 execution (per run).
  - QSON.events[] must exist and be non-empty after any successful run.
  - Each event is an execution-time record and must include required trace fields.
- Paths:
  - All file paths referenced in MG8/GITSON/GST are relative to the MG8 file location. Absolute paths or repository-prefixed paths (e.g. mgate_keeper/projects/...) are forbidden.
- Encoding:
  - No file may contain a UTF-8 BOM (U+FEFF) — validator must reject BOMs.
- Schema drift:
  - No extra fields at the root layers that are not allowed by schema (forbidden keys: project_name, metadata, notes, etc.). Validator must reject drift.
- Trace generation:
  - Every gate execution attempt MUST generate a new unique trace_id (runtime-generated).
  - trace_id values MUST NOT be pre-populated in static gate definitions or carried across runs.
  - run_trace_id is created at the start of MG8 execution and ties the entire run.
  - parent_trace_id links causal chain(s) for events.

---

# Trace and DAG semantics (detailed)
- run_trace_id:
  - Generated once at run start. Format: RUN_{uuid}
- event.trace_id:
  - Generated for every gate execution attempt. Format: TRJ_{uuid}
- parent linking:
  - Implement Option 1: each event contains a `parent_trace_id` (string) for single parent, and an optional `parent_trace_ids` array when node has multiple parents (join). Engines may populate both; primary compatibility uses `parent_trace_id` when single.
  - For node(s) with no incoming edges, `parent_trace_id` = run_trace_id.
- Multi-parent nodes:
  - If multiple upstream parents exist, `parent_trace_ids` should list all upstream trace_ids; engines must pick one primary `parent_trace_id` (recommended last upstream or deterministic selection).
- No reuse:
  - Within a single QSON `events[]`, no two events may share the same `trace_id`.
- Event order:
  - Events should reflect execution order (should align with topological order for DAG but actual runtime order is acceptable as long as causal parent ids are correct).

---

# Data model — required fields

MG8 (required keys):
- gitson: string (relative path to .gitson)
- gst: string (relative path to .gst)
- qson: string (relative path where .qson will be written)
- model: string (e.g., "gemini-pro")
- supported_models: optional array[string]
- seed: optional integer

GITSON (contains embedded gates[] and graph):
- gates: [ { gate_id, gate_name, prompt_template, expects[], produces[], atomic_requirements[], failure_policy? } ]
- graph:
  - nodes: [gate_id, ...]
  - edges: [ { from: gate_id, to: gate_id }, ... ]

GST:
- context_id
- interpretation_posture
- primary_modality
- constraints[] (optional)
- emits[] (the emitted fields expected by gates)

QSON (audit log, per run):
- schema_version
- run_trace_id
- project_id (optional)
- context_ref (must match GST.context_id)
- model (string, actual model used)
- responses[] (preserved)
- events[] (non-empty)
  - Each event object: required
    - trace_id (unique)
    - parent_trace_id (string) and/or parent_trace_ids (array)
    - run_trace_id
    - source_objects (object with gate_id, gst_id, project_id, etc.)
    - source_paths (must be relative: mg8, gitson, gst)
    - decision (string)
    - status (string)
    - confidence_at_decision (number)
    - ambiguity (boolean)
    - rule_triggered (array of rule ids)
    - timestamp (ISO-8601)
    - decision_reason (optional string)

ZIPSON:
- domain_id
- mg8_list: array of MG8 relative paths

---

# Execution flow (exact)
1. User invokes the engine with a single MG8 file (CLI or library).
2. Engine resolves MG8 path; base_dir = parent(MG8).
3. Engine loads GST first (base_dir / gst).
4. Engine loads GITSON (base_dir / gitson) and reads embedded gates and DAG definition.
5. Engine validates gst/gitson against schemas (fail fast if invalid).
6. Engine generates run_trace_id.
7. Engine computes a DAG topological order (detect cycles and fail).
8. For each node in topological order:
   - Generate a new event trace_id for the attempt.
   - Determine parent_trace_id(s) based on upstream node trace_id(s). If no parents, parent_trace_id = run_trace_id.
   - Build the prompt using GST modifiers + gate.prompt_template.
   - Call the selected model via the model adapter (Gemini/Vertex).
   - Evaluate gate atomic requirements deterministically (engine logic).
   - Create an event entry with required fields including the generated trace_id and append to qson.events[].
9. After execution completes for this MG8, write QSON to the MG8-specified relative path.
10. Each MG8 run produces one QSON; ZIPSONs orchestrate multiple MG8s (each produces its own QSON).

---

# Determinism and gating
- Determinism:
  - Engine must accept `seed` and apply it consistently to model adapter where supported (Vertex may have deterministic flags).
  - Prompt + GST + seed -> deterministic run if model + infrastructure support determinism.
- Gate evaluation:
  - Gates define `atomic_requirements` and thresholds (e.g., threshold_efficiency).
  - Engine must compute a deterministic `confidence` value for each gate decision.
  - Gate `failure_policy` defines what to do on reject or ambiguity (halt/continue/human_verify).

---

# Model runtime (Vertex Gemini)
- Use Vertex AI Gemini (model token: `gemini-pro`) as default.
- Credentials:
  - Requires `GOOGLE_APPLICATION_CREDENTIALS` (service account JSON with Vertex AI privileges).
  - Use `GCP_PROJECT_ID=true-artwork-479005-r3` and `GCP_LOCATION=us-central1`.
  - The engine's model adapter should detect model tokens starting with `gemini` and call Vertex SDK accordingly.
- Adapter behavior:
  - If Vertex not available locally, adapter must produce a deterministic mock response for local testing (useful for CI).
  - The QSON.responses or QSON.events should record which model actually produced the response (field: `model_used` or top-level `model` in QSON).

---

# Validator requirements (strict)
The validator must:
- Reject files with UTF-8 BOM (detect BOM at byte-level before decoding).
- Reject MG8 with forbidden root keys: `project_name`, `metadata`, `notes`, and other unapproved root-level additions.
- Enforce relative-only paths (no absolute, no repo-root prefixes).
- Validate:
  - MG8 contains schema_version, gitson, gst, qson, run_trace_id if needed.
  - GST.emits covers G8SON.expects (gst.emits ⊇ each gate.expects).
  - Each gate produces `trace_id` as part of its produces array where appropriate (G8SON.produces includes trace_id).
  - QSON.run_trace_id equals MG8.run_trace_id (or QSON contains run_trace_id generated by run).
  - QSON.events non-empty and all event fields present and valid.
  - No reused trace_id in QSON.
  - trace_id != run_trace_id for events.
- Fail the PR/commit if any of the above are not met.

---

# CI / GitHub Actions (must)
- On `pull_request` and `push` to main:
  - Run the strict validator (engine/validator.py or equivalent).
  - If validator fails, block merge.
  - Optionally run a lightweight execution test using the adapter mock to ensure QSON is written.

---

# File tree (recommended)
- spec/
  - mg8.schema.json
  - gitson.schema.json
  - gst.schema.json
  - qson.schema.json
  - zipson.schema.json
- engine/
  - loader.py (resolves relative paths)
  - validator.py (strict validator)
  - executor.py (DAG executor)
  - audit.py (trace id generation + qson writer)
  - model_adapter.py (Vertex Gemini adapter + mock fallback)
- cli/
  - run_project.py
- examples/
  - example/project.mg8
  - example/example.gitson
  - example/example.gst
- .github/workflows/
  - validate.yml (runs validator on PRs)

---

# Minimal examples (for implementers)
- example/project.mg8
```json
{
  "gitson": "example.gitson",
  "gst": "example.gst",
  "qson": "out/example.qson",
  "model": "gemini-pro",
  "seed": 42
}
```

- example/example.gitson
```json
{
  "gates": [
    {
      "gate_id": "G1",
      "gate_name": "ExplainPhotosynthesis",
      "prompt_template": "Explain photosynthesis simply.",
      "expects": ["event_candidate","confidence","ambiguity"],
      "produces": ["decision","status","trace_id"],
      "atomic_requirements": [{"req_id":"R1","requirement":"be factual"}],
      "failure_policy": {"on_reject":"halt"}
    }
  ],
  "graph": {
    "nodes": ["G1"],
    "edges": []
  }
}
```

- example/example.gst
```json
{
  "context_id": "CTX_PHOTOSYNTHESIS",
  "interpretation_posture": "Factual",
  "primary_modality": "Scientific",
  "emits": ["event_candidate","confidence","ambiguity"]
}
```

- expected output example/out/example.qson (excerpt)
```json
{
  "schema_version": "1.0",
  "run_trace_id": "RUN_...",
  "context_ref": "CTX_PHOTOSYNTHESIS",
  "model": "gemini-pro",
  "events": [
    {
      "trace_id": "TRJ_...",
      "parent_trace_id": "RUN_...",
      "run_trace_id": "RUN_...",
      "source_objects": {"gate_id":"G1"},
      "source_paths": {"mg8":"project.mg8","gitson":"example.gitson","gst":"example.gst"},
      "decision": "approve",
      "status": "pass",
      "confidence_at_decision": 0.9,
      "ambiguity": false,
      "rule_triggered": ["R1"],
      "timestamp": "2026-04-02T..."
    }
  ]
}
```

---

# Implementation checklist (deliverables)
- [ ] Authoritative JSON Schemas in `spec/`
- [ ] Engine loader that resolves relative MG8 paths
- [ ] Vertex Gemini adapter (gemini-pro) using Vertex SDK or documented fallback
- [ ] DAG executor implementing topological ordering and strict trace generation
- [ ] Audit utilities (run_trace_id, event trace_ids, qson writer)
- [ ] Strict validator that enforces BOM, forbidden keys, contract alignment, relative paths, trace uniqueness
- [ ] CLI `run_project.py` that executes a single MG8 and writes QSON
- [ ] GitHub Actions workflow that runs validator on PRs
- [ ] Unit tests for: DAG ordering, cycle detection, trace uniqueness, validator coverage
- [ ] Documentation README with usage and environment variable requirements (GOOGLE_APPLICATION_CREDENTIALS, GCP_PROJECT_ID=true-artwork-479005-r3, GCP_LOCATION=us-central1, GEMINI_MODEL=gemini-pro)

---

# Environment variables and Vertex setup
- `GOOGLE_APPLICATION_CREDENTIALS` = /path/to/service-account.json
- `GCP_PROJECT_ID` = true-artwork-479005-r3
- `GCP_LOCATION` = us-central1
- `GEMINI_MODEL` = gemini-pro
- Required pip packages: `google-cloud-aiplatform` (and any other dependencies the engine needs)

---

# Notes / rationale (as you stated)
- Each MG8 is “one prompt = one deterministic pipeline”; multiple MG8s combined into ZIPSON are a domain-level collection.
- Gate definitions (G8SON) are embedded in GITSON; no external gate files referenced by MG8 are allowed.
- The QSON is the canonical execution audit: comprehensive, traceable, and immutable post-write.
- This is an execution architecture, not just a filesystem format.
