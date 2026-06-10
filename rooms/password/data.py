# All puzzle content for Room 3 — Password Vault (4 phases).

PUZZLE: dict = {

    # ── Phase 1: Dictionary Attack ────────────────────────────────────────────
    "phase1": {
        "title":    "Phase 1 of 4  —  Dictionary Attack",
        "headline": "Cracking a weak password",
        "briefing": (
            "Attackers don't guess randomly — they try thousands of common "
            "passwords automatically using a wordlist. "
            "A weak password falls in milliseconds."
        ),
        "target_account": "alex.morgan@techvault.io",
        "wordlist": [
            "123456", "password", "qwerty123", "letmein",
            "sunshine", "admin123", "welcome1", "monkey",
            "sunshine2019", "iloveyou", "princess", "dragon",
            "master", "pass1234", "hello123",
        ],
        "answer": "sunshine2019",
        "teach_line": (
            "Over 23 million accounts used '123456' in real data breaches. "
            "Dictionary attacks crack passwords like these in under a second."
        ),
    },

    # ── Phase 2: Hash Cracking ────────────────────────────────────────────────
    "phase2": {
        "title":    "Phase 2 of 4  —  Hash Cracking",
        "headline": "Breaking a stored password hash",
        "briefing": (
            "Passwords are stored as hashes — not plaintext. "
            "Hashing is one-way: you cannot reverse it. "
            "But attackers precompute hashes for common passwords (rainbow tables)."
        ),
        "target_hash": "5f4dcc3b5aa765d61d8327deb882cf99",
        "rainbow_table": [
            {"plain": "123456",    "hash": "e10adc3949ba59abbe56e057f20f883e"},
            {"plain": "password",  "hash": "5f4dcc3b5aa765d61d8327deb882cf99"},
            {"plain": "qwerty",    "hash": "d8578edf8458ce06fbc5bb76a58c5ca4"},
            {"plain": "letmein",   "hash": "0d107d09f5bbe40cade3de5c71e9e9b7"},
            {"plain": "admin",     "hash": "21232f297a57a5a743894a0e4a801fc3"},
            {"plain": "welcome",   "hash": "40be4e59b9a2a2b5dffb918c0e86b3d7"},
            {"plain": "sunshine",  "hash": "d8b07c2d7d98ae3a00b7d12e8c7e4432"},
            {"plain": "master",    "hash": "9e6a80d68e7e97f44cba7e84d77f9d88"},
        ],
        "answer_index": 1,   # "password" row
        "teach_line": (
            "MD5 hashes are irreversible — but rainbow tables map known "
            "hashes back to plaintext instantly. Weak passwords offer no protection."
        ),
    },

    # ── Phase 3: Salting ──────────────────────────────────────────────────────
    "phase3": {
        "title":    "Phase 3 of 4  —  Salting",
        "headline": "Why identical passwords have different hashes",
        "briefing": (
            "A 'salt' is random data added to a password before hashing. "
            "This means two users with the same password get completely different hashes — "
            "and rainbow tables become useless."
        ),
        "users": [
            {
                "username": "alice",
                "password": "letmein",
                "salt":     None,
                "hash":     "0d107d09f5bbe40cade3de5c71e9e9b7",
            },
            {
                "username": "bob",
                "password": "letmein",
                "salt":     "x7kQ9#",
                "hash":     "c4f2e31a8b90d5f7",   # display-only fake
            },
        ],
        "question": (
            "Alice and Bob use the exact same password. "
            "Why are their stored hashes different?"
        ),
        "choices": [
            "They are actually using different passwords",
            "Bob's record includes a unique salt value",
            "The hashing algorithm produced an error",
            "The hashes will match once the system syncs",
        ],
        "answer_index": 1,
        "teach_line": (
            "Salting defeats rainbow tables entirely. "
            "Modern systems use bcrypt, scrypt, or Argon2 — "
            "algorithms designed specifically to be slow and include built-in salting."
        ),
    },

    # ── Phase 4: Fortify ──────────────────────────────────────────────────────
    "phase4": {
        "title":    "Phase 4 of 4  —  Fortify the Vault",
        "headline": "Build a password that cannot be cracked",
        "briefing": (
            "Now you understand how attacks work. "
            "Build a password that defeats a dictionary attack, "
            "rainbow tables, and brute force."
        ),
        "requirements": [
            {"key": "length12", "label": "At least 12 characters"},
            {"key": "upper",    "label": "At least one UPPERCASE letter"},
            {"key": "digit",    "label": "At least one number  (0-9)"},
            {"key": "symbol",   "label": "At least one symbol  (!@#$%^&*...)"},
        ],
        "strength_labels": [
            "Cracked instantly",
            "Very Weak",
            "Weak",
            "Fair",
            "Strong",
            "Very Strong",
        ],
        "strength_colors": [
            (220, 50,  50),    # 0 — instant
            (220, 80,  40),    # 1 — very weak
            (220, 130, 30),    # 2 — weak
            (200, 180, 20),    # 3 — fair
            (80,  200, 80),    # 4 — strong
            (0,   220, 100),   # 5 — very strong
        ],
        "teach_line": (
            "Length beats complexity. 'Tr0uble-sh00ting#2024' is both "
            "memorable and has ~72 bits of entropy — "
            "it would take centuries to brute-force at a billion guesses/second."
        ),
        "required_strength": 4,   # player must reach at least "Strong"
    },

    "score_per_phase":         100,
    "max_score":               400,
    "result_display_seconds":  4.0,
}
