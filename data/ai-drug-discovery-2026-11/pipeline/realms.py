"""Realm keyword sets for an earlier step. A record counts for a pairing when it
matches at least one term from each of the two realms."""
from itertools import combinations

REALMS = {
    "AI": ["artificial intelligence", "machine learning", "deep learning", "neural network"],
    "Biotech": ["clinical", "patient", "drug", "therapeutic", "diagnostic", "medical"],
    "Energy": ["photovoltaic", "solar cell", "power generation", "energy efficiency",
               "fusion energy", "fusion power", "nuclear reactor", "wind turbine", "power grid"],
    "Space": ["satellite", "spacecraft", "space station", "low earth orbit", "microgravity"],
    "Quantum": ["quantum computing", "quantum computer", "qubit", "quantum sensing",
                "quantum sensor", "quantum communication", "quantum key distribution"],
}

PAIRS = list(combinations(REALMS.keys(), 2))


def or_group(terms, quote='"'):
    return "(" + " OR ".join(f'{quote}{t}{quote}' if " " in t else t for t in terms) + ")"
