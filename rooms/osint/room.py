import pygame
from rooms.base_room import BaseRoom
from rooms.osint.data import PUZZLE
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

# Layout constants
_HEADER_H     = 65
_FOOTER_H     = 46
_LEFT_W       = 190   # platform tab column
_RIGHT_W      = 370   # dossier column
_CENTER_W     = SCREEN_WIDTH - _LEFT_W - _RIGHT_W  # 720
_CONTENT_Y    = _HEADER_H
_CONTENT_H    = SCREEN_HEIGHT - _HEADER_H - _FOOTER_H


class Room(BaseRoom):
    """Room 2 — OSINT Investigator (fully playable)."""

    # ---------------------------------------------------------------- setup

    def setup(self) -> None:
        self._data = PUZZLE

        self._font_h1    = pygame.font.SysFont("consolas", 20, bold=True)
        self._font_body  = pygame.font.SysFont("consolas", 14)
        self._font_sm    = pygame.font.SysFont("consolas", 12)
        self._font_input = pygame.font.SysFont("consolas", 14)

        self._platforms   = list(self._data["platforms"].keys())
        self._active_pid  = self._platforms[0]
        self._scroll      = {pid: 0 for pid in self._platforms}

        # Dossier state
        self._inputs      = {f["key"]: "" for f in self._data["dossier_fields"]}
        self._active_key  = None
        self._cursor_on   = True
        self._cursor_t    = 0.0

        # Submission state
        self._submitted   = False
        self._results     = {}
        self._score       = 0
        self._result_t    = 0.0

        # Inline feedback (empty-submit guard)
        self._feedback    = ""
        self._feedback_t  = 0.0

        # Pre-compute layout rects
        self._r_header = pygame.Rect(0, 0, SCREEN_WIDTH, _HEADER_H)
        self._r_left   = pygame.Rect(0, _CONTENT_Y, _LEFT_W, _CONTENT_H)
        self._r_center = pygame.Rect(_LEFT_W, _CONTENT_Y, _CENTER_W, _CONTENT_H)
        self._r_right  = pygame.Rect(_LEFT_W + _CENTER_W, _CONTENT_Y, _RIGHT_W, _CONTENT_H)
        self._r_footer = pygame.Rect(0, SCREEN_HEIGHT - _FOOTER_H, SCREEN_WIDTH, _FOOTER_H)

        self._build_dossier_layout()

    def _build_dossier_layout(self) -> None:
        """Pre-compute every input rect and the submit button rect."""
        fh1_h  = self._font_h1.get_height()
        fsm_h  = self._font_sm.get_height()
        x0     = self._r_right.x + 14
        w      = self._r_right.w - 28
        y      = self._r_right.y + 12

        y += fh1_h + 4       # "DOSSIER" title
        y += fsm_h + 14      # subtitle

        self._field_rects: dict[str, pygame.Rect] = {}
        for field in self._data["dossier_fields"]:
            y += fsm_h + 3       # label
            self._field_rects[field["key"]] = pygame.Rect(x0, y, w, 27)
            y += 27 + 12         # input + gap

        y += 8
        self._submit_rect = pygame.Rect(x0, y, w, 36)

    # ---------------------------------------------------------------- events

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._submitted:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._handle_click(event.pos)
            elif event.button == 4:
                self._scroll[self._active_pid] = max(
                    0, self._scroll[self._active_pid] - 25
                )
            elif event.button == 5:
                max_s = self._max_scroll(self._active_pid)
                self._scroll[self._active_pid] = min(
                    self._scroll[self._active_pid] + 25, max_s
                )

        elif event.type == pygame.KEYDOWN:
            self._handle_key(event)

    def _handle_click(self, pos: tuple) -> None:
        # Platform tabs (left panel)
        if self._r_left.collidepoint(pos):
            tab_h = _CONTENT_H // len(self._platforms)
            for i, pid in enumerate(self._platforms):
                r = pygame.Rect(self._r_left.x, self._r_left.y + i * tab_h,
                                self._r_left.w, tab_h)
                if r.collidepoint(pos):
                    self._active_pid = pid
                    return

        # Dossier input fields (right panel)
        if self._r_right.collidepoint(pos):
            self._active_key = None
            for key, rect in self._field_rects.items():
                if rect.collidepoint(pos):
                    self._active_key = key
                    return
            if self._submit_rect.collidepoint(pos):
                self._do_submit()

    def _handle_key(self, event: pygame.event.Event) -> None:
        if self._active_key is None:
            return
        k = event.key
        if k == pygame.K_BACKSPACE:
            self._inputs[self._active_key] = self._inputs[self._active_key][:-1]
        elif k == pygame.K_TAB:
            keys = [f["key"] for f in self._data["dossier_fields"]]
            idx  = keys.index(self._active_key)
            self._active_key = keys[(idx + 1) % len(keys)]
        elif k == pygame.K_RETURN:
            self._active_key = None
        elif event.unicode and event.unicode.isprintable():
            if len(self._inputs[self._active_key]) < 64:
                self._inputs[self._active_key] += event.unicode

    def _do_submit(self) -> None:
        if all(v.strip() == "" for v in self._inputs.values()):
            self._feedback   = "Fill in at least one field before submitting."
            self._feedback_t = 3.0
            return

        score = 0
        for field in self._data["dossier_fields"]:
            key     = field["key"]
            entered = self._inputs[key].strip().lower()
            correct = field["answer"].lower()

            if not entered:
                self._results[key] = False
                continue

            if field.get("flexible"):
                keywords = [w for w in correct.split() if len(w) > 3]
                hit = any(kw in entered for kw in keywords)
            else:
                hit = entered == correct or correct in entered

            self._results[key] = hit
            if hit:
                score += self._data["score_per_field"]
                if field.get("easter_egg"):
                    self.game.save.set_artefact("pet_name", self._inputs[key].strip())

        self._score     = score
        self._submitted = True

    # ---------------------------------------------------------------- update

    def update(self, dt: float) -> None:
        # Blinking cursor
        self._cursor_t += dt
        if self._cursor_t >= 0.5:
            self._cursor_on = not self._cursor_on
            self._cursor_t  = 0.0

        # Feedback timer
        if self._feedback_t > 0:
            self._feedback_t -= dt

        # Result display timer — room completes after the overlay has shown
        if self._submitted:
            self._result_t += dt
            if self._result_t >= self._data["result_display_seconds"]:
                self._complete = True

    @property
    def is_complete(self) -> bool:
        return self._complete

    def get_score(self) -> int:
        return self._score

    # ---------------------------------------------------------------- draw

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_header(surface)
        self._draw_left(surface)
        self._draw_center(surface)
        self._draw_right(surface)
        self._draw_footer(surface)
        if self._submitted:
            self._draw_result_overlay(surface)

    # --- header ---

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, self._r_header)
        pygame.draw.line(surface, BORDER,
                         (0, _HEADER_H), (SCREEN_WIDTH, _HEADER_H), 1)

        title = self._font_h1.render(
            "ROOM 2  //  OSINT INVESTIGATOR", True, ACCENT_CYAN
        )
        surface.blit(title, (18, (_HEADER_H - title.get_height()) // 2))

        hint = self._font_sm.render(
            "Browse platforms, fill the dossier, submit.  |  ESC = World Map",
            True, TEXT_MUTED,
        )
        surface.blit(hint, (SCREEN_WIDTH - hint.get_width() - 18,
                            (_HEADER_H - hint.get_height()) // 2))

    # --- left: platform tabs ---

    def _draw_left(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, self._r_left)
        pygame.draw.line(surface, BORDER,
                         (_LEFT_W, _CONTENT_Y), (_LEFT_W, SCREEN_HEIGHT - _FOOTER_H), 1)

        tab_h = _CONTENT_H // len(self._platforms)
        mx, my = pygame.mouse.get_pos()

        for i, pid in enumerate(self._platforms):
            plat = self._data["platforms"][pid]
            r    = pygame.Rect(self._r_left.x, self._r_left.y + i * tab_h,
                               self._r_left.w, tab_h)
            active  = pid == self._active_pid
            hovered = r.collidepoint(mx, my)

            fill = BG_PANEL if active else (BG_MID if not hovered else (20, 26, 44))
            pygame.draw.rect(surface, fill, r)

            # Active indicator stripe
            if active:
                stripe = pygame.Rect(r.x, r.y, 4, r.h)
                pygame.draw.rect(surface, tuple(plat["color"]), stripe)

            col   = TEXT_PRIMARY if active else TEXT_DIM
            label = self._font_body.render(plat["label"], True, col)
            surface.blit(label, (r.x + 12, r.centery - label.get_height() // 2))
            pygame.draw.line(surface, BORDER, (r.x, r.bottom - 1), (r.right, r.bottom - 1), 1)

    # --- center: profile + posts ---

    def _draw_center(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_DARK, self._r_center)

        pid    = self._active_pid
        plat   = self._data["platforms"][pid]
        scroll = self._scroll[pid]

        clip_before = surface.get_clip()
        surface.set_clip(self._r_center)

        x0 = self._r_center.x + 14
        y  = self._r_center.y + 10 - scroll

        y = self._draw_profile_card(surface, plat, x0, y)
        y += 14

        for post in plat.get("posts", []):
            y = self._draw_post(surface, post, x0, y, plat["color"])
            y += 8

        surface.set_clip(clip_before)

        # Scroll shadow at top edge when scrolled down
        if scroll > 0:
            shadow = pygame.Surface((_CENTER_W, 24), pygame.SRCALPHA)
            for i in range(24):
                alpha = int(160 * (1 - i / 24))
                pygame.draw.line(shadow, (10, 12, 20, alpha), (0, i), (_CENTER_W, i))
            surface.blit(shadow, (self._r_center.x, self._r_center.y))

    def _draw_profile_card(self, surface: pygame.Surface,
                           plat: dict, x: int, y: int) -> int:
        profile = plat["profile"]
        w       = self._r_center.w - 28

        rows: list[tuple[str, pygame.font.Font, tuple]] = []

        if "display_name" in profile:
            rows.append((profile["display_name"], self._font_h1, TEXT_PRIMARY))
        if "handle" in profile:
            rows.append((profile["handle"], self._font_sm, TEXT_DIM))
        if "headline" in profile:
            rows.append((profile["headline"], self._font_body, ACCENT_CYAN))
        if profile.get("bio"):
            rows.append((profile["bio"], self._font_sm, TEXT_DIM))
        if profile.get("location"):
            rows.append(("Location: " + profile["location"], self._font_sm, ACCENT_GREEN))
        if profile.get("employer"):
            rows.append(("Employer: " + profile["employer"], self._font_sm, ACCENT_GREEN))
        if profile.get("joined"):
            rows.append((profile["joined"], self._font_sm, TEXT_MUTED))

        for exp in profile.get("experience", []):
            rows.append((
                f"  {exp['title']}  @  {exp['company']}  ({exp['duration']})",
                self._font_sm, TEXT_DIM,
            ))
        for edu in profile.get("education", []):
            rows.append((
                f"  {edu['degree']}  -  {edu['institution']}  ({edu['year']})",
                self._font_sm, TEXT_MUTED,
            ))

        line_gap = 3
        card_h   = sum(f.get_height() + line_gap for _, f, _ in rows) + 22
        card_r   = pygame.Rect(x, y, w, card_h)
        pygame.draw.rect(surface, BG_PANEL, card_r, border_radius=6)
        pygame.draw.rect(surface, tuple(plat["color"]), card_r, 1, border_radius=6)

        cy = y + 11
        for text, font, col in rows:
            surf = font.render(text, True, col)
            surface.blit(surf, (x + 12, cy))
            cy += font.get_height() + line_gap

        return y + card_h

    def _draw_post(self, surface: pygame.Surface,
                   post: dict, x: int, y: int, color: tuple) -> int:
        w       = self._r_center.w - 28
        lines   = self._wrap(post["text"], self._font_body, w - 24)
        card_h  = (len(lines) * (self._font_body.get_height() + 2)
                   + self._font_sm.get_height() + 22)

        card_r = pygame.Rect(x, y, w, card_h)
        pygame.draw.rect(surface, BG_MID, card_r, border_radius=4)
        pygame.draw.rect(surface, BORDER, card_r, 1, border_radius=4)

        cy = y + 10
        for line in lines:
            surf = self._font_body.render(line, True, TEXT_PRIMARY)
            surface.blit(surf, (x + 12, cy))
            cy += self._font_body.get_height() + 2

        ts = self._font_sm.render(post["timestamp"], True, TEXT_MUTED)
        surface.blit(ts, (x + 12, cy + 4))

        return y + card_h

    # --- right: dossier ---

    def _draw_right(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, self._r_right)
        pygame.draw.line(surface, BORDER,
                         (self._r_right.x, _CONTENT_Y),
                         (self._r_right.x, SCREEN_HEIGHT - _FOOTER_H), 1)

        x0  = self._r_right.x + 14
        fh1 = self._font_h1
        fsm = self._font_sm
        y   = self._r_right.y + 12

        title = fh1.render("DOSSIER", True, ACCENT_ORANGE)
        surface.blit(title, (x0, y))
        y += title.get_height() + 4

        sub = fsm.render("Build a profile on the target.", True, TEXT_MUTED)
        surface.blit(sub, (x0, y))
        y += sub.get_height() + 14

        # Input fields
        for field in self._data["dossier_fields"]:
            key    = field["key"]
            rect   = self._field_rects[key]
            active = self._active_key == key

            label = fsm.render(
                field["label"] + "   " + field["source_hint"], True, TEXT_DIM
            )
            surface.blit(label, (x0, rect.y - fsm.get_height() - 3))

            pygame.draw.rect(surface, BG_DARK, rect, border_radius=3)
            pygame.draw.rect(
                surface,
                ACCENT_CYAN if active else BORDER,
                rect, 1, border_radius=3,
            )

            val     = self._inputs[key]
            display = val + ("|" if active and self._cursor_on else "")
            text    = self._font_input.render(display, True, TEXT_PRIMARY)
            surface.blit(text, (rect.x + 6, rect.y + (rect.h - text.get_height()) // 2))

        # Submit button
        mx, my = pygame.mouse.get_pos()
        hovered = self._submit_rect.collidepoint(mx, my)
        pygame.draw.rect(
            surface,
            (0, 68, 38) if hovered else BG_PANEL,
            self._submit_rect, border_radius=4,
        )
        pygame.draw.rect(surface, ACCENT_GREEN, self._submit_rect, 2, border_radius=4)
        btn = self._font_body.render("SUBMIT DOSSIER", True, ACCENT_GREEN)
        surface.blit(btn, btn.get_rect(center=self._submit_rect.center))

        # Inline feedback
        if self._feedback and self._feedback_t > 0:
            fb = fsm.render(self._feedback, True, ACCENT_RED)
            surface.blit(fb, (x0, self._submit_rect.bottom + 8))

    # --- footer ---

    def _draw_footer(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, self._r_footer)
        pygame.draw.line(surface, BORDER,
                         (0, self._r_footer.y), (SCREEN_WIDTH, self._r_footer.y), 1)
        tip = self._font_sm.render(
            "Tip: Look for username reuse across platforms, "
            "timezone clues in timestamps, and what the target shares without realising it.",
            True, TEXT_MUTED,
        )
        surface.blit(tip, (18, self._r_footer.y + (_FOOTER_H - tip.get_height()) // 2))

    # --- result overlay ---

    def _draw_result_overlay(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        surface.blit(overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2
        box = pygame.Rect(cx - 290, cy - 190, 580, 380)
        pygame.draw.rect(surface, BG_PANEL, box, border_radius=8)
        pygame.draw.rect(surface, ACCENT_CYAN, box, 2, border_radius=8)

        y = box.y + 22

        title = self._font_h1.render("DOSSIER SUBMITTED", True, ACCENT_CYAN)
        surface.blit(title, title.get_rect(centerx=cx, y=y))
        y += title.get_height() + 8

        score_col = ACCENT_GREEN if self._score > 0 else ACCENT_RED
        score_s   = self._font_h1.render(
            f"Score:  {self._score} / {self._data['max_score']}", True, score_col
        )
        surface.blit(score_s, score_s.get_rect(centerx=cx, y=y))
        y += score_s.get_height() + 18

        for field in self._data["dossier_fields"]:
            key = field["key"]
            hit = self._results.get(key, False)
            col  = ACCENT_GREEN if hit else ACCENT_RED
            mark = "[OK]" if hit else "[--]"
            line = self._font_body.render(f"{mark}  {field['label']}", True, col)
            surface.blit(line, (box.x + 32, y))
            y += line.get_height() + 6

        # Countdown
        remaining = max(0.0, self._data["result_display_seconds"] - self._result_t)
        note = self._font_sm.render(
            f"Returning to world map in {remaining:.1f}s ...", True, TEXT_MUTED
        )
        surface.blit(note, note.get_rect(centerx=cx, y=box.bottom - 32))

    # ---------------------------------------------------------------- helpers

    def _max_scroll(self, pid: str) -> int:
        plat   = self._data["platforms"][pid]
        height = 240                                 # profile card estimate
        height += len(plat.get("posts", [])) * 120  # per-post estimate
        height += 30                                 # bottom padding
        return max(0, height - _CONTENT_H)

    @staticmethod
    def _wrap(text: str, font: pygame.font.Font, max_w: int) -> list[str]:
        words   = text.split()
        lines   = []
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if font.size(test)[0] <= max_w:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines
