"""
Mega HSSE Transformer — 60-Head Domain Map

Defines fixed topic boundaries for all 60 HSSE attention heads.
The mapping is deterministic and shared across training/evaluation workflows.
"""

from typing import Dict, List


HEAD_DOMAIN_MAP: Dict[int, dict] = {
    1: {"name": "HSSE Governance", "keywords": ["governance", "policy", "management"]},
    2: {"name": "Safety Leadership", "keywords": ["leadership", "accountability", "ownership"]},
    3: {"name": "Safety Culture", "keywords": ["culture", "behavior", "engagement"]},
    4: {"name": "Legal Compliance", "keywords": ["compliance", "legal", "regulatory"]},
    5: {"name": "Hazard Identification", "keywords": ["hazard", "identification", "unsafe"]},
    6: {"name": "Risk Analysis", "keywords": ["risk", "analysis", "matrix"]},
    7: {"name": "Risk Assessment", "keywords": ["risk", "assessment", "score"]},
    8: {"name": "Control Hierarchy", "keywords": ["control", "elimination", "mitigation"]},
    9: {"name": "Audit and Inspection", "keywords": ["audit", "inspection", "finding"]},
    10: {"name": "Competence Management", "keywords": ["competence", "qualification", "training"]},
    11: {"name": "Stop Work Authority", "keywords": ["stop work", "authority", "critical"]},
    12: {"name": "Regulatory Standards", "keywords": ["osha", "iso", "ilo"]},
    13: {"name": "Contractor Safety", "keywords": ["contractor", "vendor", "prequalification"]},
    14: {"name": "Permit to Work", "keywords": ["permit", "ptw", "authorization"]},
    15: {"name": "Lockout Tagout", "keywords": ["loto", "isolation", "lockout"]},
    16: {"name": "Job Safety Analysis", "keywords": ["jsa", "job safety", "task analysis"]},
    17: {"name": "Toolbox Talks", "keywords": ["toolbox", "briefing", "pre-job"]},
    18: {"name": "Barrier Management", "keywords": ["barrier", "safeguard", "layer"]},
    19: {"name": "Change Management", "keywords": ["moc", "change", "modification"]},
    20: {"name": "Incident Reporting", "keywords": ["incident", "reporting", "event"]},
    21: {"name": "Incident Investigation", "keywords": ["investigation", "root cause", "rca"]},
    22: {"name": "Corrective Actions", "keywords": ["capa", "corrective", "preventive"]},
    23: {"name": "Learning from Events", "keywords": ["lesson learned", "learning", "trend"]},
    24: {"name": "Emergency Response", "keywords": ["emergency", "response", "evacuation"]},
    25: {"name": "Fire and Explosion", "keywords": ["fire", "explosion", "flammable"]},
    26: {"name": "First Aid", "keywords": ["first aid", "medical", "injury"]},
    27: {"name": "Crisis Management", "keywords": ["crisis", "command", "incident command"]},
    28: {"name": "Chemical Safety", "keywords": ["chemical", "compatibility", "reaction"]},
    29: {"name": "Toxicology", "keywords": ["toxic", "toxicity", "dose"]},
    30: {"name": "Process Safety", "keywords": ["process safety", "pressure", "containment"]},
    31: {"name": "Respiratory Protection", "keywords": ["respirator", "fit test", "airborne"]},
    32: {"name": "Electrical Safety", "keywords": ["electrical", "arc flash", "energized"]},
    33: {"name": "Working at Height", "keywords": ["height", "fall", "harness"]},
    34: {"name": "Mechanical Safety", "keywords": ["mechanical", "guarding", "machine"]},
    35: {"name": "Confined Space Safety", "keywords": ["confined space", "oxygen", "entry"]},
    36: {"name": "Pressure Systems", "keywords": ["pressure", "vessel", "relief"]},
    37: {"name": "Lifting and Rigging", "keywords": ["lifting", "rigging", "crane"]},
    38: {"name": "Radiation Safety", "keywords": ["radiation", "dose", "ionizing"]},
    39: {"name": "Ergonomics", "keywords": ["ergonomic", "musculoskeletal", "posture"]},
    40: {"name": "Industrial Hygiene", "keywords": ["hygiene", "silica", "exposure"]},
    41: {"name": "Occupational Health", "keywords": ["health", "occupational", "screening"]},
    42: {"name": "Waste Management", "keywords": ["waste", "disposal", "segregation"]},
    43: {"name": "Pollution Control", "keywords": ["pollution", "emission", "spill"]},
    44: {"name": "Environmental Protection", "keywords": ["environment", "ecology", "protection"]},
    45: {"name": "Training Systems", "keywords": ["training", "competency", "curriculum"]},
    46: {"name": "Communication", "keywords": ["communication", "handover", "brief"]},
    47: {"name": "Human Factors", "keywords": ["human factors", "fatigue", "error"]},
    48: {"name": "Performance Indicators", "keywords": ["kpi", "metric", "performance"]},
    49: {"name": "Behavior Based Safety", "keywords": ["behavior", "observation", "intervention"]},
    50: {"name": "Safety Performance", "keywords": ["trir", "lagging", "leading"]},
    51: {"name": "Construction Safety", "keywords": ["construction", "site", "excavation"]},
    52: {"name": "Mining Safety", "keywords": ["mining", "pit", "underground"]},
    53: {"name": "Oil and Gas Safety", "keywords": ["offshore", "drilling", "hydrocarbon"]},
    54: {"name": "Manufacturing Safety", "keywords": ["manufacturing", "production", "plant"]},
    55: {"name": "Logistics Safety", "keywords": ["warehouse", "logistics", "material handling"]},
    56: {"name": "Maritime Safety", "keywords": ["marine", "vessel", "navigation"]},
    57: {"name": "Transportation Safety", "keywords": ["transport", "vehicle", "road"]},
    58: {"name": "Security and Protection", "keywords": ["security", "threat", "access control"]},
    59: {"name": "Business Continuity", "keywords": ["continuity", "resilience", "recovery"]},
    60: {"name": "Data and AI Assurance", "keywords": ["ai", "data quality", "hallucination"]},
}


def head_name(area: int) -> str:
    """Return deterministic attention head name for a HSSE area."""
    return f"head_{area:02d}"


def all_head_names() -> List[str]:
    """Return all 60 deterministic attention head names."""
    return [head_name(area) for area in sorted(HEAD_DOMAIN_MAP)]
