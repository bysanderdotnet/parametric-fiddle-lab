"""Filament material property library.

Each module exposes:
  NAME, DATASHEET,
  SPECIFICATIONS, PRINTING, PHYSICAL, MECHANICAL, CHEMICAL, SPECIMEN_TEST,
  DENSITY_KG_M3, YOUNGS_MODULUS_PA, POISSON_RATIO, DENSITY_G_MM3

Call lookup(name) to resolve a filament by short name.
"""

from filaments import bambu_pla_basic, petg, asa, pc, nylon, pla_cf

__all__ = ["bambu_pla_basic", "petg", "asa", "pc", "nylon", "pla_cf", "lookup", "names"]

_REGISTRY = {
    "pla": bambu_pla_basic,
    "petg": petg,
    "asa": asa,
    "pc": pc,
    "nylon": nylon,
    "pla-cf": pla_cf,
}


def lookup(name):
    key = name.strip().lower()
    if key not in _REGISTRY:
        raise KeyError(f"Unknown filament '{name}'. Available: {', '.join(_REGISTRY)}")
    return _REGISTRY[key]


def names():
    return list(_REGISTRY)
