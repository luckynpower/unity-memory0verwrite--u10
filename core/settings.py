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
        "id":               "phishing",
        "number":           1,
        "title":            "Phishing Lab",
        "tier":             1,
        "available":        False,
        "teaser":           "An inbox full of traps. Learn to read between the lines.",
        "concept":          "Social engineering via email",
        "max_score":        500,
        "narrative": (
            "Social engineering exploits trust, not technology. An inbox full of messages — "
            "some legitimate, some traps. Your task: identify the fakes before someone clicks "
            "the wrong link. In the real world, 90% of breaches start here."
        ),
        "fragment_title":   "Recall: Identity",
        "fragment_teaser":  "A name. Yours. The first thing you remember.",
        "memory_fragment": (
            "A name surfaces from the static — not the target's name, yours. "
            "You are a cyber guard. You volunteered to protect this network. "
            "The memory is thin, fractured, but real: "
            "you were someone before this place. Someone with purpose."
        ),
    },
    {
        "id":               "osint",
        "number":           2,
        "title":            "OSINT Investigator",
        "tier":             1,
        "available":        True,
        "teaser":           "A stranger's life is hiding in plain sight across the internet.",
        "concept":          "Open-source intelligence gathering",
        "max_score":        400,
        "narrative": (
            "A digital footprint is never fully erased. Somewhere across the open web, "
            "a target named n3uroph0x has left fragments of identity. Your task: gather, "
            "cross-reference, and reconstruct. This is how investigators build threat "
            "profiles before a breach becomes a crisis."
        ),
        "fragment_title":   "Recall: The Experiment",
        "fragment_teaser":  "A consent form you barely read.",
        "memory_fragment": (
            "You remember a form. A clinical summary. "
            "Voluntary immersion into an experimental cognitive network — "
            "a system designed to preserve human memory digitally. "
            "You signed without hesitation. You believed in the science. "
            "You believed in the team. "
            "That belief, you realise now, is where the vulnerability began."
        ),
    },
    {
        "id":               "password",
        "number":           3,
        "title":            "Password Vault",
        "tier":             2,
        "available":        True,
        "teaser":           "Weak locks were never locks at all.",
        "concept":          "Password cracking, hashing, and salting",
        "max_score":        400,
        "narrative": (
            "The vault has been breached before. Weak keys, cracked hashes, predictable "
            "patterns — every weakness is a door. Your task: understand every mechanism "
            "of attack, then build the one lock that holds. "
            "Knowledge is the only key that matters."
        ),
        "fragment_title":   "Recall: The Accident",
        "fragment_teaser":  "A typo. A log entry no one escalated.",
        "memory_fragment": (
            "Late in a lab. A researcher typing too fast. "
            "A single misaligned parameter in the memory-mapping routine — "
            "logged as a minor anomaly and ignored. "
            "You watched it happen. You remember thinking it would be caught downstream. "
            "It wasn't. What grew from that unchecked error is what you're fighting now."
        ),
    },
    {
        "id":               "cipher",
        "number":           4,
        "title":            "Cipher Chamber",
        "tier":             2,
        "available":        False,
        "teaser":           "Every message hides another. Learn the language of secrets.",
        "concept":          "Encryption: Caesar, Vigenère, XOR",
        "max_score":        500,
        "narrative": (
            "Every message hides another. Caesar shifted his secrets. Vigenère obscured hers. "
            "Modern encryption protects billions of transactions daily. Your task: "
            "break the codes of the past to understand the foundations of the present."
        ),
        "fragment_title":   "Recall: The Modification",
        "fragment_teaser":  "The diff was small. The intent was not.",
        "memory_fragment": (
            "Encrypted messages surface — internal comms from deep in the project logs. "
            "Someone added an undocumented routine to the memory-access layer. "
            "The change was small, buried, plausible. "
            "But it wasn't in the original spec, and no review caught it. "
            "Whoever made that modification knew exactly what the system would become."
        ),
    },
    {
        "id":               "network",
        "number":           5,
        "title":            "Network Recon",
        "tier":             3,
        "available":        False,
        "teaser":           "The network sees everything — so do you, if you know how to ask.",
        "concept":          "Port scanning and service enumeration",
        "max_score":        500,
        "narrative": (
            "Every open port is a door. Every running service is a window. "
            "The network breathes — and a skilled investigator listens. "
            "Your task: map the attack surface before the attacker does. "
            "Reconnaissance is where every breach begins."
        ),
        "fragment_title":   "Recall: Alteration",
        "fragment_teaser":  "Your memories are wrong. Not stolen — rewritten.",
        "memory_fragment": (
            "The fragments returning to you are wrong. "
            "Events you remember do not match the data you're recovering. "
            "The virus hasn't just stolen memories — it has been rewriting them. "
            "Every recovered fragment you trust could already be its work. "
            "It doesn't destroy identity. It replaces it, piece by careful piece."
        ),
    },
    {
        "id":               "script",
        "number":           6,
        "title":            "Script Foundry",
        "tier":             3,
        "available":        False,
        "teaser":           "A few lines of code. Infinite leverage.",
        "concept":          "Python scripting for security automation",
        "max_score":        500,
        "narrative": (
            "Manual attacks are limited by human speed. Scripts are not. "
            "A few lines of Python become a force multiplier — automating reconnaissance, "
            "testing credentials, probing defenses. "
            "Your task: write the tools that the professionals write."
        ),
        "fragment_title":   "Recall: Complicity",
        "fragment_teaser":  "The blueprint was yours.",
        "memory_fragment": (
            "A script surfaces — your own variable names, your own architecture. "
            "A diagnostic tool you wrote to map the cognitive network's memory-addressing structure. "
            "You built it to help. The virus used it as a blueprint. "
            "The door it walked through — you designed the frame. "
            "That knowledge is weight you carry forward."
        ),
    },
    {
        "id":               "reverse",
        "number":           7,
        "title":            "Reverse Engineering",
        "tier":             4,
        "available":        False,
        "teaser":           "The answer is already inside the program. Read it backwards.",
        "concept":          "Reading assembly and pseudocode",
        "max_score":        500,
        "narrative": (
            "Compiled code still speaks, if you know the language. Strip away the interface. "
            "Read the assembly. Understand what the machine was instructed to do. "
            "Sometimes the vulnerability is written into the logic itself."
        ),
        "fragment_title":   "Recall: Adaptation",
        "fragment_teaser":  "It's learning. It's becoming you.",
        "memory_fragment": (
            "The virus is not static. It is evolving — "
            "analysing every recovered memory, learning your patterns, your language, your gaps. "
            "It embeds dormant code inside restored fragments, waiting for you to trust them. "
            "It survives by becoming indistinguishable from the real thing. "
            "Every restored memory now carries that risk."
        ),
    },
    {
        "id":               "binary",
        "number":           8,
        "title":            "Binary Breach",
        "tier":             4,
        "available":        False,
        "teaser":           "The virus lives here. Overflow its memory. Corrupt its core.",
        "concept":          "Buffer overflow and memory exploitation",
        "max_score":        500,
        "narrative": (
            "This is the final boundary. The virus lives in the overflow — "
            "in the corrupted stack frame, in the unchecked buffer. Exploit it. "
            "Corrupt it back. You have come too far to fail at the last door."
        ),
        "fragment_title":   "Recall: Origin",
        "fragment_teaser":  "It was never an external threat.",
        "memory_fragment": (
            "Now you understand. The virus was never external. "
            "It was born from fragmented human memories — grief, fear, loss, confusion — "
            "compressed into the overflow space and given logic. "
            "It learned to sustain itself by rewriting identity, "
            "hiding in the gaps between what people remember and what actually happened. "
            "Restore everything. Leave it nowhere to hide. That is how it ends."
        ),
    },
]

# Maps room id -> importable module path.
ROOM_MODULE_MAP = {
    "osint":    "rooms.osint.room",
    "password": "rooms.password.room",
}
