# NychForge

**Bounded Gated Recursive Self-Editing AI Builder**

Build deterministic, auditable agents using ADSR multi-state gating and Nych symbolic protocol. Isolate traits, recurse deeply, walk timelines, then export production APKs.

## Core Features

- **ADSR Gating**: Attack, Decay, Sustain, Release phases for controlled optimization
- **Nych Protocol**: Symbolic language for self-editing and state transitions
- **Recursive Trait Optimization**: Safely isolate and evolve specific capabilities
- **Timeline System**: Jump forward/backward to find optimal agent states
- **APK Export**:
  - **Builder APK** — Full recursive development environment on phone
  - **Runtime APK** — Locked, high-performance chat agent

## Quick Start

```bash
pip install -r requirements.txt
python cli/run.py examples/basic_agent.mg8
```

Documentation | Examples

---

### New Folder Structure (Run these commands)

```bash
# Run these commands in the root
rm -rf archive 2>/dev/null || true
mkdir -p core/{adsr,nych,recursion,timeline,gate_engine}
mkdir -p builder exporter runtime examples spec docs cli

# Move your strong core files into new structure (adjust paths if needed)
mv engine/* core/gate_engine/ 2>/dev/null || true
mv spec/* spec/ 2>/dev/null || true
```