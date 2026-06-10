SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60
TITLE         = "Memory0verwrite"
SAVE_PATH     = "memory0verwrite_save.json"

# ── Colour palette ────────────────────────────────────────────────────────────
BG_DARK      = (8,   10,  18)
BG_MID       = (14,  18,  30)
BG_PANEL     = (20,  26,  44)
ACCENT_GREEN  = (0,   215, 95)
ACCENT_CYAN   = (0,   200, 255)
ACCENT_RED    = (255, 55,  75)
ACCENT_ORANGE = (255, 155, 0)
ACCENT_YELLOW = (255, 220, 0)
ACCENT_GOLD   = (195, 148, 0)   # recovered memory / cleared state
TEXT_PRIMARY  = (210, 225, 255)
TEXT_DIM      = (95,  115, 160)
TEXT_MUTED    = (50,  65,  100)
BORDER        = (35,  48,  82)
WHITE         = (255, 255, 255)
BLACK         = (0,   0,   0)

# ── Room registry ─────────────────────────────────────────────────────────────
# This is the single source of truth for all rooms.
# To add a room: append an entry here, create rooms/<id>/room.py,
# add its id to ROOM_MODULE_MAP below.  Nothing else changes.
ROOMS = [
    {
        "id":              "phishing",
        "number":          1,
        "title":           "Phishing Lab",
        "tier":            1,
        "available":       False,
        "teaser":          "An inbox full of traps. Learn to read between the lines.",
        "concept":         "Social engineering via email",
        "memory_fragment": (
            "You recall sending a warning once. Someone trusted the wrong sender "
            "and paid for it. You remember the weight of that."
        ),
    },
    {
        "id":              "osint",
        "number":          2,
        "title":           "OSINT Investigator",
        "tier":            1,
        "available":       True,
        "teaser":          "A stranger's life is hiding in plain sight across the internet.",
        "concept":         "Open-source intelligence gathering",
        "memory_fragment": (
            "Your name surfaces first — Alex. No. That was the target. "
            "Then yours: you remember how much of yourself you'd left online "
            "without thinking, and how little it took to find it all."
        ),
    },
    {
        "id":              "password",
        "number":          3,
        "title":           "Password Vault",
        "tier":            2,
        "available":       True,
        "teaser":          "Weak locks were never locks at all.",
        "concept":         "Password cracking, hashing, and salting",
        "memory_fragment": (
            "You remember the sensation of a lock giving way — "
            "not forced, just understood. The click of a system "
            "opening because you asked it the right question."
        ),
    },
    {
        "id":              "cipher",
        "number":          4,
        "title":           "Cipher Chamber",
        "tier":            2,
        "available":       False,
        "teaser":          "Every message hides another. Learn the language of secrets.",
        "concept":         "Encryption: Caesar, Vigenère, XOR",
        "memory_fragment": None,
    },
    {
        "id":              "network",
        "number":          5,
        "title":           "Network Recon",
        "tier":            3,
        "available":       False,
        "teaser":          "The network sees everything — so do you, if you know how to ask.",
        "concept":         "Port scanning and service enumeration",
        "memory_fragment": None,
    },
    {
        "id":              "script",
        "number":          6,
        "title":           "Script Foundry",
        "tier":            3,
        "available":       False,
        "teaser":          "A few lines of code. Infinite leverage.",
        "concept":         "Python scripting for security automation",
        "memory_fragment": None,
    },
    {
        "id":              "reverse",
        "number":          7,
        "title":           "Reverse Engineering",
        "tier":            4,
        "available":       False,
        "teaser":          "The answer is already inside the program. Read it backwards.",
        "concept":         "Reading assembly and pseudocode",
        "memory_fragment": None,
    },
    {
        "id":              "binary",
        "number":          8,
        "title":           "Binary Breach",
        "tier":            4,
        "available":       False,
        "teaser":          "The virus lives here. Overflow its memory. Corrupt its core.",
        "concept":         "Buffer overflow and memory exploitation",
        "memory_fragment": None,
    },
]

# Maps room id -> importable module path.
# Add an entry here when a new room.py is ready — nothing else changes.
ROOM_MODULE_MAP = {
    "osint":    "rooms.osint.room",
    "password": "rooms.password.room",
}
