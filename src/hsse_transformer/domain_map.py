"""
Mega HSSE Transformer — 60-Head Domain Map

Defines fixed topic boundaries for all 60 HSSE attention heads organised into
six functional zones. The mapping is deterministic and shared across
training/evaluation workflows.

Zone 1 — Leadership, Policy & Foundation   (heads 01–13)
Zone 2 — Operational Controls & Risk Mitigation (heads 14–19, 45–47)
Zone 3 — Hazard Domains — Physical & Chemical  (heads 28–39)
Zone 4 — Incident Response & Crisis Management (heads 20–27, 59)
Zone 5 — Environmental & Occupational Health   (heads 40–44)
Zone 6 — Specialised Industry & Performance    (heads 48–58, 60)
"""

from typing import Dict, List


HEAD_DOMAIN_MAP: Dict[int, dict] = {
    # ------------------------------------------------------------------
    # Zone 1: Leadership, Policy & Foundation (01–13)
    # ------------------------------------------------------------------
    1: {
        "name": "HSSE Leadership",
        "zone": 1,
        "keywords": ["leadership", "management", "commitment", "accountability"],
    },
    2: {
        "name": "Policy and Strategy",
        "zone": 1,
        "keywords": ["policy", "strategy", "vision", "corporate"],
    },
    3: {
        "name": "Legal and Regulatory",
        "zone": 1,
        "keywords": ["legal", "regulatory", "law", "legislation"],
    },
    4: {
        "name": "Objectives and KPIs",
        "zone": 1,
        "keywords": ["objectives", "kpi", "targets", "goals"],
    },
    5: {
        "name": "Risk Management Framework",
        "zone": 1,
        "keywords": ["risk", "framework", "assessment", "score"],
    },
    6: {
        "name": "Hazard Identification",
        "zone": 1,
        "keywords": ["hazard", "identification", "unsafe", "hira"],
    },
    7: {
        "name": "Management of Change",
        "zone": 1,
        "keywords": ["moc", "management of change", "modification", "change"],
    },
    8: {
        "name": "Contractor Management",
        "zone": 1,
        "keywords": ["contractor", "vendor", "prequalification", "subcontractor"],
    },
    9: {
        "name": "Competency and Training",
        "zone": 1,
        "keywords": ["competency", "qualification", "training", "certification"],
    },
    10: {
        "name": "Communication and Consultation",
        "zone": 1,
        "keywords": ["communication", "consultation", "briefing", "handover"],
    },
    11: {
        "name": "Stop Work Authority",
        "zone": 1,
        "keywords": ["stop work", "authority", "critical", "swa"],
    },
    12: {
        "name": "Compliance Obligations",
        "zone": 1,
        "keywords": ["compliance", "obligation", "requirement", "osha", "iso", "ilo"],
    },
    13: {
        "name": "Internal Audit",
        "zone": 1,
        "keywords": ["audit", "inspection", "finding", "self-assessment"],
    },
    # ------------------------------------------------------------------
    # Zone 2: Operational Controls & Risk Mitigation (14–19, 45–47)
    # ------------------------------------------------------------------
    14: {
        "name": "Permit to Work",
        "zone": 2,
        "keywords": ["permit", "ptw", "authorization", "work permit"],
    },
    15: {
        "name": "Lockout Tagout",
        "zone": 2,
        "keywords": ["loto", "isolation", "lockout", "tagout"],
    },
    16: {
        "name": "Job Safety Analysis",
        "zone": 2,
        "keywords": ["jsa", "job safety", "task analysis", "step"],
    },
    17: {
        "name": "Behavioral Based Safety",
        "zone": 2,
        "keywords": ["behavior", "observation", "intervention", "bbs"],
    },
    18: {
        "name": "Hierarchy of Controls",
        "zone": 2,
        "keywords": ["control", "elimination", "substitution", "mitigation"],
    },
    19: {
        "name": "Personal Protective Equipment",
        "zone": 2,
        "keywords": ["ppe", "personal protective", "equipment", "respiratory", "protection"],
    },
    20: {
        "name": "Incident Reporting",
        "zone": 4,
        "keywords": ["incident", "reporting", "event", "notification"],
    },
    21: {
        "name": "Root Cause Analysis",
        "zone": 4,
        "keywords": ["investigation", "root cause", "rca", "why"],
    },
    22: {
        "name": "CAPA Management",
        "zone": 4,
        "keywords": ["capa", "corrective", "preventive", "action"],
    },
    23: {
        "name": "Lessons Learned",
        "zone": 4,
        "keywords": ["lesson learned", "learning", "trend", "sharing"],
    },
    24: {
        "name": "Emergency Planning",
        "zone": 4,
        "keywords": ["emergency", "evacuation", "response", "drill"],
    },
    25: {
        "name": "Fire Safety",
        "zone": 4,
        "keywords": ["fire", "explosion", "flammable", "suppression", "lel"],
    },
    26: {
        "name": "First Aid and Medical",
        "zone": 4,
        "keywords": ["first aid", "medical", "injury", "trauma"],
    },
    27: {
        "name": "Crisis Management",
        "zone": 4,
        "keywords": ["crisis", "command", "incident command", "continuity"],
    },
    # ------------------------------------------------------------------
    # Zone 3: Hazard Domains — Physical & Chemical (28–39)
    # ------------------------------------------------------------------
    28: {
        "name": "Chemical Safety",
        "zone": 3,
        "keywords": ["chemical", "compatibility", "reaction", "coshh", "sds"],
    },
    29: {
        "name": "Noise and Vibration",
        "zone": 3,
        "keywords": ["noise", "vibration", "decibel", "hearing"],
    },
    30: {
        "name": "Radiation Safety",
        "zone": 3,
        "keywords": ["radiation", "dose", "ionizing", "nuclear"],
    },
    31: {
        "name": "Biological Hazards",
        "zone": 3,
        "keywords": ["biological", "pathogen", "infection", "biohazard"],
    },
    32: {
        "name": "Thermal Stress",
        "zone": 3,
        "keywords": ["thermal", "heat stress", "cold", "temperature"],
    },
    33: {
        "name": "Electrical Safety",
        "zone": 3,
        "keywords": ["electrical", "arc flash", "energized", "voltage"],
    },
    34: {
        "name": "Mechanical Safety",
        "zone": 3,
        "keywords": ["mechanical", "guarding", "machine", "rotating"],
    },
    35: {
        "name": "Confined Space Safety",
        "zone": 3,
        "keywords": ["confined space", "oxygen", "entry", "atmospheric"],
    },
    36: {
        "name": "Working at Height",
        "zone": 3,
        "keywords": ["height", "fall", "harness", "scaffolding"],
    },
    37: {
        "name": "Lifting and Rigging",
        "zone": 3,
        "keywords": ["lifting", "rigging", "crane", "sling"],
    },
    38: {
        "name": "Excavation and Trenching",
        "zone": 3,
        "keywords": ["excavation", "trenching", "shoring", "soil"],
    },
    39: {
        "name": "Pressure Systems",
        "zone": 3,
        "keywords": ["pressure", "vessel", "relief", "containment"],
    },
    # ------------------------------------------------------------------
    # Zone 5: Environmental & Occupational Health (40–44)
    # ------------------------------------------------------------------
    40: {
        "name": "Occupational Health",
        "zone": 5,
        "keywords": ["health", "occupational", "surveillance", "screening"],
    },
    41: {
        "name": "Industrial Hygiene",
        "zone": 5,
        "keywords": ["hygiene", "silica", "exposure", "twa", "ih"],
    },
    42: {
        "name": "Waste Management",
        "zone": 5,
        "keywords": ["waste", "disposal", "segregation", "hazardous waste"],
    },
    43: {
        "name": "Pollution Control",
        "zone": 5,
        "keywords": ["pollution", "emission", "spill", "effluent"],
    },
    44: {
        "name": "Sustainability",
        "zone": 5,
        "keywords": ["sustainability", "carbon", "esg", "environment", "ecology"],
    },
    45: {
        "name": "Safety Induction",
        "zone": 2,
        "keywords": ["induction", "onboarding", "site access", "orientation"],
    },
    46: {
        "name": "Document Control",
        "zone": 2,
        "keywords": ["document", "procedure", "revision", "controlled"],
    },
    47: {
        "name": "Resource Management",
        "zone": 2,
        "keywords": ["resource", "manpower", "staffing", "availability"],
    },
    # ------------------------------------------------------------------
    # Zone 6: Specialised Industry & Performance (48–58, 60)
    # ------------------------------------------------------------------
    48: {
        "name": "Lagging Indicators",
        "zone": 6,
        "keywords": ["lagging", "trir", "ltir", "recordable", "severity rate"],
    },
    49: {
        "name": "Leading Indicators",
        "zone": 6,
        "keywords": ["leading", "proactive", "near miss", "observation"],
    },
    50: {
        "name": "Safety Culture Index",
        "zone": 6,
        "keywords": ["culture", "maturity", "climate", "engagement"],
    },
    51: {
        "name": "Construction Safety",
        "zone": 6,
        "keywords": ["construction", "site", "civil", "building"],
    },
    52: {
        "name": "Mining Safety",
        "zone": 6,
        "keywords": ["mining", "pit", "underground", "tunneling"],
    },
    53: {
        "name": "Oil and Gas Safety",
        "zone": 6,
        "keywords": ["offshore", "drilling", "hydrocarbon", "oil", "gas"],
    },
    54: {
        "name": "Marine Safety",
        "zone": 6,
        "keywords": ["marine", "vessel", "maritime", "navigation"],
    },
    55: {
        "name": "Aviation Safety",
        "zone": 6,
        "keywords": ["aviation", "helideck", "helicopter", "air"],
    },
    56: {
        "name": "Logistics and Warehousing",
        "zone": 6,
        "keywords": ["warehouse", "logistics", "material handling", "forklift"],
    },
    57: {
        "name": "Transportation Safety",
        "zone": 6,
        "keywords": ["transport", "vehicle", "road", "fleet"],
    },
    58: {
        "name": "Manufacturing Safety",
        "zone": 6,
        "keywords": ["manufacturing", "production", "plant", "production line"],
    },
    # Zone 4 continued (head 59 is within Zone 4 range)
    59: {
        "name": "Physical Security",
        "zone": 4,
        "keywords": ["security", "threat", "access control", "intrusion"],
    },
    60: {
        "name": "Mega-Scale Integration",
        "zone": 6,
        "keywords": ["mega", "integration", "synthesis", "master", "system"],
    },
}


def head_name(area: int) -> str:
    """Return deterministic attention head name for a HSSE area."""
    return f"head_{area:02d}"


def all_head_names() -> List[str]:
    """Return all 60 deterministic attention head names."""
    return [head_name(area) for area in sorted(HEAD_DOMAIN_MAP)]
