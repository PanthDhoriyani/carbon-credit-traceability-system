def calculate_credits(
    reported_co2: float,
    baseline_co2: float,
    ai_verdict: str,
) -> dict:
    """
    Carbon credit issuance logic.

    Rules:
      - Company MUST pass AI fraud check (verdict = NORMAL)
      - Company MUST have reported BELOW baseline
      - Credits = baseline - reported  (1 credit = 1 tonne CO2 saved)
      - If reported >= baseline: 0 credits (no punishment, just no reward)
      - If AI flags as suspicious: 0 credits (report rejected)
    """

    if ai_verdict == "SUSPICIOUS":
        return {
            "credits_earned": 0.0,
            "eligible": False,
            "reason": "Report flagged as suspicious by AI anomaly detector. Verification failed.",
        }

    co2_saved = baseline_co2 - reported_co2

    if co2_saved <= 0:
        return {
            "credits_earned": 0.0,
            "eligible": False,
            "reason": (
                f"Reported emissions ({reported_co2:.2f}t) meet or exceed "
                f"baseline ({baseline_co2:.2f}t). No credits earned."
            ),
        }

    credits = round(co2_saved, 4)

    return {
        "credits_earned": credits,
        "eligible": True,
        "reason": (
            f"Saved {credits:.2f}t CO2 below baseline. "
            f"{credits:.2f} carbon credit tokens (CCT) will be issued."
        ),
    }
