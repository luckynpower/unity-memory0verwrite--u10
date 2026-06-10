# All puzzle content for Room 2.
# Room logic in room.py reads this dict — no code changes needed to adjust clues.

PUZZLE: dict = {
    "target_username": "n3uroph0x",

    "objective_header": "Find five pieces of information about the target.",
    "objective_items":  ["Full Name", "Employer", "City", "Daily Routine", "Pet Name"],

    "platforms": {
        "chirp": {
            "label": "Chirp  (social)",
            "color": (29, 161, 242),
            "profile": {
                "handle":       "@n3uroph0x",
                "display_name": "Alex M.",
                "bio":          "Infosec enthusiast | cat parent to Biscuit | opinions my own",
                "joined":       "Joined January 2020",
                "followers":    89,
                "following":    312,
            },
            "posts": [
                {
                    "text":      "Morning commute again. District line never disappoints with delays.",
                    "timestamp": "Mon  08:23 GMT",
                    "clue_key":  "routine",
                },
                {
                    "text":      "Lunch near the office. November sun, who knew.",
                    "timestamp": "Mon  12:31 GMT",
                    "clue_key":  "routine",
                },
                {
                    "text":      "Biscuit knocked my coffee off the desk. Zero remorse.",
                    "timestamp": "Sat  09:14 GMT",
                    "clue_key":  "pet_name",
                },
                {
                    "text":      "First week done at TechVault! New chapter.",
                    "timestamp": "Fri  18:05 GMT",
                    "clue_key":  "employer",
                },
            ],
        },

        "facenet": {
            "label": "Facenet  (social)",
            "color": (66, 103, 178),
            "profile": {
                "handle":       "n3uroph0x",
                "display_name": "Alex Morgan",
                "bio":          "Working in tech, based in London. Coffee and cats.",
                "location":     "London, UK",
                "employer":     "TechVault Solutions",
                "education":    "University of Edinburgh",
                "joined":       "Member since 2018",
            },
            "posts": [
                {
                    "text":      "Does anyone else take the District line into Canary Wharf daily? "
                                 "Delays are character-building apparently.",
                    "timestamp": "3 days ago",
                    "clue_key":  "location",
                },
                {
                    "text":      "Shoutout to TechVault Solutions for the welcome cake on day one.",
                    "timestamp": "2 weeks ago",
                    "clue_key":  "employer",
                },
            ],
        },

        "prolink": {
            "label": "ProLink  (professional)",
            "color": (0, 119, 181),
            "profile": {
                "handle":       "alex-morgan-infosec",
                "display_name": "Alex Morgan",
                "headline":     "Junior Security Analyst at TechVault Solutions",
                "location":     "Greater London, UK",
                "about":        "Blue team ops, threat intelligence, CTF enthusiast.",
                "experience": [
                    {"title": "Junior Security Analyst",
                     "company":  "TechVault Solutions", "duration": "Oct 2024 - Present"},
                    {"title": "IT Support Technician",
                     "company":  "Redbridge Council",   "duration": "2022 - 2024"},
                ],
                "education": [
                    {"degree": "BSc Computer Science",
                     "institution": "University of Edinburgh", "year": "2022"},
                ],
            },
            "posts": [],
        },

        "geartalk": {
            "label": "GearTalk Forum",
            "color": (180, 90, 0),
            "profile": {
                "handle":      "n3uroph0x",
                "display_name": "n3uroph0x",
                "bio":         "Long-time lurker, occasional poster.",
                "joined":      "Registered 2021-03-14",
                "post_count":  47,
            },
            "posts": [
                {
                    "text":      "[REVIEW] Logitech MX Keys - solid for long sessions, "
                                 "though I mostly use it at the TechVault office.",
                    "timestamp": "2024-11-02  09:17 GMT",
                    "clue_key":  "employer",
                },
                {
                    "text":      "Anyone in London going to BSides next month?",
                    "timestamp": "2024-10-15  14:52 GMT",
                    "clue_key":  "location",
                },
            ],
        },
    },

    # ── Dossier fields ────────────────────────────────────────────────────────
    # answer      : accepted text (case-insensitive contains-match)
    # flexible    : if True, any word > 3 chars in the answer counts
    # easter_egg  : if True, value saved as artefact for Room 3
    # hints       : list of 2 strings — vague then specific
    # ─────────────────────────────────────────────────────────────────────────
    "dossier_fields": [
        {
            "key":         "full_name",
            "label":       "Full Name",
            "answer":      "Alex Morgan",
            "flexible":    False,
            "easter_egg":  False,
            "hints": [
                "Check profiles that display real names, not usernames.",
                "Look at Facenet and ProLink — both show the full name.",
            ],
        },
        {
            "key":         "employer",
            "label":       "Employer",
            "answer":      "TechVault Solutions",
            "flexible":    False,
            "easter_egg":  False,
            "hints": [
                "Look for mentions of a workplace across all platforms.",
                "The target posted about starting a new job. Check Chirp and Facenet.",
            ],
        },
        {
            "key":         "location",
            "label":       "City",
            "answer":      "London",
            "flexible":    False,
            "easter_egg":  False,
            "hints": [
                "Location clues appear on more than one platform.",
                "Facenet lists a location directly. Geartalk confirms it too.",
            ],
        },
        {
            "key":         "routine",
            "label":       "Daily Routine",
            "answer":      "district line commute lunch 12:30",
            "flexible":    True,
            "easter_egg":  False,
            "hints": [
                "Timestamps on posts reveal when and where someone is active.",
                "Two Chirp posts — one at 08:23, one at 12:31 — show a commute and a lunch break.",
            ],
        },
        {
            "key":         "pet_name",
            "label":       "Pet Name",
            "answer":      "Biscuit",
            "flexible":    False,
            "easter_egg":  True,
            "hints": [
                "People often mention their pets without thinking. Read bios carefully.",
                "The Chirp bio mentions a cat by name.",
            ],
        },
    ],

    "score_per_field":         100,
    "max_score":               500,
    "result_display_seconds":  4.0,
    "easter_egg_artefact_key": "pet_name",
}
