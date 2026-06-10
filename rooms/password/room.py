"""
Room 3 — Password Vault  (fully playable, 4 sequential phases).

Phase 1 — Dictionary Attack : click RUN ATTACK, watch wordlist scroll, see crack
Phase 2 — Hash Cracking     : spot the matching row in a rainbow table
Phase 3 — Salting           : multiple-choice question about salt
Phase 4 — Fortify           : type a strong password; strength meter must reach "Strong"
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

# Symbols accepted for the strength check
_SYMBOLS = set("!@#$%^&*()-_=+[]{}|;:',.<>?/")


def _calc_strength(password: str) -> int:
    """Return 0-5 strength score."""
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

        self._phase       = 0     # 0 = phase 1, …, 3 = phase 4
        self._phase_score = [0, 0, 0, 0]
        self._phase_done  = [False, False, False, False]

        # Phase-specific state
        self._reset_phase()

        self._result_t    = 0.0
        self._time        = 0.0
        self._feedback    = ""
        self._feedback_t  = 0.0

    def _reset_phase(self) -> None:
        # ── phase 1 ───────────────────────────────────────────────────────────
        self._p1_running    = False
        self._p1_idx        = 0      # current word being tried
        self._p1_speed      = 8.0    # words per second (accelerates)
        self._p1_accum      = 0.0
        self._p1_cracked    = False
        self._p1_crack_t    = 0.0    # countdown after crack before advance

        # ── phase 2 ───────────────────────────────────────────────────────────
        self._p2_selected   = -1
        self._p2_result     = None   # True/False after selection

        # ── phase 3 ───────────────────────────────────────────────────────────
        self._p3_selected   = -1
        self._p3_result     = None
        self._p3_reveal_t   = 0.0   # timer for salt reveal animation

        # ── phase 4 ───────────────────────────────────────────────────────────
        self._p4_password   = ""
        self._p4_active     = False
        self._p4_cursor_on  = True
        self._p4_cursor_t   = 0.0
        self._p4_tested     = False
        self._p4_test_t     = 0.0
        self._p4_test_anim  = 0.0

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        if event.type == pygame.KEYDOWN:
            self._handle_key(event)

    def _handle_click(self, pos: tuple) -> None:
        p = self._phase

        if p == 0:   self._click_p1(pos)
        elif p == 1: self._click_p2(pos)
        elif p == 2: self._click_p3(pos)
        elif p == 3: self._click_p4(pos)

    def _click_p1(self, pos: tuple) -> None:
        if not self._p1_cracked and not self._p1_running:
            if self._btn_rect("RUN ATTACK").collidepoint(pos):
                self._p1_running = True
                self._p1_idx     = 0
                self._p1_speed   = 6.0

    def _click_p2(self, pos: tuple) -> None:
        if self._p2_result is not None:
            return
        rows  = self._data["phase2"]["rainbow_table"]
        start_y = _HEADER_H + 180
        row_h   = 32
        for i in range(len(rows)):
            r = pygame.Rect(_CX - 280, start_y + i * row_h, 560, row_h - 2)
            if r.collidepoint(pos):
                self._p2_selected = i
                correct = self._data["phase2"]["answer_index"]
                self._p2_result   = (i == correct)
                if self._p2_result:
                    self._set_feedback("Correct! That hash matches the target.")
                    self._phase_score[1] = self._data["score_per_phase"]
                else:
                    self._set_feedback("Wrong row — look more carefully at the hash characters.", 5.0)
                return

        # Next button
        if self._p2_result is True and self._btn_rect("NEXT PHASE").collidepoint(pos):
            self._advance_phase()

    def _click_p3(self, pos: tuple) -> None:
        if self._p3_result is not None:
            if self._btn_rect("NEXT PHASE").collidepoint(pos):
                self._advance_phase()
            return

        choices = self._data["phase3"]["choices"]
        start_y = _HEADER_H + 230
        row_h   = 44
        for i in range(len(choices)):
            r = pygame.Rect(_CX - 300, start_y + i * row_h, 600, row_h - 4)
            if r.collidepoint(pos):
                self._p3_selected = i
                correct = self._data["phase3"]["answer_index"]
                self._p3_result   = (i == correct)
                if self._p3_result:
                    self._set_feedback("Exactly right. Salting defeats rainbow tables.")
                    self._phase_score[2] = self._data["score_per_phase"]
                    self._p3_reveal_t    = 0.0
                else:
                    self._set_feedback("Not quite. Think about what's different in Bob's record.")
                return

    def _click_p4(self, pos: tuple) -> None:
        # Activate input box
        if self._p4_input_rect().collidepoint(pos):
            self._p4_active = True
            return
        self._p4_active = False

        strength = _calc_strength(self._p4_password)
        required = self._data["phase4"]["required_strength"]

        # Test button
        if strength >= required and not self._p4_tested:
            if self._btn_rect("TEST PASSWORD").collidepoint(pos):
                self._p4_tested  = True
                self._p4_test_t  = 0.0
                self._p4_test_anim = 0.0

        # Finish button
        if self._p4_tested and self._btn_rect("SECURE THE VAULT").collidepoint(pos):
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
        elif p == 2 and self._p3_result:
            self._p3_reveal_t += dt
        elif p == 3:
            self._p4_cursor_t += dt
            if self._p4_cursor_t >= 0.5:
                self._p4_cursor_on = not self._p4_cursor_on
                self._p4_cursor_t  = 0.0
            if self._p4_tested:
                self._p4_test_t   += dt
                self._p4_test_anim = min(1.0, self._p4_test_anim + dt * 0.5)

    def _update_p1(self, dt: float) -> None:
        d = self._data["phase1"]
        if self._p1_cracked:
            self._p1_crack_t += dt
            if self._p1_crack_t > 2.8:
                self._phase_score[0] = self._data["score_per_phase"]
                self._advance_phase()
            return

        if not self._p1_running:
            return

        # Accelerate the attack
        self._p1_speed = min(22.0, self._p1_speed + dt * 3)
        self._p1_accum += dt * self._p1_speed

        steps = int(self._p1_accum)
        self._p1_accum -= steps
        self._p1_idx   = min(self._p1_idx + steps, len(d["wordlist"]) - 1)

        if d["wordlist"][self._p1_idx] == d["answer"]:
            self._p1_cracked = True
            self._p1_running = False
            self._set_feedback("Password cracked!", 4.0)

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
        """4-step progress dots just below the header."""
        dot_r   = 7
        spacing = 60
        n       = 4
        total_w = n * dot_r * 2 + (n - 1) * (spacing - dot_r * 2)
        sx      = _CX - total_w // 2
        y       = _HEADER_H + 16

        for i in range(n):
            x    = sx + i * spacing
            done = i < self._phase
            cur  = i == self._phase
            col  = (ACCENT_GREEN if done else
                    ACCENT_CYAN  if cur  else BORDER)
            if done or cur:
                pygame.draw.circle(surface, col, (x, y), dot_r)
            else:
                pygame.draw.circle(surface, col, (x, y), dot_r, 1)

            label = self._fsm.render(f"P{i+1}", True,
                                     TEXT_DIM if not (done or cur) else TEXT_PRIMARY)
            surface.blit(label, label.get_rect(centerx=x, y=y + dot_r + 3))

        if i < n - 1:
            lx = sx + (n - 1) * spacing
            pygame.draw.line(surface, BORDER, (sx, y), (lx, y), 1)

    # ── Phase 1 draw ──────────────────────────────────────────────────────────

    def _draw_p1(self, surface: pygame.Surface) -> None:
        d = self._data["phase1"]
        y = _HEADER_H + 56

        self._draw_phase_title(surface, d["title"], d["headline"], y)
        y += 64

        self._draw_briefing(surface, d["briefing"], y)
        y += 54

        # Target account box
        box = pygame.Rect(_CX - 260, y, 520, 52)
        pygame.draw.rect(surface, BG_PANEL, box, border_radius=5)
        pygame.draw.rect(surface, BORDER,   box, 1, border_radius=5)
        label = self._fbody.render(
            f"Target account:  {d['target_account']}", True, TEXT_DIM
        )
        surface.blit(label, label.get_rect(center=box.center))
        y += box.h + 16

        # Scrolling wordlist window
        win_h   = 120
        win_r   = pygame.Rect(_CX - 200, y, 400, win_h)
        pygame.draw.rect(surface, BG_MID, win_r, border_radius=4)
        pygame.draw.rect(surface, BORDER, win_r, 1, border_radius=4)

        wordlist   = d["wordlist"]
        visible_n  = 5
        center_idx = self._p1_idx
        start_idx  = max(0, center_idx - visible_n // 2)

        clip = surface.get_clip()
        surface.set_clip(win_r)
        for vi, wi in enumerate(range(start_idx, min(len(wordlist), start_idx + visible_n + 1))):
            word = wordlist[wi]
            wy   = win_r.y + 8 + vi * 22
            if wi == center_idx:
                col = ACCENT_GREEN if self._p1_cracked else ACCENT_CYAN
                hl  = pygame.Rect(win_r.x + 4, wy - 2, win_r.w - 8, 22)
                pygame.draw.rect(surface, (0, 30, 18), hl, border_radius=3)
                ws = self._fbody.render(f">> {word}", True, col)
            else:
                dist = abs(wi - center_idx)
                alpha_col = max(40, 140 - dist * 35)
                ws = self._fmono.render(f"   {word}", True, (alpha_col, alpha_col+20, alpha_col+40))
            surface.blit(ws, (win_r.x + 12, wy))
        surface.set_clip(clip)

        y += win_h + 14

        if self._p1_cracked:
            crk = self._fh1.render(
                f"CRACKED:  {d['answer']}", True, ACCENT_GREEN
            )
            surface.blit(crk, crk.get_rect(centerx=_CX, y=y))
            y += crk.get_height() + 8
            teach = self._fsm.render(d["teach_line"], True, TEXT_DIM)
            surface.blit(teach, teach.get_rect(centerx=_CX, y=y))
        elif not self._p1_running:
            self._draw_button(surface, "RUN ATTACK", _CX - 100, y, 200)

        self._draw_feedback(surface)

    # ── Phase 2 draw ──────────────────────────────────────────────────────────

    def _draw_p2(self, surface: pygame.Surface) -> None:
        d = self._data["phase2"]
        y = _HEADER_H + 56

        self._draw_phase_title(surface, d["title"], d["headline"], y)
        y += 64

        self._draw_briefing(surface, d["briefing"], y)
        y += 54

        # Target hash box
        hbox = pygame.Rect(_CX - 300, y, 600, 44)
        pygame.draw.rect(surface, BG_PANEL, hbox, border_radius=5)
        pygame.draw.rect(surface, ACCENT_RED, hbox, 1, border_radius=5)
        label = self._fbody.render(
            f"Intercepted hash:   {d['target_hash']}", True, ACCENT_RED
        )
        surface.blit(label, label.get_rect(center=hbox.center))
        y += hbox.h + 12

        instr = self._fsm.render(
            "Click the row in the rainbow table whose hash matches.", True, TEXT_DIM
        )
        surface.blit(instr, instr.get_rect(centerx=_CX, y=y))
        y += instr.get_height() + 10

        # Rainbow table rows
        row_h = 32
        header = pygame.Rect(_CX - 280, y, 560, row_h - 2)
        pygame.draw.rect(surface, BG_PANEL, header, border_radius=3)
        hl = self._fsm.render("Plaintext password", True, TEXT_MUTED)
        hr = self._fsm.render("MD5 Hash", True, TEXT_MUTED)
        surface.blit(hl, (header.x + 12, header.centery - hl.get_height() // 2))
        surface.blit(hr, (header.x + 200, header.centery - hr.get_height() // 2))
        y += row_h

        mx, my  = pygame.mouse.get_pos()
        for i, row in enumerate(d["rainbow_table"]):
            r = pygame.Rect(_CX - 280, y + i * row_h, 560, row_h - 2)
            if i == self._p2_selected and self._p2_result is True:
                fill, border_c = (0, 40, 20), ACCENT_GREEN
            elif i == self._p2_selected and self._p2_result is False:
                fill, border_c = (50, 0, 0), ACCENT_RED
            elif r.collidepoint(mx, my) and self._p2_result is None:
                fill, border_c = (18, 24, 42), ACCENT_CYAN
            else:
                fill, border_c = BG_MID, BORDER
            pygame.draw.rect(surface, fill, r, border_radius=3)
            pygame.draw.rect(surface, border_c, r, 1, border_radius=3)

            col = ACCENT_GREEN if (i == self._p2_selected and self._p2_result) else TEXT_DIM
            pw  = self._fmono.render(row["plain"], True, col)
            hh  = self._fmono.render(row["hash"],  True, col)
            surface.blit(pw, (r.x + 12,  r.centery - pw.get_height() // 2))
            surface.blit(hh, (r.x + 200, r.centery - hh.get_height() // 2))

        if self._p2_result is True:
            ty = y + len(d["rainbow_table"]) * row_h + 8
            teach = self._fsm.render(d["teach_line"], True, TEXT_DIM)
            surface.blit(teach, teach.get_rect(centerx=_CX, y=ty))
            self._draw_button(surface, "NEXT PHASE", _CX - 90, ty + 26, 180)

        self._draw_feedback(surface)

    # ── Phase 3 draw ──────────────────────────────────────────────────────────

    def _draw_p3(self, surface: pygame.Surface) -> None:
        d = self._data["phase3"]
        y = _HEADER_H + 56

        self._draw_phase_title(surface, d["title"], d["headline"], y)
        y += 64

        self._draw_briefing(surface, d["briefing"], y)
        y += 54

        # User records table
        col_labels = ["Username", "Password", "Salt", "Stored Hash"]
        col_x      = [_CX - 300, _CX - 160, _CX - 20, _CX + 100]
        # Header row
        for label, cx in zip(col_labels, col_x):
            s = self._fsm.render(label, True, TEXT_MUTED)
            surface.blit(s, (cx, y))
        y += self._fsm.get_height() + 6
        pygame.draw.line(surface, BORDER, (_CX - 300, y), (_CX + 290, y), 1)
        y += 8

        reveal = min(1.0, self._p3_reveal_t / 0.8)
        for user in d["users"]:
            vals = [
                user["username"],
                user["password"],
                user["salt"] if (self._p3_result and reveal > 0.5) else "????????",
                user["hash"],
            ]
            for val, cx in zip(vals, col_x):
                col = (ACCENT_GREEN if val != "????????" and self._p3_result
                       else TEXT_DIM)
                s = self._fmono.render(str(val), True, col)
                surface.blit(s, (cx, y))
            y += self._fsm.get_height() + 8

        y += 10
        # Question
        q = self._fbody.render(d["question"], True, TEXT_PRIMARY)
        surface.blit(q, q.get_rect(centerx=_CX, y=y))
        y += q.get_height() + 12

        # Choices
        mx, my   = pygame.mouse.get_pos()
        row_h    = 44
        for i, choice in enumerate(d["choices"]):
            r = pygame.Rect(_CX - 300, y + i * row_h, 600, row_h - 4)
            if i == self._p3_selected and self._p3_result is True:
                fill, bc = (0, 40, 20), ACCENT_GREEN
            elif i == self._p3_selected and self._p3_result is False:
                fill, bc = (50, 0, 0), ACCENT_RED
            elif r.collidepoint(mx, my) and self._p3_result is None:
                fill, bc = (18, 24, 42), ACCENT_CYAN
            else:
                fill, bc = BG_MID, BORDER
            pygame.draw.rect(surface, fill, r, border_radius=4)
            pygame.draw.rect(surface, bc,   r, 1, border_radius=4)
            ls = self._fbody.render(f"  {chr(65+i)}.  {choice}", True, TEXT_PRIMARY)
            surface.blit(ls, (r.x + 10, r.centery - ls.get_height() // 2))

        if self._p3_result is True:
            ty = y + len(d["choices"]) * row_h + 8
            teach = self._fsm.render(d["teach_line"], True, TEXT_DIM)
            surface.blit(teach, teach.get_rect(centerx=_CX, y=ty))
            self._draw_button(surface, "NEXT PHASE", _CX - 90, ty + 26, 180)

        self._draw_feedback(surface)

    # ── Phase 4 draw ──────────────────────────────────────────────────────────

    def _draw_p4(self, surface: pygame.Surface) -> None:
        d = self._data["phase4"]
        y = _HEADER_H + 56

        self._draw_phase_title(surface, d["title"], d["headline"], y)
        y += 64

        self._draw_briefing(surface, d["briefing"], y)
        y += 54

        # Password input
        instr = self._fbody.render("Type your secure password:", True, TEXT_DIM)
        surface.blit(instr, instr.get_rect(centerx=_CX, y=y))
        y += instr.get_height() + 8

        inp_r = self._p4_input_rect()
        pygame.draw.rect(surface, BG_MID, inp_r, border_radius=4)
        pygame.draw.rect(surface,
                         ACCENT_CYAN if self._p4_active else BORDER,
                         inp_r, 2, border_radius=4)
        display = self._p4_password + ("|" if self._p4_active and self._p4_cursor_on else "")
        pw_s    = self._fbody.render(display, True, TEXT_PRIMARY)
        surface.blit(pw_s, (inp_r.x + 12, inp_r.centery - pw_s.get_height() // 2))
        y += inp_r.h + 14

        # Strength meter
        strength = _calc_strength(self._p4_password)
        max_s    = len(d["strength_labels"]) - 1
        s_label  = d["strength_labels"][min(strength, max_s)]
        s_col    = tuple(d["strength_colors"][min(strength, max_s)])
        bar_w    = 460
        bar_h    = 12
        bx       = _CX - bar_w // 2
        pygame.draw.rect(surface, BG_PANEL, (bx, y, bar_w, bar_h), border_radius=5)
        fill_w = int(bar_w * strength / max_s) if max_s else 0
        if fill_w > 0:
            pygame.draw.rect(surface, s_col, (bx, y, fill_w, bar_h), border_radius=5)
        sl = self._fbody.render(s_label, True, s_col)
        surface.blit(sl, (bx + bar_w + 12, y - 2))
        y += bar_h + 14

        # Requirements checklist
        for req in d["requirements"]:
            met  = _check_req(req["key"], self._p4_password)
            col  = ACCENT_GREEN if met else TEXT_MUTED
            mark = "[v]" if met else "[ ]"
            rs   = self._fsm.render(f"  {mark}  {req['label']}", True, col)
            surface.blit(rs, rs.get_rect(centerx=_CX, y=y))
            y += rs.get_height() + 4

        y += 10
        required = d["required_strength"]
        if strength >= required and not self._p4_tested:
            self._draw_button(surface, "TEST PASSWORD", _CX - 110, y, 220)

        if self._p4_tested:
            # Attack animation
            prog = self._p4_test_anim
            anim_w = 400
            ax     = _CX - anim_w // 2
            ay     = y
            pygame.draw.rect(surface, BG_MID, (ax, ay, anim_w, 30), border_radius=4)
            if prog < 1.0:
                fill_c = (int(200 * prog), 0, 0)
                pygame.draw.rect(surface, fill_c,
                                 (ax, ay, int(anim_w * prog), 30), border_radius=4)
                atxt = self._fsm.render("Dictionary attack running...", True, TEXT_DIM)
            else:
                pygame.draw.rect(surface, (0, 180, 60),
                                 (ax, ay, anim_w, 30), border_radius=4)
                atxt = self._fh1.render("ATTACK FAILED  —  Password is too strong!", True, ACCENT_GREEN)

            surface.blit(atxt, atxt.get_rect(centerx=_CX, y=ay + 6))
            y += 44

            if prog >= 1.0:
                teach = self._fsm.render(d["teach_line"], True, TEXT_DIM)
                surface.blit(teach, teach.get_rect(centerx=_CX, y=y))
                y += teach.get_height() + 12
                self._draw_button(surface, "SECURE THE VAULT", _CX - 130, y, 260)

        self._draw_feedback(surface)

    # ── footer ────────────────────────────────────────────────────────────────

    def _draw_footer(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, (0, SCREEN_HEIGHT - _FOOTER_H,
                                           SCREEN_WIDTH, _FOOTER_H))
        pygame.draw.line(surface, BORDER,
                         (0, SCREEN_HEIGHT - _FOOTER_H),
                         (SCREEN_WIDTH, SCREEN_HEIGHT - _FOOTER_H), 1)
        d = self._data
        p = self._phase if self._phase < 4 else 3
        keys = ["phase1", "phase2", "phase3", "phase4"]
        teach = d[keys[p]].get("teach_line", "")
        if teach:
            ts = self._fsm.render(teach, True, TEXT_MUTED)
            surface.blit(ts, (18, SCREEN_HEIGHT - _FOOTER_H + (_FOOTER_H - ts.get_height()) // 2))

    # ── shared draw helpers ───────────────────────────────────────────────────

    def _draw_phase_title(self, surface: pygame.Surface,
                          phase_str: str, headline: str, y: int) -> None:
        ps = self._fsm.render(phase_str, True, TEXT_MUTED)
        surface.blit(ps, ps.get_rect(centerx=_CX, y=y))
        hs = self._fh1.render(headline, True, ACCENT_ORANGE)
        surface.blit(hs, hs.get_rect(centerx=_CX, y=y + ps.get_height() + 4))

    def _draw_briefing(self, surface: pygame.Surface,
                       text: str, y: int) -> None:
        lines = self._wrap(text, self._fsm, 700)
        for line in lines:
            ls = self._fsm.render(line, True, TEXT_DIM)
            surface.blit(ls, ls.get_rect(centerx=_CX, y=y))
            y += ls.get_height() + 3

    def _draw_button(self, surface: pygame.Surface,
                     label: str, x: int, y: int, w: int) -> None:
        mx, my  = pygame.mouse.get_pos()
        r       = pygame.Rect(x, y, w, 36)
        hovered = r.collidepoint(mx, my)
        pygame.draw.rect(surface, (0, 55, 28) if hovered else BG_PANEL, r, border_radius=4)
        pygame.draw.rect(surface, ACCENT_GREEN, r, 2, border_radius=4)
        ls = self._fbody.render(label, True, ACCENT_GREEN)
        surface.blit(ls, ls.get_rect(center=r.center))

    def _btn_rect(self, label: str) -> pygame.Rect:
        """Return the Rect for a labelled button by name so click tests match draw."""
        lookup = {
            "RUN ATTACK":       (_CX - 100, _HEADER_H + 56 + 64 + 54 + 52 + 16 + 120 + 14, 200),
            "NEXT PHASE":       (-999, -999, 180),   # y varies; use per-phase click logic instead
            "TEST PASSWORD":    (_CX - 110, -999, 220),
            "SECURE THE VAULT": (_CX - 130, -999, 260),
        }
        vals = lookup.get(label, (_CX - 100, -999, 200))
        return pygame.Rect(vals[0], vals[1], vals[2], 36)

    def _draw_feedback(self, surface: pygame.Surface) -> None:
        if self._feedback and self._feedback_t > 0:
            alpha = min(1.0, self._feedback_t / 0.4)
            col   = tuple(int(c * alpha) for c in ACCENT_ORANGE)
            fs    = self._fbody.render(self._feedback, True, col)
            surface.blit(fs, fs.get_rect(centerx=_CX, y=SCREEN_HEIGHT - _FOOTER_H - 32))

    def _p4_input_rect(self) -> pygame.Rect:
        return pygame.Rect(_CX - 230, _HEADER_H + 56 + 64 + 54 + 26 + 8, 460, 36)

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
