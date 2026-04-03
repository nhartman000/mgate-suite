# mgate-suite Execution Stack

```
┌───────────────────────────────────────────────────┐
│ ZIPSON (.zipson)                                 │
│ Operational domain package                       │
│ Contains multiple MG8 references                 │
└───────────────────┬───────────────────────────────┘
                    │
┌───────────────────▼───────────────────────────────┐
│ MG8 (.mg8)                                       │
│ Single-purpose deterministic reasoning program   │
│ References: 1 GITSON + 1 GST + 1 QSON output     │
└───────────────────┬───────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼───────┐       ┌───────▼───────┐
│ GST (.gst)    │       │ GITSON        │
│ Context       │       │ (.gitson)     │
│ modifiers     │       │ Gate DAG +    │
│ environment   │       │ embedded G8SON│
└───────────────┘       └───────┬───────┘
                                │
                        ┌───────┴───────┐
                        │ G8SON (.g8son)│
                        │ Individual    │
                        │ gate          │
                        │ definitions   │
                        └───────┬───────┘
                                │
┌───────────────────────────────▼───────────────────────┐
│ QSON (.qson)                                          │
│ Per-MG8 execution audit log                           │
│ Full trace ID chain, every gate execution event       │
└───────────────────────────────────────────────────────┘
```

### Execution flow order
1.  ZIPSON → loads referenced MG8s
2.  MG8 → loads GST **first**, then GITSON
3.  GST → applies context modifiers
4.  GITSON → executes DAG of embedded G8SON gates
5.  Each gate execution → generates unique trace_id
6.  All events written to QSON audit log

### Cardinality rules (strict)
- 1 ZIPSON → N MG8
- 1 MG8 → exactly 1 GST, exactly 1 GITSON, exactly 1 QSON
- 1 GITSON → N G8SON gates (embedded, no external references)
- 1 MG8 execution → exactly 1 QSON
