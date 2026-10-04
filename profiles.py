"""Fictional Indian ex-serviceman profiles used for demonstration only.

No real person, unit, base, platform or service record is represented here.
Quantities are invented purely to exercise the application.
"""

SERVICES = ["Indian Army", "Indian Navy", "Indian Air Force"]

DEMO_PROFILES = {
    "Army · Stores & Logistics (Havildar)": {
        "service": "Indian Army",
        "rank": "Havildar",
        "trade": "Logistics / Stores",
        "years": 15,
        "education": "Higher Secondary (12th)",
        "certifications": "Defence driving licence (heavy vehicle)",
        "location": "Pune, Maharashtra",
        "duties": (
            "Supervised a stores section of 12 personnel handling receipt, inspection and "
            "issue of unit equipment. Maintained daily stock ledgers and monthly "
            "reconciliation of holdings. Coordinated vehicle dispatch schedules and load "
            "planning for routine resupply moves. Trained new personnel on stock "
            "documentation and safe handling procedures."
        ),
        "target_role": "Warehouse / Stores Supervisor",
    },
    "Navy · Technical Maintenance (Petty Officer)": {
        "service": "Indian Navy",
        "rank": "Petty Officer",
        "trade": "Electrical / Technical maintenance",
        "years": 12,
        "education": "Diploma (Electrical)",
        "certifications": "",
        "duties": (
            "Planned and supervised routine preventive maintenance checks on electrical "
            "equipment. Maintained fault logs and spares consumption records. Coordinated "
            "a six-member maintenance team across rotating watches. Prepared handover "
            "reports and briefed supervisors on pending defects."
        ),
        "target_role": "Maintenance Coordinator",
    },
    "Air Force · Maintenance Support (Sergeant)": {
        "service": "Indian Air Force",
        "rank": "Sergeant",
        "trade": "Maintenance support",
        "years": 14,
        "education": "Diploma (Mechanical)",
        "certifications": "Internal safety and quality training",
        "duties": (
            "Coordinated shift handovers, tool control and maintenance documentation for "
            "eight technicians. Scheduled servicing tasks against available manpower and "
            "spares. Conducted toolbox safety briefings and tracked corrective actions "
            "raised during internal inspections."
        ),
        "target_role": "Maintenance Planning Assistant",
    },
    "Army · Hindi / mixed-language sample": {
        "service": "Indian Army",
        "rank": "Naik",
        "trade": "Transport",
        "years": 10,
        "education": "Higher Secondary (12th)",
        "certifications": "",
        "duties": (
            "यूनिट के वाहन बेड़े की दैनिक देखभाल और मरम्मत का समन्वय किया। "
            "8 ड्राइवरों की ड्यूटी रोस्टर तैयार की और ईंधन तथा सर्विसिंग रिकॉर्ड रखे। "
            "Road safety briefings conducted before every convoy movement."
        ),
        "target_role": "Transport / Fleet Coordinator",
    },
}

# Short, clearly illustrative descriptions. These are NOT live vacancies,
# official equivalence rulings or authoritative eligibility criteria.
CIVILIAN_ROLES = {
    "Warehouse / Stores Supervisor": "Stock accuracy, inward/outward flow, team supervision, safety compliance.",
    "Logistics Coordinator": "Dispatch planning, vendor coordination, documentation, delivery tracking.",
    "Transport / Fleet Coordinator": "Vehicle scheduling, driver rosters, servicing records, route compliance.",
    "Maintenance Coordinator": "Preventive maintenance planning, fault tracking, spares control, technician scheduling.",
    "Operations Supervisor": "Shift planning, process discipline, reporting, escalation handling.",
    "Technical Support Coordinator": "Issue triage, resolution tracking, documentation, user communication.",
}
