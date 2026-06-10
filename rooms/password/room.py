"""
Room 3 — Password Vault  (4 sequential phases, redesigned).

Phase 1 — Dictionary Attack  : watch wordlist scan, NEXT PHASE when cracked
Phase 2 — Hash Cracking      : two-column layout (info + table)
Phase 3 — Salting Simulation : watch rainbow-table attack on two users
Phase 4 — Fortify            : two-column layout (input + requirements)
"""
import pygame
from rooms.base_room import BaseRoom
from rooms.password.data import PUZZLE
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

MAX_SCORE = PUZZLE["max_score"]

_HEADER_H = 65
_FOOTER_H = 46
_CX       = SCREEN_WIDTH  // 2
_BOTTOM   = SCREEN_HEIGHT - _FOOTER_H   # 674

_SYMBOLS = set("!@#$%^&*()-_=+[]{}|;:',.<>?/")


def _calc_strength(password: str) -> int:
    if not password:
        return 0
    s = 0
    if len(password) >= 8:  s += 1
    if len(password) >= 12: s += 1
    if any(c.isupper() for c in password): s += 1
    if any(c.isdigit() for c in password): s += 1
    if any(c in _SYMBOLS  for c in password): s += 1
    return s


def _check_req(key: str, password: str) -> bool:
    if key == "length12": return len(password) >= 12
    if key == "upper":    return any(c.isupper() for c in password)
    if key == "digit":    return any(c.isdigit() for c in password)
    if key == "symbol":   return any(c in _SYMBOLS for c in password)
    return False


class Room(BaseRoom):
    """Room 3 — Password Vault."""

    # ── setup ─────────────────────────────────────────────────────────────────

    def setup(self) -> None:
        self._data = PUZZLE

        self._fh1   = pygame.font.SysFont("consolas", 20, bold=True)
        self._fbody = pygame.font.SysFont("consolas", 15)
        self._fsm   = pygame.font.SysFont("consolas", 13)
        self._fmono = pygame.font.SysFont("consolas", 13)
        self._fxs   = pygame.font.SysFont("consolas", 11)

        self._phase       = 0
        self._phase_score = [0, 0, 0, 0]

        # Dynamic button rects (populated during draw, read in click handlers)
        self._btn_rects:       dict[str, pygame.Rect] = {}
        self._p2_row_rects:    list[pygame.Rect]       = []

        self._reset_phase()

        self._time       = 0.0
        self._feedback   = ""
        self._feedback_t = 0.0

        # Room 2 → Room 3 narrative bridge
        pet = self.game.save.get_artefact("pet_name")
        self._p1_pet_hint = pet if pet else ""

    def _reset_phase(self) -> None:
        # Phase 1
        self._p1_running  = False
        self._p1_idx      = 0
        self._p1_speed    = 8.0
        self._p1_accum    = 0.0
        self._p1_cracked  = False

        # Phase 2
        self._p2_selected = -1
        self._p2_result   = None   # None / True / False

        # Phase 3 (simulation)
        self._p3_state       = "idle"  # idle | attacking | alice_cracked | trying_bob | bob_failed | revealed
        self._p3_alice_t     = 0.0    # 0→1 attack progress for alice
        self._p3_bob_t       = 0.0    # 0→1 attack progress for bob
        self._p3_auto_t      = 0.0    # auto-advance timer
        self._p3_reveal_step = 0      # 0=result  1=explanation  2=takeaway

        # Phase 4
        self._p4_password  = ""
        self._p4_active    = False
        self._p4_cursor_on = True
        self._p4_cursor_t  = 0.0
        self._p4_tested    = False
        self._p4_test_t    = 0.0
        self._p4_test_anim = 0.0

        self._btn_rects     = {}
        self._p2_row_rects  = []

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        if event.type == pygame.KEYDOWN:
            self._handle_key(event)

    def _handle_click(self, pos: tuple) -> None:
        if   self._phase == 0: self._click_p1(pos)
        elif self._phase == 1: self._click_p2(pos)
        elif self._phase == 2: self._click_p3(pos)
        elif self._phase == 3: self._click_p4(pos)

    def _click_p1(self, pos: tuple) -> None:
        if self._p1_cracked:
            r = self._btn_rects.get("NEXT PHASE")
            if r and r.collidepoint(pos):
                self._phase_score[0] = self._data["score_per_phase"]
                self._advance_phase()
            return
        if not self._p1_running:
            r = self._btn_rects.get("RUN ATTACK")
            if r and r.collidepoint(pos):
                self._p1_running = True
                self._p1_idx     = 0
                self._p1_speed   = 6.0

    def _click_p2(self, pos: tuple) -> None:
        if self._p2_result is True:
            r = self._btn_rects.get("NEXT PHASE")
            if r and r.collidepoint(pos):
                self._advance_phase()
            return

        self._p2_result   = None
        self._p2_selected = -1

        for i, r in enumerate(self._p2_row_rects):
            if r.collidepoint(pos):
                self._p2_selected = i
                if i == self._data["phase2"]["answer_index"]:
                    self._p2_result = True
                    self._phase_score[1] = self._data["score_per_phase"]
                    self._set_feedback("Correct! That hash matches the intercepted hash.")
                else:
                    self._p2_result = False
                    self._set_feedback("Not quite — compare each character carefully.", 4.0)
                return

    def _click_p3(self, pos: tuple) -> None:
        if self._p3_state == "revealed":
            if self._p3_reveal_step == 0:
                r = self._btn_rects.get("WHAT HAPPENED?")
                if r and r.collidepoint(pos):
                    self._p3_reveal_step = 1
            elif self._p3_reveal_step == 1:
                r = self._btn_rects.get("SEE THE LESSON")
                if r and r.collidepoint(pos):
                    self._p3_reveal_step = 2
            elif self._p3_reveal_step == 2:
                r = self._btn_rects.get("NEXT PHASE")
                if r and r.collidepoint(pos):
                    self._advance_phase()
            return
        if self._p3_state == "idle":
            r = self._btn_rects.get("LAUNCH ATTACK")
            if r and r.collidepoint(pos):
                self._p3_state = "attacking"

    def _click_p4(self, pos: tuple) -> None:
        if self._p4_input_rect().collidepoint(pos):
            self._p4_active = True
            return
        self._p4_active = False

        strength = _calc_strength(self._p4_password)
        required = self._data["phase4"]["required_strength"]

        if strength >= required and not self._p4_tested:
            r = self._btn_rects.get("TEST PASSWORD")
            if r and r.collidepoint(pos):
                self._p4_tested    = True
                self._p4_test_t    = 0.0
                self._p4_test_anim = 0.0

        if self._p4_tested and self._p4_test_anim >= 1.0:
            r = self._btn_rects.get("SECURE THE VAULT")
            if r and r.collidepoint(pos):
                self._phase_score[3] = self._data["score_per_phase"]
                self._advance_phase()

    def _handle_key(self, event: pygame.event.Event) -> None:
        if self._phase == 3 and self._p4_active:
            k = event.key
            if k == pygame.K_BACKSPACE:
                self._p4_password = self._p4_password[:-1]
            elif k == pygame.K_RETURN:
                self._p4_active = False
            elif event.unicode and event.unicode.isprintable():
                if len(self._p4_password) < 64:
                    self._p4_password += event.unicode

    def _advance_phase(self) -> None:
        self._phase += 1
        if self._phase >= 4:
            self._score    = sum(self._phase_score)
            self._complete = True
        else:
            self._reset_phase()
            self._set_feedback("")

    def _set_feedback(self, msg: str, dur: float = 3.5) -> None:
        self._feedback   = msg
        self._feedback_t = dur

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time += dt

        if self._feedback_t > 0:
            self._feedback_t -= dt

        p = self._phase
        if p == 0:
            self._update_p1(dt)
        elif p == 2:
            self._update_p3(dt)
        elif p == 3:
            self._p4_cursor_t += dt
            if self._p4_cursor_t >= 0.5:
                self._p4_cursor_on = not self._p4_cursor_on
                self._p4_cursor_t  = 0.0
            if self._p4_tested:
                self._p4_test_t   += dt
                self._p4_test_anim = min(1.0, self._p4_test_anim + dt * 0.45)

    def _update_p1(self, dt: float) -> None:
        d = self._data["phase1"]
        if self._p1_cracked or not self._p1_running:
            return
        self._p1_speed  = min(22.0, self._p1_speed + dt * 3)
        self._p1_accum += dt * self._p1_speed
        steps = int(self._p1_accum)
        self._p1_accum -= steps
        self._p1_idx    = min(self._p1_idx + steps, len(d["wordlist"]) - 1)
        if d["wordlist"][self._p1_idx] == d["answer"]:
            self._p1_cracked = True
            self._p1_running = False
            self.game.audio.play("crack")
            self._set_feedback("Password cracked! Read the lesson, then click NEXT PHASE.", 12.0)

    def _update_p3(self, dt: float) -> None:
        state = self._p3_state
        if state == "attacking":
            self._p3_alice_t = min(1.0, self._p3_alice_t + dt * 0.7)
            if self._p3_alice_t >= 1.0:
                self._p3_state  = "alice_cracked"
                self._p3_auto_t = 0.0
                self.game.audio.play("crack")
        elif state == "alice_cracked":
            self._p3_auto_t += dt
            if self._p3_auto_t >= 1.6:
                self._p3_state  = "trying_bob"
                self._p3_auto_t = 0.0
        elif state == "trying_bob":
            self._p3_bob_t = min(1.0, self._p3_bob_t + dt * 0.42)
            if self._p3_bob_t >= 1.0:
                self._p3_state  = "bob_failed"
                self._p3_auto_t = 0.0
        elif state == "bob_failed":
            self._p3_auto_t += dt
            if self._p3_auto_t >= 1.6:
                self._p3_state       = "revealed"
                self._phase_score[2] = self._data["score_per_phase"]

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_header(surface)
        self._draw_phase_bar(surface)
        if   self._phase == 0: self._draw_p1(surface)
        elif self._phase == 1: self._draw_p2(surface)
        elif self._phase == 2: self._draw_p3(surface)
        elif self._phase == 3: self._draw_p4(surface)
        self._draw_footer(surface)

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, (0, 0, SCREEN_WIDTH, _HEADER_H))
        pygame.draw.line(surface, BORDER,
                         (0, _HEADER_H), (SCREEN_WIDTH, _HEADER_H), 1)
        title = self._fh1.render("ROOM 3  //  PASSWORD VAULT", True, ACCENT_ORANGE)
        surface.blit(title, (18, (_HEADER_H - title.get_height()) // 2))
        hint = self._fsm.render("ESC = Rooms  |  M = toggle sound", True, TEXT_MUTED)
        surface.blit(hint, (SCREEN_WIDTH - hint.get_width() - 18,
                            (_HEADER_H - hint.get_height()) // 2))

    def _draw_phase_bar(self, surface: pygame.Surface) -> None:
        dot_r   = 7
        spacing = 60
        n       = 4
        total_w = n * dot_r * 2 + (n - 1) * (spacing - dot_r * 2)
        sx      = _CX - total_w // 2
        y       = _HEADER_H + 16
        pygame.draw.line(surface, BORDER, (sx, y), (sx + (n - 1) * spacing, y), 1)
        for i in range(n):
            x    = sx + i * spacing
            done = i < self._phase
            cur  = i == self._phase
            col  = (ACCENT_GREEN if done else ACCENT_CYAN if cur else BORDER)
            if done or cur:
                pygame.draw.circle(surface, col, (x, y), dot_r)
            else:
                pygame.draw.circle(surface, col, (x, y), dot_r, 1)
            label = self._fsm.render(f"P{i+1}", True,
                                     TEXT_DIM if not (done or cur) else TEXT_PRIMARY)
            surface.blit(label, label.get_rect(centerx=x, y=y + dot_r + 3))

    # ── Phase 1 ───────────────────────────────────────────────────────────────

    def _draw_p1(self, surface: pygame.Surface) -> None:
        d = self._data["phase1"]
        y = _HEADER_H + 56

        # Room 2 → 3 intel bridge banner
        if self._p1_pet_hint:
            banner_r = pygame.Rect(18, y, SCREEN_WIDTH - 36, 34)
            pygame.draw.rect(surface, (30, 18, 0), banner_r, border_radius=4)
            pygame.draw.rect(surface, ACCENT_ORANGE, banner_r, 1, border_radius=4)
            msg = self._fsm.render(
                f"[OSINT INTEL]  Target may use pet name \"{self._p1_pet_hint}\" as a password component.",
                True, ACCENT_ORANGE,
            )
            surface.blit(msg, msg.get_rect(center=banner_r.center))
            y += banner_r.h + 10

        self._draw_phase_title(surface, d["title"], d["headline"], y)
        y += 64

        self._draw_briefing(surface, d["briefing"], y)
        y += 54

        # Target account
        box = pygame.Rect(_CX - 260, y, 520, 48)
        pygame.draw.rect(surface, BG_PANEL, box, border_radius=5)
        pygame.draw.rect(surface, BORDER,   box, 1, border_radius=5)
        label = self._fbody.render(
            f"Target account:  {d['target_account']}", True, TEXT_DIM
        )
        surface.blit(label, label.get_rect(center=box.center))
        y += box.h + 16

        # Scrolling wordlist window
        win_h = 118
        win_r = pygame.Rect(_CX - 200, y, 400, win_h)
        pygame.draw.rect(surface, BG_MID, win_r, border_radius=4)
        pygame.draw.rect(surface, BORDER, win_r, 1, border_radius=4)

        wordlist  = d["wordlist"]
        vis_n     = 5
        center_i  = self._p1_idx
        start_i   = max(0, center_i - vis_n // 2)

        clip = surface.get_clip()
        surface.set_clip(win_r)
        for vi, wi in enumerate(range(start_i, min(len(wordlist), start_i + vis_n + 1))):
            word = wordlist[wi]
            wy   = win_r.y + 8 + vi * 22
            if wi == center_i:
                col = ACCENT_GREEN if self._p1_cracked else ACCENT_CYAN
                hl  = pygame.Rect(win_r.x + 4, wy - 2, win_r.w - 8, 22)
                pygame.draw.rect(surface, (0, 30, 18), hl, border_radius=3)
                ws  = self._fbody.render(f">> {word}", True, col)
            else:
                dist = abs(wi - center_i)
                v    = max(40, 140 - dist * 35)
                ws   = self._fmono.render(f"   {word}", True, (v, v + 20, v + 40))
            surface.blit(ws, (win_r.x + 12, wy))
        surface.set_clip(clip)

        y += win_h + 14

        if self._p1_cracked:
            crk = self._fh1.render(f"CRACKED:  {d['answer']}", True, ACCENT_GREEN)
            surface.blit(crk, crk.get_rect(centerx=_CX, y=y))
            y += crk.get_height() + 10
            for line in self._wrap(d["teach_line"], self._fsm, 740):
                ts = self._fsm.render(line, True, TEXT_DIM)
                surface.blit(ts, ts.get_rect(centerx=_CX, y=y))
                y += ts.get_height() + 3
            y += 10
            self._draw_button(surface, "NEXT PHASE", _CX - 90, y, 180)
        elif not self._p1_running:
            self._draw_button(surface, "RUN ATTACK", _CX - 100, y, 200)

        self._draw_feedback(surface)

    # ── Phase 2 ───────────────────────────────────────────────────────────────
    # Two-column layout: left = info cards + target hash; right = rainbow table

    def _draw_p2(self, surface: pygame.Surface) -> None:
        d = self._data["phase2"]
        y = _HEADER_H + 56

        self._draw_phase_title(surface, d["title"], d["headline"], y)
        y += 64   # y = 185 (with _HEADER_H=65)

        # Column geometry
        mid       = _CX - 20
        lx        = 18
        lw        = mid - lx - 14           # left column width ~588
        rx        = mid + 14
        rw        = SCREEN_WIDTH - rx - 18  # right column width ~606
        col_y     = y   # both columns start at same y

        # ── LEFT COLUMN: info panels + target hash ────────────────────────
        ly = col_y

        # Info card 1: What is a hash?
        card1_lines = [
            "WHAT IS A HASH?",
            "",
            "A hash turns a password into a fixed-length",
            "string. The same input always produces the",
            "same output — but you cannot reverse it.",
        ]
        ly = self._draw_info_card(surface, card1_lines, lx, ly, lw, ACCENT_CYAN)
        ly += 10

        # Info card 2: What is a rainbow table?
        card2_lines = [
            "WHAT IS A RAINBOW TABLE?",
            "",
            "A pre-computed list of passwords and their",
            "hashes. If the intercepted hash appears in",
            "the table, the plaintext password is known.",
        ]
        ly = self._draw_info_card(surface, card2_lines, lx, ly, lw, ACCENT_ORANGE)
        ly += 10

        # Target hash panel
        th_r = pygame.Rect(lx, ly, lw, 58)
        pygame.draw.rect(surface, (30, 0, 0), th_r, border_radius=5)
        pygame.draw.rect(surface, ACCENT_RED, th_r, 1, border_radius=5)
        th_lbl = self._fsm.render("INTERCEPTED HASH (MD5):", True, ACCENT_RED)
        surface.blit(th_lbl, (lx + 10, ly + 8))
        th_val = self._fmono.render(d["target_hash"], True, TEXT_PRIMARY)
        surface.blit(th_val, (lx + 10, ly + 28))
        ly += th_r.h + 10

        # Instruction
        instr = self._fsm.render(
            "Click the row in the table whose hash matches.", True, TEXT_DIM
        )
        surface.blit(instr, (lx, ly))

        # ── RIGHT COLUMN: rainbow table ───────────────────────────────────
        ry = col_y

        # Table header
        row_h  = 32
        header = pygame.Rect(rx, ry, rw, 28)
        pygame.draw.rect(surface, BG_PANEL, header, border_radius=3)
        col_div  = rx + int(rw * 0.30)
        hl = self._fsm.render("Plaintext password", True, TEXT_MUTED)
        hr = self._fsm.render("MD5 Hash", True, TEXT_MUTED)
        surface.blit(hl, (rx + 10, header.centery - hl.get_height() // 2))
        surface.blit(hr, (col_div + 10, header.centery - hr.get_height() // 2))
        pygame.draw.line(surface, BORDER,
                         (col_div + 4, ry), (col_div + 4, ry + 28), 1)
        ry += header.h + 2

        # Data rows
        mx, my = pygame.mouse.get_pos()
        self._p2_row_rects = []
        for i, row in enumerate(d["rainbow_table"]):
            r = pygame.Rect(rx, ry + i * row_h, rw, row_h - 2)
            self._p2_row_rects.append(r)

            if i == self._p2_selected and self._p2_result is True:
                fill, bc = (0, 40, 20), ACCENT_GREEN
            elif i == self._p2_selected and self._p2_result is False:
                fill, bc = (50, 0, 0), ACCENT_RED
            elif r.collidepoint(mx, my) and self._p2_result is None:
                fill, bc = (18, 24, 42), ACCENT_CYAN
            else:
                fill, bc = (BG_MID if i % 2 == 0 else BG_PANEL), BORDER

            pygame.draw.rect(surface, fill, r, border_radius=3)
            pygame.draw.rect(surface, bc,   r, 1, border_radius=3)
            pygame.draw.line(surface, BORDER,
                             (col_div + 4, r.y), (col_div + 4, r.bottom), 1)

            col = ACCENT_GREEN if (i == self._p2_selected and self._p2_result) else TEXT_DIM
            pw  = self._fmono.render(row["plain"], True, col)
            hh  = self._fmono.render(row["hash"],  True, col)
            surface.blit(pw, (rx + 10,       r.centery - pw.get_height() // 2))
            surface.blit(hh, (col_div + 10, r.centery - hh.get_height() // 2))

        if self._p2_result is True:
            result_y = ry + len(d["rainbow_table"]) * row_h + 12
            for tl in self._wrap(d["teach_line"], self._fsm, rw):
                ts = self._fsm.render(tl, True, TEXT_DIM)
                surface.blit(ts, (rx, result_y))
                result_y += ts.get_height() + 3
            result_y += 8
            self._draw_button(surface, "NEXT PHASE", rx, result_y, 180)

        self._draw_feedback(surface)

    def _draw_info_card(self, surface: pygame.Surface,
                        lines: list[str], x: int, y: int,
                        w: int, accent: tuple) -> int:
        lh    = self._fxs.get_height() + 3
        h     = len(lines) * lh + 18
        card  = pygame.Rect(x, y, w, h)
        r, g, b = accent
        pygame.draw.rect(surface, (r // 8, g // 8, b // 8), card, border_radius=4)
        pygame.draw.rect(surface, accent, card, 1, border_radius=4)
        cy = y + 9
        for line in lines:
            if line == "":
                cy += lh // 2
                continue
            is_header = line.isupper() and "?" in line
            col  = accent if is_header else TEXT_DIM
            font = self._fsm if is_header else self._fxs
            ls   = font.render(line, True, col)
            surface.blit(ls, (x + 10, cy))
            cy += font.get_height() + 3
        return y + h

    # ── Phase 3 — Salting Simulation ──────────────────────────────────────────

    def _draw_p3(self, surface: pygame.Surface) -> None:
        d = self._data["phase3"]
        y = _HEADER_H + 56

        self._draw_phase_title(surface, d["title"], d["headline"], y)
        y += 64

        state = self._p3_state

        if state == "idle" or state != "revealed" or self._p3_reveal_step == 0:
            # Always show user table in idle/attacking/result step
            y = self._draw_p3_user_table(surface, d, y)
            y += 18

        if state == "idle":
            intro = self._fsm.render(
                "Both users have the same password. Watch what happens when an attacker has the rainbow table.",
                True, TEXT_DIM,
            )
            surface.blit(intro, intro.get_rect(centerx=_CX, y=y))
            y += intro.get_height() + 14
            self._draw_button(surface, "LAUNCH ATTACK", _CX - 120, y, 240)

        elif state != "revealed":
            # Still animating
            y = self._draw_p3_attack_bars(surface, y)

        elif self._p3_reveal_step == 0:
            # Step 0 — show attack result, prompt player to continue
            y = self._draw_p3_attack_bars(surface, y)
            y += 16
            self._draw_button(surface, "WHAT HAPPENED?", _CX - 120, y, 240)

        elif self._p3_reveal_step == 1:
            # Step 1 — compact result recap + Alice/Bob explanation cards
            y = self._draw_p3_result_recap(surface, y)
            y += 8
            y = self._draw_p3_explanation(surface, d, y, max_cards=2)
            y += 8
            if y < _BOTTOM - 46:
                self._draw_button(surface, "SEE THE LESSON", _CX - 120, y, 240)

        elif self._p3_reveal_step == 2:
            # Step 2 — cybersecurity takeaway + NEXT PHASE
            y = self._draw_p3_takeaway(surface, d, y)
            y += 8
            if y < _BOTTOM - 46:
                self._draw_button(surface, "NEXT PHASE", _CX - 90, y, 180)

        self._draw_feedback(surface)

    def _draw_p3_user_table(self, surface: pygame.Surface, d: dict, y: int) -> int:
        state     = self._p3_state
        show_salt = state in ("revealed",)

        tw    = 900
        tx    = _CX - tw // 2
        col_x = [tx + 10, tx + 160, tx + 330, tx + 490]
        hdr_r = pygame.Rect(tx, y, tw, 28)
        pygame.draw.rect(surface, BG_PANEL, hdr_r, border_radius=3)
        for lbl, cx in zip(["Username", "Password", "Salt", "Stored Hash"], col_x):
            ls = self._fsm.render(lbl, True, TEXT_MUTED)
            surface.blit(ls, (cx, y + 7))
        y += hdr_r.h + 3

        for ui, user in enumerate(d["users"]):
            row_r = pygame.Rect(tx, y, tw, 34)
            pygame.draw.rect(surface, BG_MID if ui % 2 == 0 else BG_PANEL,
                             row_r, border_radius=3)
            pygame.draw.rect(surface, BORDER, row_r, 1, border_radius=3)
            salt_val = user["salt"] if (user["salt"] and show_salt) else (
                "x7kQ9#" if (user["username"] == "bob" and show_salt) else
                ("????????" if user["salt"] else "(none)")
            )
            vals = [user["username"], user["password"], salt_val, user["hash"]]
            for val, cx in zip(vals, col_x):
                vc = TEXT_DIM
                if val == "????????":   vc = TEXT_MUTED
                if val == "(none)":     vc = ACCENT_RED
                if show_salt and user["salt"] and val == user.get("salt", ""):
                    vc = ACCENT_CYAN
                vs = self._fmono.render(str(val), True, vc)
                surface.blit(vs, (cx, row_r.centery - vs.get_height() // 2))
            y += row_r.h + 2

        return y

    def _draw_p3_attack_bars(self, surface: pygame.Surface, y: int) -> int:
        state     = self._p3_state
        bar_w     = 540
        bar_h     = 34
        bx        = _CX - bar_w // 2
        lbl_w     = 90

        for who in ("alice", "bob"):
            # Determine progress and status for this user
            if who == "alice":
                prog   = self._p3_alice_t
                active = state in ("attacking",)
                done   = state in ("alice_cracked", "trying_bob", "bob_failed", "revealed")
                failed = False
            else:
                prog   = self._p3_bob_t
                active = state in ("trying_bob",)
                done   = False
                failed = state in ("bob_failed", "revealed")

            # Label
            lbl = self._fmono.render(who + ":", True, TEXT_DIM)
            surface.blit(lbl, (bx, y + (bar_h - lbl.get_height()) // 2))

            # Bar background
            bar_r = pygame.Rect(bx + lbl_w, y, bar_w - lbl_w, bar_h)
            pygame.draw.rect(surface, BG_MID, bar_r, border_radius=4)
            pygame.draw.rect(surface, BORDER, bar_r, 1, border_radius=4)

            if active or done or failed:
                fill_w = int((bar_w - lbl_w) * prog)
                if fill_w > 0:
                    if failed:
                        fill_col = (160, 30, 30)
                    elif done:
                        fill_col = (0, 160, 50)
                    else:
                        fill_col = (0, 80, 180)
                    pygame.draw.rect(surface, fill_col,
                                     pygame.Rect(bar_r.x, y, fill_w, bar_h),
                                     border_radius=4)

            # Status text overlay
            if who == "alice" and done:
                status = self._fh1.render("CRACKED: \"letmein\"", True, ACCENT_GREEN)
            elif who == "alice" and active:
                status = self._fsm.render("scanning rainbow table...", True, ACCENT_CYAN)
            elif who == "bob" and failed:
                status = self._fh1.render("ATTACK FAILED", True, ACCENT_RED)
            elif who == "bob" and active:
                status = self._fsm.render("scanning rainbow table...", True, ACCENT_CYAN)
            elif who == "bob":
                status = self._fsm.render("waiting...", True, TEXT_MUTED)
            else:
                status = self._fsm.render("waiting...", True, TEXT_MUTED)

            surface.blit(status, status.get_rect(
                centerx=bar_r.centerx,
                centery=bar_r.centery,
            ))
            y += bar_h + 8

        return y

    def _draw_p3_result_recap(self, surface: pygame.Surface, y: int) -> int:
        """Compact two-line summary of the attack outcome (shown in steps 1)."""
        for text, col in [
            ('alice  >>  CRACKED: "letmein"', ACCENT_GREEN),
            ("bob    >>  ATTACK FAILED",      ACCENT_RED),
        ]:
            ls = self._fmono.render(text, True, col)
            surface.blit(ls, ls.get_rect(centerx=_CX, y=y))
            y += ls.get_height() + 6
        return y

    def _draw_p3_takeaway(self, surface: pygame.Surface, d: dict, y: int) -> int:
        """Draws the 'What does this teach us?' card (step 2)."""
        card_w = 840
        cx     = _CX - card_w // 2
        title  = "WHAT DOES THIS TEACH US?"
        lines  = self._wrap(d["teach_line"], self._fsm, card_w - 24)
        card_h = 20 + self._fbody.get_height() + 6 + len(lines) * (self._fsm.get_height() + 3)
        card_r = pygame.Rect(cx, y, card_w, card_h)
        r, g, b = ACCENT_CYAN
        pygame.draw.rect(surface, (r // 8, g // 8, b // 8), card_r, border_radius=4)
        pygame.draw.rect(surface, ACCENT_CYAN, card_r, 1, border_radius=4)
        surface.blit(self._fbody.render(title, True, ACCENT_CYAN), (cx + 10, y + 8))
        ty = y + 8 + self._fbody.get_height() + 6
        for line in lines:
            surface.blit(self._fsm.render(line, True, TEXT_DIM), (cx + 10, ty))
            ty += self._fsm.get_height() + 3
        return y + card_h + 8

    def _draw_p3_explanation(self, surface: pygame.Surface, d: dict, y: int,
                             max_cards: int = 3) -> int:
        sections = [
            (ACCENT_GREEN, "WHY DID ALICE'S HASH CRACK?",
             "Alice has no salt. The hash maps directly to \"letmein\" in the rainbow table."),
            (ACCENT_RED, "WHY DID BOB'S HASH SURVIVE?",
             "Bob's salt changes the hash entirely. \"x7kQ9#letmein\" is not in any rainbow table."),
            (ACCENT_CYAN, "WHAT DOES THIS TEACH US?",
             d["teach_line"]),
        ]
        for i, (col, title, body) in enumerate(sections):
            if i >= max_cards:
                break
            card_w = 840
            cx     = _CX - card_w // 2
            lines  = self._wrap(body, self._fsm, card_w - 24)
            card_h = 20 + self._fbody.get_height() + 6 + len(lines) * (self._fsm.get_height() + 3)
            if y + card_h > _BOTTOM - 56:
                break
            card_r = pygame.Rect(cx, y, card_w, card_h)
            r, g, b = col
            pygame.draw.rect(surface, (r // 8, g // 8, b // 8), card_r, border_radius=4)
            pygame.draw.rect(surface, col, card_r, 1, border_radius=4)
            surface.blit(self._fbody.render(title, True, col), (cx + 10, y + 8))
            ty = y + 8 + self._fbody.get_height() + 6
            for line in lines:
                surface.blit(self._fsm.render(line, True, TEXT_DIM), (cx + 10, ty))
                ty += self._fsm.get_height() + 3
            y += card_h + 8
        return y

    # ── Phase 4 ───────────────────────────────────────────────────────────────
    # Two-column: left = input + strength + test; right = requirements + secure

    def _draw_p4(self, surface: pygame.Surface) -> None:
        d = self._data["phase4"]
        y = _HEADER_H + 56

        self._draw_phase_title(surface, d["title"], d["headline"], y)
        y += 64

        self._draw_briefing(surface, d["briefing"], y)
        y += 50

        # Column geometry
        mid = _CX - 20
        lx  = 18
        lw  = mid - lx - 14
        rx  = mid + 14
        rw  = SCREEN_WIDTH - rx - 18

        # ── RIGHT COLUMN: requirements card ───────────────────────────────
        req_y = y
        reqs  = d["requirements"]
        req_h = 16 + len(reqs) * 30 + 10
        req_r = pygame.Rect(rx, req_y, rw, req_h)
        pygame.draw.rect(surface, BG_PANEL, req_r, border_radius=5)
        pygame.draw.rect(surface, BORDER, req_r, 1, border_radius=5)
        rq_lbl = self._fsm.render("REQUIREMENTS", True, TEXT_MUTED)
        surface.blit(rq_lbl, (rx + 10, req_y + 8))
        rqy = req_y + 8 + rq_lbl.get_height() + 6
        for req in reqs:
            met   = _check_req(req["key"], self._p4_password)
            col   = ACCENT_GREEN if met else TEXT_MUTED
            mark  = "[v]" if met else "[ ]"
            rs    = self._fsm.render(f"  {mark}  {req['label']}", True, col)
            surface.blit(rs, (rx + 10, rqy))
            rqy += rs.get_height() + 8

        # Teach line (right column, below requirements)
        strength = _calc_strength(self._p4_password)
        required = d["required_strength"]
        if self._p4_tested and self._p4_test_anim >= 1.0:
            teach_y = req_y + req_h + 12
            for line in self._wrap(d["teach_line"], self._fxs, rw):
                ts = self._fxs.render(line, True, TEXT_DIM)
                surface.blit(ts, (rx, teach_y))
                teach_y += ts.get_height() + 3
            teach_y += 8
            if teach_y < _BOTTOM - 46:
                self._draw_button(surface, "SECURE THE VAULT", rx, teach_y, min(rw, 260))

        # ── LEFT COLUMN: input + strength + test ──────────────────────────
        ly = y

        # "Create your secure password:" label
        instr = self._fbody.render("Create your secure password:", True, TEXT_DIM)
        surface.blit(instr, (lx, ly))
        ly += instr.get_height() + 8

        # Input field
        inp_r = self._p4_input_rect()
        pygame.draw.rect(surface, BG_MID, inp_r, border_radius=4)
        pygame.draw.rect(surface,
                         ACCENT_CYAN if self._p4_active else BORDER,
                         inp_r, 2, border_radius=4)
        display = self._p4_password + ("|" if self._p4_active and self._p4_cursor_on else "")
        pw_s    = self._fbody.render(display, True, TEXT_PRIMARY)
        surface.blit(pw_s, (inp_r.x + 12, inp_r.centery - pw_s.get_height() // 2))
        ly += inp_r.h + 14

        # Strength bar
        max_s   = len(d["strength_labels"]) - 1
        s_label = d["strength_labels"][min(strength, max_s)]
        s_col   = tuple(d["strength_colors"][min(strength, max_s)])
        bar_w   = lw
        bar_h   = 14
        pygame.draw.rect(surface, BG_PANEL, (lx, ly, bar_w, bar_h), border_radius=6)
        fill_w = int(bar_w * strength / max_s) if max_s else 0
        if fill_w > 0:
            pygame.draw.rect(surface, s_col, (lx, ly, fill_w, bar_h), border_radius=6)
        sl = self._fbody.render(s_label, True, s_col)
        surface.blit(sl, (lx, ly + bar_h + 6))
        ly += bar_h + sl.get_height() + 16

        # TEST PASSWORD button (left column, when strength met)
        if strength >= required and not self._p4_tested:
            self._draw_button(surface, "TEST PASSWORD", lx, ly, 220)
            ly += 46

        # Attack animation (left column)
        if self._p4_tested:
            prog   = self._p4_test_anim
            anim_w = lw
            anim_r = pygame.Rect(lx, ly, anim_w, 36)
            pygame.draw.rect(surface, BG_MID, anim_r, border_radius=4)
            if prog < 1.0:
                fill_c = (int(180 * prog), 0, 0)
                pygame.draw.rect(surface, fill_c,
                                 (lx, ly, int(anim_w * prog), 36),
                                 border_radius=4)
                atxt = self._fsm.render("Dictionary attack running...", True, TEXT_DIM)
            else:
                pygame.draw.rect(surface, (0, 150, 50),
                                 anim_r, border_radius=4)
                atxt = self._fh1.render("ATTACK FAILED", True, ACCENT_GREEN)
            surface.blit(atxt, atxt.get_rect(centerx=anim_r.centerx,
                                             centery=anim_r.centery))

        self._draw_feedback(surface)

    def _p4_input_rect(self) -> pygame.Rect:
        # y: _HEADER_H + 56 + 64(title) + 50(briefing) + ~23(label+gap) + 8
        y = _HEADER_H + 56 + 64 + 50 + 23 + 8
        return pygame.Rect(18, y, _CX - 52, 44)

    # ── shared helpers ────────────────────────────────────────────────────────

    def _draw_footer(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID,
                         (0, SCREEN_HEIGHT - _FOOTER_H, SCREEN_WIDTH, _FOOTER_H))
        pygame.draw.line(surface, BORDER,
                         (0, SCREEN_HEIGHT - _FOOTER_H),
                         (SCREEN_WIDTH, SCREEN_HEIGHT - _FOOTER_H), 1)

    def _draw_phase_title(self, surface: pygame.Surface,
                          phase_str: str, headline: str, y: int) -> None:
        ps = self._fsm.render(phase_str, True, TEXT_MUTED)
        surface.blit(ps, ps.get_rect(centerx=_CX, y=y))
        hs = self._fh1.render(headline, True, ACCENT_ORANGE)
        surface.blit(hs, hs.get_rect(centerx=_CX, y=y + ps.get_height() + 4))

    def _draw_briefing(self, surface: pygame.Surface, text: str, y: int) -> None:
        for line in self._wrap(text, self._fsm, 700):
            ls = self._fsm.render(line, True, TEXT_DIM)
            surface.blit(ls, ls.get_rect(centerx=_CX, y=y))
            y += ls.get_height() + 3

    def _draw_button(self, surface: pygame.Surface,
                     label: str, x: int, y: int, w: int) -> None:
        mx, my  = pygame.mouse.get_pos()
        r       = pygame.Rect(x, y, w, 36)
        self._btn_rects[label] = r
        hovered = r.collidepoint(mx, my)
        pygame.draw.rect(surface, (0, 55, 28) if hovered else BG_PANEL, r, border_radius=4)
        pygame.draw.rect(surface, ACCENT_GREEN, r, 2, border_radius=4)
        ls = self._fbody.render(label, True, ACCENT_GREEN)
        surface.blit(ls, ls.get_rect(center=r.center))

    def _draw_feedback(self, surface: pygame.Surface) -> None:
        if self._feedback and self._feedback_t > 0:
            alpha = min(1.0, self._feedback_t / 0.4)
            col   = tuple(int(c * alpha) for c in ACCENT_ORANGE)
            fs    = self._fbody.render(self._feedback, True, col)
            surface.blit(fs, fs.get_rect(
                centerx=_CX,
                y=SCREEN_HEIGHT - _FOOTER_H - 32,
            ))

    # ── completion ────────────────────────────────────────────────────────────

    @property
    def is_complete(self) -> bool:
        return self._complete

    def get_score(self) -> int:
        return self._score

    # ── util ──────────────────────────────────────────────────────────────────

    @staticmethod
    def _wrap(text: str, font: pygame.font.Font, max_w: int) -> list[str]:
        words, lines, cur = text.split(), [], ""
        for w in words:
            test = (cur + " " + w).strip()
            if font.size(test)[0] <= max_w:
                cur = test
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines
