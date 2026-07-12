# Dataset — Mega HSSE Transformer

This folder contains the dataset structure for the Mega HSSE Transformer research project.

**Status:** Folder structure established. Data ingestion pending.  
**Target scale:** 1.5 TB (HSSE_AI_DATASET_MAX)

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

## Ingestion Pipeline (Future Phase)

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

## Open Training Workflow (Current Scaffold)

Anyone can train using their own data by keeping this folder layout:

- `dataset/01_KNOWLEDGE_LIBRARY`
- `dataset/02_TECHNICAL_LIBRARY`
- `dataset/03_GENERAL_KNOWLEDGE`
- `dataset/04_AI_DATA`

Then:

1. Add records that follow `open_training_schema.json`.
2. Register record files in `manifest.json` (`ai_data_records` list).
3. Run:
   - `python -m src.math_engine.cli train --dataset-root ./dataset --output ./artifacts/open_model.json`
   - `python -m src.math_engine.cli evaluate --dataset-root ./dataset --output ./artifacts/benchmark_report.json`

The evaluation report includes deployment-readiness gating. Claims of deployment readiness
must remain evidence-based and depend on benchmark + expert validation results.
