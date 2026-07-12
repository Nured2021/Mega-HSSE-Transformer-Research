# Dataset — Mega HSSE Transformer

This folder contains the dataset structure for the Mega HSSE Transformer research project.

**Status:** Phase 3 complete. All 4 layers populated. Training pipeline operational.
**Total training records:** 70 across all 60 HSSE attention heads.
**Target scale:** 1.5 TB (HSSE_AI_DATASET_MAX — future expansion)

---

## Folder Descriptions

### 01_KNOWLEDGE_LIBRARY

**Intended content:**
- HSSE regulatory standards (ISO 45001, OSHA 29 CFR, ILO guidelines)
- Codes of practice and safety procedures
- Industry regulations and legislation (national and international)
- Professional body guidelines (IOSH, ASSP, NSC)
- Permit-to-work frameworks and LOTO procedures

**Ingestion expectations:**
- Document formats: PDF, DOCX, structured text
- Source verification required for each document
- Metadata: standard reference number, issuing body, version, date

---

### 02_TECHNICAL_LIBRARY

**Intended content:**
- Engineering reference manuals
- Equipment operation and maintenance manuals
- Technical safety data sheets (SDS/MSDS)
- Structural and mechanical engineering references
- Lifting and rigging technical specifications
- Hazardous area classification standards

**Ingestion expectations:**
- Document formats: PDF, technical specifications, tables
- Equipment-specific tagging required
- Cross-reference with HSSE area item numbers (e.g., Item 37: Lifting & Rigging)

---

### 03_GENERAL_KNOWLEDGE

**Intended content:**
- Occupational health and industrial hygiene references
- Toxicology and chemical hazard databases
- Environmental science references
- Human factors and ergonomics literature
- Emergency response guidelines
- Incident investigation case studies

**Ingestion expectations:**
- Academic and professional publications
- Annotated with HSSE area tags
- Quality-checked for source reliability

---

### 04_AI_DATA

**Intended content:**
- Labeled HSSE scenario datasets for model training
- Benchmark test cases (minimum 5,000 professional scenarios)
- Expert-annotated safety decision examples
- Structured input/output pairs for formula validation
- Example JSON files (see also `examples/`)

**Ingestion expectations:**
- JSON or CSV format preferred for structured data
- Labeling schema: scenario, inputs, expected_outputs, hsse_areas, rule_applied
- Split into train/validation/test sets when used for model training
- No personally identifiable information (PII)

**Open training files now included:**
- `manifest.json` — dataset manifest listing AI record files
- `open_training_schema.json` — canonical JSON schema contract
- `benchmark_cases.json` — starter benchmark cases for proof suites

---

## Data Quality Standards

All data ingested into this dataset must meet the following criteria:

| Criterion | Requirement |
|-----------|-------------|
| Source verification | Each document must have a traceable, authoritative source |
| Accuracy | Content must align with current (≤ 5 years) HSSE standards where applicable |
| Completeness | Incomplete or truncated documents must be flagged |
| Format consistency | Processed into standardized format before ingestion |
| No PII | No personally identifiable information from incident reports |

---

**Ingestion Pipeline (Phase 3 — COMPLETE)**

The data ingestion pipeline will include:

1. **Document collection** — gather source materials from authoritative bodies
2. **Format normalization** — convert to processable text/structured formats
3. **Quality checking** — validate completeness, accuracy, and source reliability
4. **Tagging** — annotate with HSSE area item numbers and metadata
5. **Loading** — populate the vector store or knowledge database
6. **Verification** — run data quality report and source citation audit

**This pipeline is planned for Phase 1 of the Build & Proof Plan.**
See [`docs/BUILD_AND_PROOF_PLAN.md`](../docs/BUILD_AND_PROOF_PLAN.md) for details.

---

## Open Training Workflow (Phase 3 — ACTIVE)

The four dataset layers are now populated and the training pipeline is operational.

### Dataset Population Status

| Layer | Content | Status |
|-------|---------|--------|
| `01_KNOWLEDGE_LIBRARY` | OSHA regulations, ISO standards, safety policies, procedures | ✅ Populated |
| `02_TECHNICAL_LIBRARY` | Engineering references, chemical safety, OEL tables, industry data | ✅ Populated |
| `03_GENERAL_KNOWLEDGE` | HSSE fundamentals, definitions, acronyms | ✅ Populated |
| `04_AI_DATA` | 70 labeled training records across all 60 HSSE heads | ✅ Populated |

### Training Records Summary

| File | Split | Count | Suites Covered |
|------|-------|-------|----------------|
| `benchmark_cases.json` | benchmark/test | 5 | unsafe_detection, no_guessing, technical_selection, multi_risk, expert_comparison |
| `hazard_cases/hazard_scenarios.json` | train | 20 | unsafe_detection, no_guessing, technical_selection, multi_risk |
| `incident_cases/incident_scenarios.json` | train | 12 | general, technical_selection, multi_risk |
| `instructions/operational_instructions.json` | train | 15 | unsafe_detection, technical_selection, general |
| `reasoning_examples/reasoning_scenarios.json` | validation | 8 | multi_risk, expert_comparison, technical_selection, no_guessing |
| `evaluation/evaluation_cases.json` | test | 10 | unsafe_detection, technical_selection |
| **Total** | | **70** | All 6 suites |

### Phase 3 Pipeline Commands

```bash
# Run training data pipeline — produces train/validation/test JSONL splits
python -m src.math_engine.cli pipeline \
    --dataset-root ./dataset \
    --output-dir ./dataset/04_AI_DATA/training

# Build training artifact (Phase 2 open training)
python -m src.math_engine.cli train \
    --dataset-root ./dataset \
    --output ./artifacts/open_model.json

# Run benchmark evaluation (Phase 4 proof)
python -m src.math_engine.cli evaluate \
    --dataset-root ./dataset \
    --output ./artifacts/benchmark_report.json
```

### JSONL Output

After running the pipeline command, the following split files are produced:

- `04_AI_DATA/training/train.jsonl` — ~47 records for model training
- `04_AI_DATA/training/validation.jsonl` — ~8 records for validation
- `04_AI_DATA/training/test.jsonl` — ~15 records for final testing

Each line is a complete JSON object conforming to `open_training_schema.json`.
