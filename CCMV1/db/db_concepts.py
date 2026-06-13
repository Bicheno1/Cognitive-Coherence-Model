# db/db_concepts.py — CCM v5
#
# system neuronal — graph de asociaciones unificado
#
# Cada nodo tiene:
#   sense    : sensory channel (sight, touch, hearing, smell, taste)
#   type     : category (illogical, subject, environment, object, status, action)
#   subtype  : subcategory placeholder
#   synonyms : alternative token forms
#   related  : dict nodo_hijo → {somatic: [...tags], mental: [...asociaciones]}
#
# The related values flow down to the internal motors:
#   somatic → tags de TAG_VALUES_SOMATIC (liberan chemicals, activan reflexes)
#   mental  → asociaciones mentales (buscar en memory, evocar concepts)
#
# A node can have multiple parents (graph, not tree).
# El conteo de activaciones es global — si adrenaline aparece 3 veces → x3.

CONCEPTS = {

    # ── ILLOGICAL ─────────────────────────────────────────────────────────────
    "ghost": {
        "sense":    "sight",
        "type":     "illogical",
        "subtype":  "apparition",
        "synonyms": ["spirit", "phantom", "specter", "apparition", "ghost_es"],
        "related": {
            "self":         {"somatic": ["concept_ghost"],                   "mental": ["concept_ghost"]},
            "fear":         {"somatic": ["adrenaline", "cortisol"],          "mental": ["seek_light", "seek_person"]},
            "danger":       {"somatic": ["adrenaline", "flight_burst"],             "mental": ["traumatic_memory"]},
            "supernatural": {"somatic": [],                                  "mental": ["disbelief", "denial"]},
            "defenseless":  {"somatic": ["paralysis", "muscle_tension"],   "mental": ["seek_exit"]},
        }
    },
    "shadow": {
        "sense":    "sight",
        "type":     "illogical",
        "subtype":  "apparition",
        "synonyms": ["shade", "silhouette", "sombra"],
        "related": {
            "fear":         {"somatic": ["muscle_tension"],                "mental": ["seek_light"]},
            "uncertainty":  {"somatic": ["noradrenaline"],                   "mental": ["confusion", "hypervigilance"]},
            "danger":       {"somatic": ["adrenaline"],                      "mental": ["cognitive_threat"]},
        }
    },
    "corpse": {
        "sense":    "sight",
        "type":     "illogical",
        "subtype":  "presence",
        "synonyms": ["body", "cadaver", "muerto"],
        "related": {
            "death":        {"somatic": ["paralysis", "death_presence"],   "mental": ["mortality", "disbelief"]},
            "danger":       {"somatic": ["adrenaline"],                      "mental": ["cognitive_threat"]},
            "fear":         {"somatic": ["cortisol"],                        "mental": ["anguish"]},
        }
    },

    # ── SUBJECT ───────────────────────────────────────────────────────────────
    "person": {
        "sense":    "sight",
        "type":     "subject",
        "subtype":  "person",
        "synonyms": ["human", "someone", "somebody", "person_es"],
        "related": {
            "self":         {"somatic": ["concept_person"],                  "mental": ["concept_person"]},
            "safe":         {"somatic": ["oxytocin", "serotonin"],         "mental": ["seek_person", "trust"]},
            "trust":        {"somatic": ["oxytocin"],                       "mental": ["affection", "relief"]},
            "social":       {"somatic": ["serotonin"],                      "mental": ["relief"]},
        }
    },
    "animal": {
        "sense":    "sight",
        "type":     "subject",
        "subtype":  "animal",
        "synonyms": ["beast", "creature", "criatura"],
        "related": {
            "danger":       {"somatic": ["adrenaline", "muscle_tension"],  "mental": ["alert", "suspicion"]},
            "threat":       {"somatic": ["noradrenaline"],                   "mental": ["hypervigilance"]},
            "unpredictable":{"somatic": ["cortisol"],                        "mental": ["suspicion"]},
        }
    },

    # ── ENVIRONMENT ───────────────────────────────────────────────────────────
    "room": {
        "sense":    "sight",
        "type":     "environment",
        "subtype":  "built",
        "synonyms": ["cuarto", "habitacion", "chamber"],
        "related": {
            "self":         {"somatic": ["concept_room"],                    "mental": ["concept_room"]},
            "enclosed":     {"somatic": ["espacio_cerrado"],                 "mental": ["anticipation", "loneliness"]},
            "isolated":     {"somatic": ["aislamiento"],                     "mental": ["loneliness"]},
            "dark":         {"somatic": ["physical_darkness"],                "mental": ["hypervigilance"]},
        }
    },
    "dark": {
        "sense":    "sight",
        "type":     "environment",
        "subtype":  "condition",
        "synonyms": ["darkness", "oscuro", "darkness", "dim"],
        "related": {
            "self":         {"somatic": ["concept_dark"],                    "mental": ["concept_dark"]},
            "fear":         {"somatic": ["cortisol", "noradrenaline"],       "mental": ["seek_light", "anguish"]},
            "danger":       {"somatic": ["muscle_tension"],                "mental": ["cognitive_threat"]},
            "uncertainty":  {"somatic": ["noradrenaline"],                   "mental": ["confusion", "hypervigilance"]},
            "defenseless":  {"somatic": ["muscle_tension"],                "mental": ["anguish"]},
        }
    },
    "light": {
        "sense":    "sight",
        "type":     "environment",
        "subtype":  "condition",
        "synonyms": ["luz", "bright", "iluminado", "lamp"],
        "related": {
            "self":         {"somatic": ["concept_light"],                   "mental": ["concept_light"]},
            "safe":         {"somatic": ["serotonin", "ambient_light"],      "mental": ["relief", "clarity"]},
            "calm":         {"somatic": ["body_calm"],                    "mental": ["clarity"]},
            "warmth":       {"somatic": ["serotonin"],                      "mental": ["mental_security"]},
        }
    },
    "night": {
        "sense":    "sight",
        "type":     "environment",
        "subtype":  "time",
        "synonyms": ["noche", "midnight", "evening"],
        "related": {
            "dark":         {"somatic": ["physical_darkness", "cortisol"],    "mental": ["hypervigilance"]},
            "fear":         {"somatic": ["noradrenaline"],                   "mental": ["anticipation"]},
            "uncertainty":  {"somatic": ["muscle_tension"],                "mental": ["confusion"]},
        }
    },
    "forest": {
        "sense":    "sight",
        "type":     "environment",
        "subtype":  "natural",
        "synonyms": ["woods", "bosque", "jungle"],
        "related": {
            "isolated":     {"somatic": ["aislamiento"],                     "mental": ["loneliness", "anticipation"]},
            "unpredictable":{"somatic": ["noradrenaline"],                   "mental": ["alert"]},
            "natural":      {"somatic": ["espacio_abierto"],                 "mental": ["curiosity"]},
        }
    },
    "casa": {
        "sense":    "sight",
        "type":     "environment",
        "subtype":  "built",
        "synonyms": ["home", "house", "hogar"],
        "related": {
            "safe":         {"somatic": ["serotonin", "body_calm"],      "mental": ["mental_security", "relief"]},
            "calm":         {"somatic": ["body_calm"],                    "mental": ["acceptance"]},
            "trust":        {"somatic": ["oxytocin"],                       "mental": ["trust"]},
        }
    },
    "place": {
        "sense":    "sight",
        "type":     "environment",
        "subtype":  "natural",
        "synonyms": ["lugar", "spot", "site"],
        "related": {
            "enclosed":     {"somatic": ["espacio_cerrado"],                 "mental": ["anticipation"]},
            "isolated":     {"somatic": ["aislamiento"],                     "mental": ["loneliness"]},
        }
    },

    # ── SUBJECT / SOCIAL ──────────────────────────────────────────────────────
        # ── MUSIC ─────────────────────────────────────────────────────────────────
    "melody": {
        "sense":    "hearing",
        "type":     "music",
        "subtype":  "melodic_phrase",
        "synonyms": ["melody", "melodia", "frase_melodica", "tune", "song", "cancion",
                     "musica", "music", "bonita_cancion", "beautiful_song"],
        "related": {
            "calm":     {"somatic": ["melodia_suave", "ritmo_calm"],  "mental": ["melodia_mental", "contemplacion"]},
            "warmth":   {"somatic": ["frase_melodica"],                "mental": ["resonancia_suave"]},
            "presence": {"somatic": ["ritmo_calm"],                   "mental": ["contemplacion", "melodia_mental"]},
        }
    },
    "angelo": {
        "sense":    "sight",
        "type":     "subject",
        "subtype":  "person_known",
        "synonyms": ["angelo", "angel", "angelo-typo"],
        "related": {
            "love":     {"somatic": ["oxytocin", "safe_presence", "safe_contact"], "mental": ["affection", "trust", "relief"]},
            "admire":   {"somatic": ["serotonin", "muscle_calm"],                    "mental": ["trust", "mental_security", "clarity"]},
            "safe":     {"somatic": ["oxytocin", "body_calm"],                       "mental": ["mental_security", "relief"]},
            "social":   {"somatic": ["serotonin"],                                      "mental": ["affection", "joy"]},
        }
    },
"person": {
        "sense":    "sight",
        "type":     "subject",
        "subtype":  "social",
        "synonyms": ["person_es", "people_es", "someone_es", "someone", "people", "human"],
        "related": {
            "safe":     {"somatic": ["oxytocin", "safe_presence"], "mental": ["trust", "security"]},
            "calm":     {"somatic": ["muscle_calm", "serotonin"],  "mental": ["relief", "clarity"]},
            "social":   {"somatic": ["serotonin"],                    "mental": ["cognitive_calm", "mental_clarity"]},
        }
    },
    "street": {
        "sense":    "sight",
        "type":     "environment",
        "subtype":  "outdoor",
        "synonyms": ["calle", "avenida", "afuera", "outside", "outdoor", "open"],
        "related": {
            "safe":     {"somatic": ["serotonin", "safe_presence"], "mental": ["security", "clarity"]},
            "open":     {"somatic": ["muscle_calm"],                 "mental": ["relief", "mental_clarity"]},
            "calm":     {"somatic": ["oxytocin"],                      "mental": ["cognitive_calm"]},
        }
    },

    # ── SUBJECT / ANIMALES ────────────────────────────────────────────────────
    "fish": {
        "sense":    "sight",
        "type":     "subject",
        "subtype":  "animal",
        "synonyms": ["peces", "pez", "pescado", "tiburon", "salmon", "trucha"],
        "related": {
            "water":    {"somatic": [],               "mental": ["clarity"]},
            "calm":     {"somatic": ["body_calm"],  "mental": ["clarity"]},
            "natural":  {"somatic": ["espacio_abierto"],"mental": ["curiosity"]},
        }
    },
    "bird": {
        "sense":    "sight",
        "type":     "subject",
        "subtype":  "animal",
        "synonyms": ["bird", "bird", "bird", "small-bird", "eagle", "dove"],
        "related": {
            "fly":      {"somatic": ["espacio_abierto"], "mental": ["clarity", "curiosity"]},
            "natural":  {"somatic": ["espacio_abierto"], "mental": ["curiosity"]},
            "calm":     {"somatic": ["body_calm"],    "mental": ["relief"]},
        }
    },
    "duck": {
        "sense":    "sight",
        "type":     "subject",
        "subtype":  "animal",
        "synonyms": ["pato", "patos", "anatidae"],
        "related": {
            "fly":      {"somatic": ["espacio_abierto"], "mental": ["curiosity"]},
            "natural":  {"somatic": ["espacio_abierto"], "mental": ["curiosity"]},
            "calm":     {"somatic": ["body_calm"],    "mental": ["clarity"]},
        }
    },

    # ── STATUS ────────────────────────────────────────────────────────────────
    "danger": {
        "sense":    "sight",
        "type":     "status",
        "subtype":  "threat",
        "synonyms": ["danger_es", "dangerous", "dangerous", "threat_es"],
        "related": {
            "fear":         {"somatic": ["adrenaline", "cortisol"],          "mental": ["seek_exit", "cognitive_threat"]},
            "threat":       {"somatic": ["muscle_tension", "noradrenaline"],"mental": ["hypervigilance"]},
            "defenseless":  {"somatic": ["paralysis"],                       "mental": ["denial"]},
            "run":          {"somatic": ["adrenaline", "flight_burst"],             "mental": ["seek_exit"]},
        }
    },
    "threat": {
        "sense":    "sight",
        "type":     "status",
        "subtype":  "threat",
        "synonyms": ["threatening", "amenazante"],
        "related": {
            "danger":       {"somatic": ["adrenaline", "noradrenaline"],     "mental": ["cognitive_threat"]},
            "fear":         {"somatic": ["cortisol"],                        "mental": ["hypervigilance"]},
            "defenseless":  {"somatic": ["muscle_tension"],                "mental": ["denial"]},
        }
    },
    "alone": {
        "sense":    "sight",
        "type":     "status",
        "subtype":  "social",
        "synonyms": ["alone", "lonely", "solitary"],
        "related": {
            "isolated":     {"somatic": ["aislamiento"],                     "mental": ["loneliness"]},
            "defenseless":  {"somatic": ["cortisol"],                        "mental": ["anguish"]},
            "fear":         {"somatic": ["noradrenaline"],                   "mental": ["anticipation"]},
        }
    },
    "safe": {
        "sense":    "sight",
        "type":     "status",
        "subtype":  "safety",
        "synonyms": ["seguro", "protected", "secure"],
        "related": {
            "calm":         {"somatic": ["serotonin", "body_calm"],      "mental": ["relief", "clarity"]},
            "trust":        {"somatic": ["oxytocin"],                       "mental": ["trust", "mental_security"]},
            "warmth":       {"somatic": ["serotonin"],                      "mental": ["acceptance"]},
        }
    },
    "calm": {
        "sense":    "sight",
        "type":     "status",
        "subtype":  "emotional",
        "synonyms": ["tranquilo", "peaceful", "relaxed"],
        "related": {
            "safe":         {"somatic": ["serotonin", "body_calm"],      "mental": ["clarity", "acceptance"]},
            "trust":        {"somatic": ["oxytocin"],                       "mental": ["trust"]},
            "warmth":       {"somatic": ["body_calm"],                    "mental": ["relief"]},
        }
    },
    "scared": {
        "sense":    "sight",
        "type":     "status",
        "subtype":  "emotional",
        "synonyms": ["afraid", "frightened", "asustado", "terrified"],
        "related": {
            "fear":         {"somatic": ["adrenaline", "cortisol"],          "mental": ["seek_exit", "cognitive_threat"]},
            "danger":       {"somatic": ["adrenaline"],                      "mental": ["seek_person"]},
            "defenseless":  {"somatic": ["paralysis"],                       "mental": ["denial", "overflow"]},
            "run":          {"somatic": ["flight_burst", "adrenaline"],             "mental": ["seek_exit"]},
        }
    },
    "tired": {
        "sense":    "sight",
        "type":     "status",
        "subtype":  "physical",
        "synonyms": ["exhausted", "cansado", "weary"],
        "related": {
            "defenseless":  {"somatic": ["fatiga", "immobility"],           "mental": ["denial"]},
            "isolated":     {"somatic": ["aislamiento"],                     "mental": ["loneliness"]},
        }
    },
    "quiet": {
        "sense":    "sight",
        "type":     "status",
        "subtype":  "condition",
        "synonyms": ["silence", "silent", "still"],
        "related": {
            "calm":         {"somatic": ["silence", "body_calm"],        "mental": ["clarity"]},
            "safe":         {"somatic": ["body_calm"],                    "mental": ["acceptance"]},
        }
    },

    # ── ACTION ────────────────────────────────────────────────────────────────
    "run": {
        "sense":    "sight",
        "type":     "action",
        "subtype":  "locomotion",
        "synonyms": ["flee", "correr", "huir", "escape"],
        "related": {
            "fear":         {"somatic": ["adrenaline", "flight_burst"],             "mental": ["seek_exit"]},
            "danger":       {"somatic": ["adrenaline", "fast_movement"], "mental": ["cognitive_threat"]},
            "escape":       {"somatic": ["endorphins", "flight_burst"],             "mental": ["seek_exit"]},
        }
    },
    "walk": {
        "sense":    "sight",
        "type":     "action",
        "subtype":  "locomotion",
        "synonyms": ["caminar", "stroll", "march"],
        "related": {
            "calm":         {"somatic": ["slow_movement", "serotonin"],  "mental": ["clarity"]},
            "safe":         {"somatic": ["firm_surface"],                "mental": ["acceptance"]},
        }
    },
    "hide": {
        "sense":    "sight",
        "type":     "action",
        "subtype":  "evasion",
        "synonyms": ["esconder", "conceal", "crouch"],
        "related": {
            "fear":         {"somatic": ["cortisol", "immobility"],         "mental": ["seek_exit", "denial"]},
            "danger":       {"somatic": ["muscle_tension"],                "mental": ["cognitive_threat"]},
            "enclosed":     {"somatic": ["espacio_cerrado"],                 "mental": ["anticipation"]},
            "defenseless":  {"somatic": ["paralysis"],                       "mental": ["denial"]},
        }
    },
    "breathe": {
        "sense":    "sight",
        "type":     "action",
        "subtype":  "physiological",
        "synonyms": ["respirar", "inhale", "exhale"],
        "related": {
            "calm":         {"somatic": ["breathing", "body_calm"],     "mental": ["clarity", "relief"]},
            "safe":         {"somatic": ["serotonin"],                      "mental": ["acceptance"]},
        }
    },

    # ── ACTION / LOCOMOCION ───────────────────────────────────────────────────
    "fly": {
        "sense":    "sight",
        "type":     "action",
        "subtype":  "locomotion",
        "synonyms": ["vuelan", "volar", "vuelo", "vuela", "flies", "flying"],
        "related": {
            "freedom":  {"somatic": ["espacio_abierto"], "mental": ["clarity", "curiosity"]},
            "natural":  {"somatic": [],                  "mental": ["clarity"]},
        }
    },

    # ── OBJECT ────────────────────────────────────────────────────────────────
    "food": {
        "sense":    "sight",
        "type":     "object",
        "subtype":  "consumable",
        "synonyms": ["comida", "meal", "eat"],
        "related": {
            "safe":         {"somatic": ["satiety", "dopamine"],            "mental": ["relief", "acceptance"]},
            "warmth":       {"somatic": ["serotonin"],                      "mental": ["clarity"]},
            "calm":         {"somatic": ["body_calm"],                    "mental": ["acceptance"]},
        }
    },
    "water": {
        "sense":    "sight",
        "type":     "object",
        "subtype":  "consumable",
        "synonyms": ["agua", "drink", "liquid"],
        "related": {
            "safe":         {"somatic": ["satiety", "body_calm"],        "mental": ["relief"]},
            "calm":         {"somatic": ["body_calm"],                    "mental": ["clarity"]},
        }
    },
    "money": {
        "sense":    "sight",
        "type":     "object",
        "subtype":  "resource",
        "synonyms": ["dinero", "cash", "resource"],
        "related": {
            "safe":         {"somatic": ["dopamine"],                        "mental": ["trust", "clarity"]},
            "trust":        {"somatic": ["serotonin"],                      "mental": ["mental_security"]},
        }
    },
    "llaves": {
        "sense":    "sight",
        "type":     "object",
        "subtype":  "tool",
        "synonyms": ["keys", "llave", "key"],
        "related": {
            "enclosed":     {"somatic": ["muscle_tension"],                "mental": ["anticipation"]},
            "escape":       {"somatic": ["adrenaline"],                      "mental": ["seek_exit"]},
            "safe":         {"somatic": ["dopamine"],                        "mental": ["relief"]},
        }
    },
    "door": {
        "sense":    "sight",
        "type":     "object",
        "subtype":  "structure",
        "synonyms": ["puerta", "gate", "entrance"],
        "related": {
            "enclosed":     {"somatic": ["espacio_cerrado"],                 "mental": ["anticipation"]},
            "escape":       {"somatic": ["adrenaline"],                      "mental": ["seek_exit"]},
            "safe":         {"somatic": ["firm_surface"],                "mental": ["relief"]},
        }
    },
    "window": {
        "sense":    "sight",
        "type":     "object",
        "subtype":  "structure",
        "synonyms": ["ventana", "glass", "pane"],
        "related": {
            "light":        {"somatic": ["ambient_light"],                    "mental": ["clarity"]},
            "escape":       {"somatic": ["adrenaline"],                      "mental": ["seek_exit"]},
            "safe":         {"somatic": ["body_calm"],                    "mental": ["relief"]},
        }
    },
    # ── HEARING / LANGUAGE → mental only ─────────────────────────────────────
    "amable": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "voice_tone",
        "synonyms": ["friendly", "kind", "gentle", "cordial"],
        "related": {
            "safe":         {"somatic": [],                                  "mental": ["trust", "relief"]},
            "trust":        {"somatic": [],                                  "mental": ["affection", "mental_security"]},
            "calm":         {"somatic": [],                                  "mental": ["clarity", "acceptance"]},
        }
    },
    "frio_tono": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "voice_tone",
        "synonyms": ["cold", "distant", "inexpressive", "flat"],
        "related": {
            "uncertainty":  {"somatic": [],                                  "mental": ["suspicion", "confusion"]},
            "alone":        {"somatic": [],                                  "mental": ["loneliness", "anticipation"]},
        }
    },
    "enfadado": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "voice_tone",
        "synonyms": ["angry", "furious", "angry_es", "aggressive", "irritated_es"],
        "related": {
            "threat":       {"somatic": [],                                  "mental": ["cognitive_threat", "hypervigilance"]},
            "danger":       {"somatic": [],                                  "mental": ["anguish", "seek_exit"]},
            "fear":         {"somatic": [],                                  "mental": ["seek_person", "denial"]},
        }
    },
    "triste_tono": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "voice_tone",
        "synonyms": ["sad", "melancholic", "triste", "apagado"],
        "related": {
            "alone":        {"somatic": [],                                  "mental": ["loneliness", "sadness"]},
            "uncertainty":  {"somatic": [],                                  "mental": ["confusion", "anguish"]},
        }
    },
    "urgente": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "voice_tone",
        "synonyms": ["urgent", "alarmed", "alarmed", "apurado", "desesperado"],
        "related": {
            "danger":       {"somatic": [],                                  "mental": ["cognitive_threat", "seek_exit"]},
            "fear":         {"somatic": [],                                  "mental": ["hypervigilance", "anticipation"]},
        }
    },
    "neutral_tono": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "voice_tone",
        "synonyms": ["neutral", "calm_voice", "monotone"],
        "related": {
            "calm":         {"somatic": [],                                  "mental": ["clarity", "acceptance"]},
        }
    },

    # ── HEARING / TONE → mental + somatic ──────────────────────────────────────
    # Physical tone (dB, Hz) goes through db_receptors to the somatic cycle.
    # Here the semantic category for the mental engine is defined.
    "grito": {
        "sense":    "hearing",
        "type":     "tone_es",
        "subtype":  "volumen",
        "synonyms": ["scream", "shout", "yell", "alarido", "grito"],
        "related": {
            "danger":       {"somatic": ["adrenaline", "muscle_tension"],  "mental": ["cognitive_threat", "seek_exit"]},
            "fear":         {"somatic": ["cortisol", "noradrenaline"],       "mental": ["hypervigilance", "anguish"]},
            "threat":       {"somatic": ["adrenaline"],                      "mental": ["seek_person"]},
        }
    },
    "susurro": {
        "sense":    "hearing",
        "type":     "tone_es",
        "subtype":  "volumen",
        "synonyms": ["whisper", "murmur", "murmullo"],
        "related": {
            "uncertainty":  {"somatic": ["noradrenaline"],                   "mental": ["suspicion", "hypervigilance"]},
            "fear":         {"somatic": ["muscle_tension"],                "mental": ["anticipation"]},
        }
    },
    "silencio_auditivo": {
        "sense":    "hearing",
        "type":     "tone_es",
        "subtype":  "volumen",
        "synonyms": ["silence", "quiet_sound", "no_sound"],
        "related": {
            "calm":         {"somatic": ["silence", "body_calm"],        "mental": ["clarity"]},
            "uncertainty":  {"somatic": ["noradrenaline"],                   "mental": ["anticipation", "suspicion"]},
        }
    },

    # ── LANGUAGE / question ───────────────────────────────────────────────
    # Negative value — a question opens momentary absence (A rises, P falls)
    # The system searches for a response to close that opening
    "which": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "question_word",
        "synonyms": ["what", "which", "what-is", "what", "what_es", "what_es2"],
        "related": {
            "uncertainty":  {"somatic": [],  "mental": ["confusion", "anticipation"]},
            "search":       {"somatic": [],  "mental": ["seek_exit", "clarity"]},
        }
    },
    "who": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "question_word",
        "synonyms": ["who", "who"],
        "related": {
            "uncertainty":  {"somatic": [],  "mental": ["suspicion", "anticipation"]},
            "search":       {"somatic": [],  "mental": ["seek_person"]},
        }
    },
    "donde": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "question_word",
        "synonyms": ["where", "donde"],
        "related": {
            "uncertainty":  {"somatic": [],  "mental": ["confusion", "anticipation"]},
            "search":       {"somatic": [],  "mental": ["seek_exit"]},
        }
    },
    "como_pregunta": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "question_word",
        "synonyms": ["how"],
        "related": {
            "uncertainty":  {"somatic": [],  "mental": ["confusion", "clarity"]},
        }
    },

    # ── LANGUAGE / subject ─────────────────────────────────────────────────────
    "self": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "internal_subject",
        "synonyms": ["i", "me", "mi", "myself", "mio", "i'm", "im"],
        "related": {
            "identity":    {"somatic": [],  "mental": ["mental_security", "clarity"]},
            "name":       {"somatic": [],  "mental": ["clarity"]},
        }
    },
    "tu": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "external_subject",
        "synonyms": ["you", "your", "yours"],
        "related": {
            "identity":    {"somatic": [],  "mental": ["anticipation", "clarity"]},
            "social":       {"somatic": [],  "mental": ["seek_person"]},
        }
    },

    # ── LANGUAGE / VERB ───────────────────────────────────────────────────────
    "es": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "verb",
        "synonyms": ["am", "is", "are", "be", "called"],
        "related": {
            "identity":    {"somatic": [],  "mental": ["clarity", "acceptance"]},
        }
    },

    # ── LANGUAGE / property ──────────────────────────────────────────────────
    "name": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "property",
        "synonyms": ["name", "called", "julia"],
        "related": {
            "identity":    {"somatic": [],  "mental": ["clarity", "mental_security"]},
            "name":       {"somatic": [],  "mental": ["clarity"]},
        }
    },
    "identity": {
        "sense":    "hearing",
        "type":     "language",
        "subtype":  "property",
        "synonyms": ["identity", "who are you", "who am i"],
        "related": {
            "identity":    {"somatic": [],  "mental": ["clarity", "mental_security"]},
        }
    },

    "aggressive": {
        "sense":    "sight",
        "type":     "status",
        "subtype":  "threat",
        "synonyms": ["aggression", "aggressive", "aggressive_f", "hostile", "hostile_es", "violent"],
        "related": {
            "danger":      {"somatic": ["adrenaline", "noradrenaline", "muscle_tension"], "mental": ["cognitive_threat", "hypervigilance"]},
            "fear":        {"somatic": ["cortisol", "adrenaline"],                          "mental": ["hypervigilance", "anguish"]},
            "threat":      {"somatic": ["muscle_tension", "noradrenaline"],               "mental": ["cognitive_threat", "denial"]},
            "defenseless": {"somatic": ["paralysis"],                                        "mental": ["seek_exit"]},
        },
    },

    "face": {
        "sense":    "sight",
        "type":     "subject",
        "subtype":  "social",
        "synonyms": ["face_es", "face_alt", "expression", "expression_es"],
        "related": {
            "social":  {"somatic": ["serotonin"],       "mental": ["cognitive_calm"]},
            "threat":  {"somatic": ["muscle_tension"], "mental": ["hypervigilance"]},
            "fear":    {"somatic": ["cortisol"],         "mental": ["cognitive_threat"]},
        },
    },

    "tone": {
        "sense":    "hearing",
        "type":     "status",
        "subtype":  "social",
        "synonyms": ["tone_es", "voice", "voice_es", "tones"],
        "related": {
            "threat":  {"somatic": ["noradrenaline", "muscle_tension"], "mental": ["hypervigilance", "cognitive_threat"]},
            "social":  {"somatic": ["serotonin"],                        "mental": ["cognitive_calm"]},
        },
    },

}


# ── RESOLVERS ─────────────────────────────────────────────────────────────────

def resolve_concept(token):
    """Resolves raw token → canonical name in CONCEPTS."""
    token = token.lower().strip()
    if token in CONCEPTS:
        return token
    for name, c in CONCEPTS.items():
        if token in [s.lower() for s in c.get("synonyms", [])]:
            return name
    return None


def get_internal_activations(concept_names):
    """
    Given a list of scene concepts, returns:
      somatic_counts: {tag: count}  — how many times each somatic tag activates
      mental_counts:  {assoc: count} — how many times each mental association activates
    The multiplier of each activation = count (release x1, x2, x3...)
    """
    from collections import Counter
    somatic_counts = Counter()
    mental_counts  = Counter()

    for name in concept_names:
        c = CONCEPTS.get(name, {})
        for related_node, branches in c.get("related", {}).items():
            for tag in branches.get("somatic", []):
                somatic_counts[tag] += 1
            for assoc in branches.get("mental", []):
                mental_counts[assoc] += 1

    return dict(somatic_counts), dict(mental_counts)


def get_focus(concept_names):
    """Returns the highest-priority concept (focus) from the scene."""
    PRIORITY = ["illogical", "subject", "action", "status", "environment", "object"]
    STATUS_SUB = ["threat", "emotional", "physical", "social", "safety", "condition"]

    best_name, best_score = None, (999, 999)
    for name in concept_names:
        c = CONCEPTS.get(name, {})
        ctype   = c.get("type", "object")
        subtype = c.get("subtype", "")
        ts = PRIORITY.index(ctype) if ctype in PRIORITY else 999
        ss = STATUS_SUB.index(subtype) if (ctype == "status" and subtype in STATUS_SUB) else 999
        if (ts, ss) < best_score:
            best_score = (ts, ss)
            best_name  = name
    return best_name


def get_multiplier(focus_name, concept_names):
    """
    Counts related matches between the focus and the other concepts.
    Multiplicador = coincidencias + 1
    """
    focus = CONCEPTS.get(focus_name, {})
    focus_related = set(focus.get("related", {}).keys())
    if not focus_related:
        return 1

    coincidences = 0
    for name in concept_names:
        if name == focus_name:
            continue
        other_related = set(CONCEPTS.get(name, {}).get("related", {}).keys())
        coincidences += len(focus_related & other_related)

    return coincidences + 1
