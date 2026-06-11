SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60
TITLE         = "Memory0verwrite"
SAVE_PATH     = "memory0verwrite_save.json"

# ── Colour palette ─────────────────────────────────────────────────────────────
# Primary five: #11151c #30f2f2 #4cffdf #ff3377 #ff9f1c
BG_DARK      = (17,  21,  28)    # #11151c  deep navy-black
BG_MID       = (22,  28,  40)    # slightly lighter chrome
BG_PANEL     = (30,  38,  55)    # card / panel background
ACCENT_GREEN  = (76,  255, 223)  # #4cffdf  mint teal — success / confirm
ACCENT_CYAN   = (48,  242, 242)  # #30f2f2  bright cyan — info / highlight
ACCENT_RED    = (255, 51,  119)  # #ff3377  hot pink   — error / danger
ACCENT_ORANGE = (255, 159, 28)   # #ff9f1c  amber      — warning / intel
ACCENT_YELLOW = (255, 220, 0)
ACCENT_GOLD   = (200, 160, 0)    # recovered memory / cleared state
TEXT_PRIMARY  = (205, 230, 255)  # cool blue-white
TEXT_DIM      = (80,  110, 155)  # muted blue
TEXT_MUTED    = (42,  58,  88)   # very muted
BORDER        = (40,  54,  88)   # subtle blue border
WHITE         = (255, 255, 255)
BLACK         = (0,   0,   0)

# ── Gameplay ───────────────────────────────────────────────────────────────────
ROOM_TIMER_SECONDS = 600   # 10-minute countdown per room

# ── Room registry ─────────────────────────────────────────────────────────────
ROOMS = [
    {
        "id":              "phishing",
        "number":          1,
        "title":           "Phishing Lab",
        "tier":            1,
        "available":       False,
        "teaser":          "An inbox full of traps. Learn to read between the lines.",
        "concept":         "Social engineering via email",
        "narrative": (
            "Social engineering exploits trust, not technology. An inbox full of messages — "
            "some legitimate, some traps. Your task: identify the fakes before someone clicks "
            "the wrong link. In the real world, 90% of breaches start here."
        ),
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
        "narrative": (
            "A digital footprint is never fully erased. Somewhere across the open web, "
            "a target named n3uroph0x has left fragments of identity. Your task: gather, "
            "cross-reference, and reconstruct. This is how investigators build threat "
            "profiles before a breach becomes a crisis."
        ),
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
        "narrative": (
            "The vault has been breached before. Weak keys, cracked hashes, predictable "
            "patterns — every weakness is a door. Your task: understand every mechanism "
            "of attack, then build the one lock that holds. "
            "Knowledge is the only key that matters."
        ),
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
        "narrative": (
            "Every message hides another. Caesar shifted his secrets. Vigenère obscured hers. "
            "Modern encryption protects billions of transactions daily. Your task: "
            "break the codes of the past to understand the foundations of the present."
        ),
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
        "narrative": (
            "Every open port is a door. Every running service is a window. "
            "The network breathes — and a skilled investigator listens. "
            "Your task: map the attack surface before the attacker does. "
            "Reconnaissance is where every breach begins."
        ),
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
        "narrative": (
            "Manual attacks are limited by human speed. Scripts are not. "
            "A few lines of Python become a force multiplier — automating reconnaissance, "
            "testing credentials, probing defenses. "
            "Your task: write the tools that the professionals write."
        ),
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
        "narrative": (
            "Compiled code still speaks, if you know the language. Strip away the interface. "
            "Read the assembly. Understand what the machine was instructed to do. "
            "Sometimes the vulnerability is written into the logic itself."
        ),
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
        "narrative": (
            "This is the final boundary. The virus lives in the overflow — "
            "in the corrupted stack frame, in the unchecked buffer. Exploit it. "
            "Corrupt it back. You have come too far to fail at the last door."
        ),
        "memory_fragment": None,
    },
]

# Maps room id -> importable module path.
ROOM_MODULE_MAP = {
    "osint":    "rooms.osint.room",
    "password": "rooms.password.room",
}
