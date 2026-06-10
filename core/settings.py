SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60
TITLE         = "CyberEscape"

# Colour palette — dark terminal / cyberpunk aesthetic
BG_DARK      = (10,  12,  20)
BG_MID       = (16,  20,  34)
BG_PANEL     = (22,  28,  46)
ACCENT_GREEN  = (0,   220, 100)
ACCENT_CYAN   = (0,   210, 255)
ACCENT_RED    = (255, 60,  80)
ACCENT_ORANGE = (255, 160, 0)
TEXT_PRIMARY  = (210, 225, 255)
TEXT_DIM      = (100, 118, 160)
TEXT_MUTED    = (55,  70,  105)
BORDER        = (38,  50,  85)
WHITE         = (255, 255, 255)
BLACK         = (0,   0,   0)

# Room registry — the ONLY place to register a room.
# Set available=True when its room.py is ready to play.
# World map reads this list; no other file needs changing when you add a room.
ROOMS = [
    {"id": "phishing", "number": 1, "title": "Phishing Lab",       "tier": 1, "available": False},
    {"id": "osint",    "number": 2, "title": "OSINT Investigator",  "tier": 1, "available": True},
    {"id": "password", "number": 3, "title": "Password Vault",      "tier": 2, "available": True},
    {"id": "cipher",   "number": 4, "title": "Cipher Chamber",      "tier": 2, "available": False},
    {"id": "network",  "number": 5, "title": "Network Recon",       "tier": 3, "available": False},
    {"id": "script",   "number": 6, "title": "Script Foundry",      "tier": 3, "available": False},
    {"id": "reverse",  "number": 7, "title": "Reverse Engineering",  "tier": 4, "available": False},
    {"id": "binary",   "number": 8, "title": "Binary Breach",       "tier": 4, "available": False},
]

SAVE_PATH = "save.json"

# Maps room id -> importable module path for rooms that have implementations.
# Add an entry here when a new room.py is created — nothing else changes.
ROOM_MODULE_MAP = {
    "osint":    "rooms.osint.room",
    "password": "rooms.password.room",
}
