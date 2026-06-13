# motors/internal_mental.py — CCM v7
#
# mental INTERNAL ENGINE — cognitive self-regulation
#
# Exact analog of internal_somatic.py but for the mental engine.
#
# The push comes from mental_state_system — states like fear, loneliness,
# security, joy — that accumulate through concepts and decay with half_life.
#
# process() receives the push already computed by MentalStateSystem and returns it
# as a vector {P, A, Er, Rr} ready for apply_internal().

from db.db_mental import MENTAL_KEYS


def process(mental_state_push: dict) -> dict:
    """
    mental_state_push : vector {P,A,Er,Rr} de MentalStateSystem.get_mental_push()
    Returns same vector with pipeline metadata.
    """
    result = {k: mental_state_push.get(k, 0.0) for k in MENTAL_KEYS}
    result["_pipeline"] = "internal_mental"
    result["_active"]   = [k for k in MENTAL_KEYS if result[k] != 0.0]
    return result
