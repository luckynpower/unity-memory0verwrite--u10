# All puzzle content for Room 2 is defined here as plain data.
# The room module reads this dict — adding new clues or tweaking answers
# never requires touching room.py.

PUZZLE: dict = {
    "target_username": "n3uroph0x",

    "intro_lines": [
        "TARGET USERNAME : n3uroph0x",
        "OBJECTIVE       : Build a complete profile using only public data.",
        "METHOD          : Browse platforms. Every post is evidence.",
    ],

    # --- platforms -----------------------------------------------------------
    # Each platform has a profile dict and a list of posts.
    # post fields:  text, timestamp, clue (internal tag, not shown to player)
    # -------------------------------------------------------------------------
    "platforms": {
        "chirp": {
            "label": "Chirp",
            "color": (29, 161, 242),
            "profile": {
                "handle":       "@n3uroph0x",
                "display_name": "Alex M.",
                "bio":          "Infosec enthusiast | cat parent to Biscuit | opinions my own",
                "location":     "",
                "joined":       "Joined January 2020",
                "followers":    89,
                "following":    312,
            },
            "posts": [
                {
                    "text":      "Morning commute again. District line never disappoints with the delays.",
                    "timestamp": "Mon 08:23 GMT",
                    "clue":      "timezone_gmt",
                },
                {
                    "text":      "Lunch near the office. This weather is unreal for November.",
                    "timestamp": "Mon 12:31 GMT",
                    "clue":      "routine_lunch",
                },
                {
                    "text":      "Biscuit knocked my coffee off the desk again. Zero remorse.",
                    "timestamp": "Sat 09:14 GMT",
                    "clue":      "pet_name",
                },
                {
                    "text":      "Got the new role at TechVault! First week done.",
                    "timestamp": "Fri 18:05 GMT",
                    "clue":      "employer",
                },
            ],
        },

        "facenet": {
            "label": "Facenet",
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
                    "text":      "Anyone else take the District line into Canary Wharf every day? "
                                 "The delays are giving me character.",
                    "timestamp": "3 days ago",
                    "clue":      "location_london",
                },
                {
                    "text":      "Shoutout to TechVault Solutions for the welcome cake on day one.",
                    "timestamp": "2 weeks ago",
                    "clue":      "employer_confirm",
                },
            ],
        },

        "prolink": {
            "label": "ProLink",
            "color": (0, 119, 181),
            "profile": {
                "handle":       "alex-morgan-infosec",
                "display_name": "Alex Morgan",
                "headline":     "Junior Security Analyst at TechVault Solutions",
                "location":     "Greater London, UK",
                "about":        "Blue team ops and threat intelligence. CTF enthusiast.",
                "experience": [
                    {
                        "title":    "Junior Security Analyst",
                        "company":  "TechVault Solutions",
                        "duration": "Oct 2024 - Present",
                    },
                    {
                        "title":    "IT Support Technician",
                        "company":  "Redbridge Council",
                        "duration": "2022 - 2024",
                    },
                ],
                "education": [
                    {
                        "degree":      "BSc Computer Science",
                        "institution": "University of Edinburgh",
                        "year":        "2022",
                    },
                ],
            },
            "posts": [],
        },

        "geartalk": {
            "label": "GearTalk Forum",
            "color": (180, 90, 0),
            "profile": {
                "handle":      "n3uroph0x",
                "display_name":"n3uroph0x",
                "bio":         "Long-time lurker, occasional poster.",
                "joined":      "Registered 2021-03-14",
                "post_count":  47,
            },
            "posts": [
                {
                    "text":      "[REVIEW] Logitech MX Keys - solid for long sessions, "
                                 "though I mostly use it at the TechVault office.",
                    "timestamp": "2024-11-02 09:17 GMT",
                    "clue":      "employer_geartalk",
                },
                {
                    "text":      "Anyone in London going to BSides next month?",
                    "timestamp": "2024-10-15 14:52 GMT",
                    "clue":      "location_geartalk",
                },
            ],
        },
    },

    # --- dossier fields ------------------------------------------------------
    # answer       : expected text (checked case-insensitively)
    # flexible     : if True, any single answer word of len>3 counts as correct
    # easter_egg   : if True, the value is saved as an artefact for Room 3
    # source_hint  : hint shown next to the field label
    # -------------------------------------------------------------------------
    "dossier_fields": [
        {
            "key":         "full_name",
            "label":       "Full Name",
            "answer":      "Alex Morgan",
            "flexible":    False,
            "easter_egg":  False,
            "source_hint": "Check Facenet or ProLink",
        },
        {
            "key":         "employer",
            "label":       "Employer",
            "answer":      "TechVault Solutions",
            "flexible":    False,
            "easter_egg":  False,
            "source_hint": "Mentioned on multiple platforms",
        },
        {
            "key":         "location",
            "label":       "City / Location",
            "answer":      "London",
            "flexible":    False,
            "easter_egg":  False,
            "source_hint": "Where does the target live and work?",
        },
        {
            "key":         "routine",
            "label":       "Daily Routine",
            "answer":      "district line commute lunch 12:30",
            "flexible":    True,
            "easter_egg":  False,
            "source_hint": "Look at timestamps and transport mentions",
        },
        {
            "key":         "pet_name",
            "label":       "Pet Name",
            "answer":      "Biscuit",
            "flexible":    False,
            "easter_egg":  True,
            "source_hint": "Read the bio and posts carefully",
        },
    ],

    "score_per_field": 100,
    "max_score":       500,

    # How long the result overlay stays on screen before completing the room
    "result_display_seconds": 4.0,
}
