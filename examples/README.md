# HSSE Scenario Examples — How to Run

This folder contains JSON scenario files with inputs and expected outputs for each
mathematical safety engine module and the deterministic verification layer.

**Research Status:** Foundation Built — Validation Pending

---

## Prerequisites

Install dependencies from the repository root:

```bash
pip install -r requirements.txt
```

---

## Running Scenarios via CLI

All examples can be run using the `src.math_engine.cli` command-line interface
from the **repository root directory**.

---

### 1. Risk Calculation (Fine-Kinney)

**Scenario:** [`risk_scenario.json`](risk_scenario.json)

```bash
python -m src.math_engine.cli risk \
  --probability 6 \
  --severity 15 \
  --exposure 3 \
  --control-efficiency 0.8
```

**Expected output:**
```json
{
  "initial_risk": 270.0,
  "residual_risk": 54.0,
  "risk_level": "medium",
  "formula_initial": "Ri = P \u00d7 S \u00d7 E",
  "formula_residual": "Rr = Ri \u00d7 (1 \u2212 \u03b5)"
}
```

---

### 2. TWA Exposure

**Scenario:** [`exposure_scenario.json`](exposure_scenario.json)

```bash
python -m src.math_engine.cli exposure \
  --concentrations 150,80 \
  --durations 3,5
```

**Expected output:**
```json
{
  "twa_value": 106.25,
  "total_hours": 8.0,
  "formula": "TWA = \u03a3(Ci \u00d7 Ti) / 8"
}
```

Compare `twa_value` against the applicable OEL/PEL/TLV for the specific substance.

---

### 3. Lifting Safety Factor

**Scenario:** [`lifting_scenario.json`](lifting_scenario.json)

Reference scenario from the Mega HSSE Transformer concept:
> Load = 50 tonnes, Breaking Strength = 250 tonnes, Dynamic Factor = 1.5

```bash
python -m src.math_engine.cli lifting \
  --breaking-strength 250 \
  --applied-load 50 \
  --dynamic-factor 1.5
```

**Expected output:**
```json
{
  "safety_factor": 3.3333333333333335,
  "status": "FAIL",
  "minimum_required": 5.0,
  "decision": "STOP WORK AUTHORITY \u2014 Insufficient Safety Factor",
  "formula": "SF = Breaking_Strength / (Applied_Load \u00d7 Dynamic_Factor)"
}
```

To use a different minimum SF (e.g., 3.0 for standard industrial lift):
```bash
python -m src.math_engine.cli lifting \
  --breaking-strength 250 --applied-load 50 --dynamic-factor 1.5 --minimum-sf 3.0
```

---

### 4. Failure Probability (RCA)

**Scenario:** [`incident_scenario.json`](incident_scenario.json)

```bash
python -m src.math_engine.cli incident \
  --probabilities 0.1,0.05,0.02 \
  --threshold 0.1
```

**Expected output:**
```json
{
  "combined_probability": 0.1629,
  "status": "EXCEEDS_THRESHOLD",
  "threshold": 0.1,
  "capa_required": true,
  "formula": "Pf = 1 \u2212 \u03a0(1 \u2212 Pj)"
}
```

---

### 5. Verification Rule Check (Oxygen Threshold)

**Scenario:** [`verification_scenario.json`](verification_scenario.json)

```bash
# Unsafe oxygen level (18%) — entry should be denied
python -m src.math_engine.cli verify --oxygen-percent 18.0

# Safe oxygen level (20.9%) — no violation
python -m src.math_engine.cli verify --oxygen-percent 20.9
```

**Expected output (unsafe):**
```json
[
  {
    "rule_id": "oxygen_threshold",
    "violated": true,
    "decision": "ENTRY DENIED \u2014 Unsafe Atmospheric Condition",
    "threshold": 19.5,
    "standard": "OSHA 1910.146 \u2014 Permit-Required Confined Spaces"
  }
]
```

Combined checks:
```bash
python -m src.math_engine.cli verify \
  --oxygen-percent 18.0 \
  --safety-factor 3.3
```

---

## Running All Tests

From the repository root:

```bash
python -m pytest tests/ -v
```

---

## Research Note

All example outputs represent **research foundation artifacts**.
Outputs are deterministic and formula-based, but have not yet been:

- Cross-validated against certified engineering calculations
- Reviewed by certified HSSE professionals
- Benchmarked against a full HSSE test dataset

See [`docs/VALIDATION_FRAMEWORK.md`](../docs/VALIDATION_FRAMEWORK.md) for the
full validation plan.
