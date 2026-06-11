# Puzzle content for Room 2 — OSINT Investigator.
# Three evidence sources lead to four dossier fields.

PUZZLE: dict = {
    "target_username": "n3uroph0x",

    # ── Evidence 1: Photo metadata ─────────────────────────────────────────────
    "photo": {
        "filename": "profile_photo_2024.jpg",
        "caption":  '"Just another morning commute."',
        "metadata": [
            ("File name",       "profile_photo_2024.jpg"),
            ("Device",          "iPhone 14 Pro"),
            ("Date taken",      "2024-10-12   08:23:14"),
            ("GPS coordinates", "51.5074° N,  0.1278° W"),
            ("Location",        "London, United Kingdom"),
            ("Timezone",        "Europe/London  (GMT+0)"),
            ("Software",        "iOS 17.0.3"),
            ("Resolution",      "4032 × 3024"),
        ],
    },

    # ── Evidence 2: Social media posts ────────────────────────────────────────
    "social_platforms": [
        {
            "name":         "Chirp",
            "handle":       "@n3uroph0x",
            "display_name": "Alex M.",
            "color":        (29, 161, 242),
            "posts": [
                {
                    "text":      "Biscuit knocked my coffee off the desk this morning. Absolute chaos. Zero remorse.",
                    "timestamp": "Sat  09:14 GMT",
                },
                {
                    "text":      "Morning commute again. District line never disappoints with delays.",
                    "timestamp": "Mon  08:23 GMT",
                    "highlight": False,
                },
            ],
        },
        {
            "name":         "Facenet",
            "handle":       "n3uroph0x",
            "display_name": "Alex Morgan",
            "color":        (66, 103, 178),
            "posts": [
                {
                    "text":      "Working in tech, based in London. Coffee and cats.",
                    "timestamp": "profile bio",
                    "highlight": False,
                },
                {
                    "text":      "Does anyone else take the District line into Canary Wharf daily? Delays are character-building apparently.",
                    "timestamp": "3 days ago",
                    "highlight": False,
                },
            ],
        },
        {
            "name":         "GearTalk Forum",
            "handle":       "n3uroph0x",
            "display_name": "n3uroph0x",
            "color":        (180, 90, 0),
            "posts": [
                {
                    "text":      "Anyone in London going to BSides next month?",
                    "timestamp": "2024-10-15  14:52 GMT",
                    "highlight": False,
                },
            ],
        },
    ],

    # ── Evidence 3: Username reuse ─────────────────────────────────────────────
    "username_accounts": [
        {"platform": "Chirp",    "handle": "@n3uroph0x",  "real_name": "Alex M.",     "color": (29, 161, 242)},
        {"platform": "Facenet",  "handle": "n3uroph0x",   "real_name": "Alex Morgan", "color": (66, 103, 178)},
        {"platform": "GearTalk", "handle": "n3uroph0x",   "real_name": "n3uroph0x",   "color": (180, 90, 0)},
    ],

    # ── Dossier fields ─────────────────────────────────────────────────────────
    # answer      : accepted text (case-insensitive)
    # flexible    : if True, any word >3 chars from the answer counts as correct
    # easter_egg  : if True, value saved as artefact for Room 3
    # hints       : [vague, specific]
    "dossier_fields": [
        {
            "key":        "name",
            "label":      "Full Name",
            "answer":     "Alex Morgan",
            "flexible":   False,
            "easter_egg": False,
            "hints": [
                "Check profiles that display real names, not just usernames.",
                "Facenet shows a display name alongside the handle n3uroph0x.",
            ],
        },
        {
            "key":        "location",
            "label":      "Location",
            "answer":     "London",
            "flexible":   False,
            "easter_egg": False,
            "hints": [
                "Location clues appear in more than one source.",
                "The photo GPS resolves to a specific city. Facenet and GearTalk confirm it.",
            ],
        },
        {
            "key":        "timezone",
            "label":      "Timezone",
            "answer":     "GMT",
            "flexible":   True,
            "easter_egg": False,
            "hints": [
                "Post timestamps include a timezone abbreviation.",
                "The photo EXIF data shows a Timezone field explicitly.",
            ],
        },
        {
            "key":        "pet_name",
            "label":      "Pet Name",
            "answer":     "Biscuit",
            "flexible":   False,
            "easter_egg": True,
            "hints": [
                "People often mention their pets casually in social posts.",
                "There is a Chirp post about a very mischievous cat.",
            ],
        },
    ],

    "score_per_field":         100,
    "max_score":               400,
    "result_display_seconds":  4.0,
    "easter_egg_artefact_key": "pet_name",
}
