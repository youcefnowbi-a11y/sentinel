# P4A EvalBench Plan

Status: first slice implemented through targeted tests

P4A EvalBench focuses on perception and reliability, not Browser V3 powers.

## Metrics

The P4A slice tracks:

- AX tree capture correctness;
- DOMSnapshot normalization correctness;
- UIObservation hash integrity;
- visual observation boundedness;
- public pool lease/release correctness;
- public multi-tab lifecycle correctness;
- verifier post-action correctness;
- loop detector correctness;
- FinalGate rejection of forged V2.5 events.

## Targeted Tests

Implemented tests cover:

- CDP AX tree capture and hash binding;
- DOMSnapshot capture and hash binding;
- UIObservation from stable refs;
- forged UIObservation hash rejection;
- visual crop/zoom observation with OCR stub;
- public/stateless pool lease and release;
- public multi-tab strategy;
- pool over-capacity rejection;
- loop detection;
- post-action verifier;
- stateful forged V2.5 pool event rejection.

## Later Benchmark Expansion

After P4A lock, the broader Browser EvalBench can add multi-run statistics, fault injection, and external benchmark mappings. That remains evaluation infrastructure, not a new browser authority class.
