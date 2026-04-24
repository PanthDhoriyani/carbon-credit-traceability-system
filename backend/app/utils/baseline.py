"""
IPCC-sourced emission factors for heavy industry materials.
Unit: tonnes of CO2 per tonne of material produced.
Sources: IPCC AR6, IEA, World Steel Association.
"""

EMISSION_FACTORS: dict[str, dict] = {
    "cement": {
        "factor": 0.90,
        "unit": "t CO2 / t cement",
        "description": "Portland cement production (clinker + calcination)",
        "source": "IPCC 2006 Guidelines, Vol 3, Ch 2",
        "tolerance_pct": 15.0,
    },
    "steel": {
        "factor": 1.80,
        "unit": "t CO2 / t steel",
        "description": "Basic oxygen furnace steelmaking",
        "source": "World Steel Association, 2023",
        "tolerance_pct": 20.0,
    },
    "aluminum": {
        "factor": 11.50,
        "unit": "t CO2 / t aluminum",
        "description": "Primary aluminum smelting (Hall-Heroult process)",
        "source": "IPCC 2006 Guidelines, Vol 3, Ch 4",
        "tolerance_pct": 18.0,
    },
}

SUPPORTED_MATERIALS = list(EMISSION_FACTORS.keys())

def get_baseline(material: str, quantity_tonnes: float) -> dict:
    """
    Compute expected baseline CO2 for a given material and quantity.
    Returns baseline value + metadata.
    """
    material = material.lower().strip()
    if material not in EMISSION_FACTORS:
        raise ValueError(
            f"Unsupported material '{material}'. "
            f"Supported: {SUPPORTED_MATERIALS}"
        )
    ef = EMISSION_FACTORS[material]
    baseline_co2 = round(quantity_tonnes * ef["factor"], 4)
    return {
        "material": material,
        "quantity_tonnes": quantity_tonnes,
        "emission_factor": ef["factor"],
        "baseline_co2_tonnes": baseline_co2,
        "unit": ef["unit"],
        "source": ef["source"],
        "tolerance_pct": ef["tolerance_pct"],
    }
