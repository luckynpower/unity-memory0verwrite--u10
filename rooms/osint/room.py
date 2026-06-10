"""
Room 2 — OSINT Investigator (fully playable).

Layout (1280 × 720):
  ┌─ Header (65px) ──────────────────────────────────────────────────┐
  ├─ Objective bar (40px) ───────────────────────────────────────────┤
  ├── Left tabs (190px) ─┬─── Center feed (700px) ──┬─ Dossier (390px) ─┤
  └─ Footer (46px) ──────────────────────────────────────────────────┘
"""
import pygame
from rooms.base_room import BaseRoom
from rooms.osint.data import PUZZLE
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE, ACCENT_YELLOW,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

MAX_SCORE = PUZZLE["max_score"]

_HEADER_H  = 65
_OBJBAR_H  = 38
_FOOTER_H  = 44
_LEFT_W    = 190
_RIGHT_W   = 390
_CENTER_W  = SCREEN_WIDTH - _LEFT_W - _RIGHT_W          # 700
_CONTENT_Y = _HEADER_H + _OBJBAR_H
_CONTENT_H = SCREEN_HEIGHT - _CONTENT_Y - _FOOTER_H


class Room(BaseRoom):
    """Room 2 — OSINT Investigator."""

    # ── setup ─────────────────────────────────────────────────────────────────

    def setup(self) -> None:
        self._data = PUZZLE

        self._fh1    = pygame.font.SysFont("consolas", 19, bold=True)
        self._fbody  = pygame.font.SysFont("consolas", 14)
        self._fsm    = pygame.font.SysFont("consolas", 12)
        self._finput = pygame.font.SysFont("consolas", 14)

        self._platforms  = list(self._data["platforms"].keys())
        self._active_pid = self._platforms[0]
        self._scroll     = {pid: 0 for pid in self._platforms}

        # Dossier
        self._inputs      = {f["key"]: "" for f in self._data["dossier_fields"]}
        self._active_key  = None
        self._cursor_on   = True
        self._cursor_t    = 0.0

        # Hints: track how many times each field's hint has been requested (0, 1, 2)
        self._hint_level  = {f["key"]: 0 for f in self._data["dossier_fields"]}
        self._hint_score_penalty = 0

        # Submission
        self._submitted   = False
        self._results: dict[str, bool] = {}
        self._score       = 0
        self._result_t    = 0.0

        # Inline feedback
        self._feedback    = ""
        self._feedback_t  = 0.0

        # Layout pre-computation
        self._r_header  = pygame.Rect(0, 0, SCREEN_WIDTH, _HEADER_H)
        self._r_objbar  = pygame.Rect(0, _HEADER_H, SCREEN_WIDTH, _OBJBAR_H)
        self._r_left    = pygame.Rect(0, _CONTENT_Y, _LEFT_W, _CONTENT_H)
        self._r_center  = pygame.Rect(_LEFT_W, _CONTENT_Y, _CENTER_W, _CONTENT_H)
        self._r_right   = pygame.Rect(_LEFT_W + _CENTER_W, _CONTENT_Y, _RIGHT_W, _CONTENT_H)
        self._r_footer  = pygame.Rect(0, SCREEN_HEIGHT - _FOOTER_H, SCREEN_WIDTH, _FOOTER_H)

        self._build_dossier_layout()

    def _build_dossier_layout(self) -> None:
        x0 = self._r_right.x + 14
        w  = self._r_right.w - 28
        y  = self._r_right.y + 10

        y += self._fh1.get_height()  + 4   # "DOSSIER" title
        y += self._fsm.get_height()  + 4   # progress line
        y += self._fsm.get_height()  + 12  # separator + gap

        self._field_rects:  dict[str, pygame.Rect] = {}
        self._hint_btn_rects: dict[str, pygame.Rect] = {}

        for field in self._data["dossier_fields"]:
            y += self._fsm.get_height() + 3  # label
            input_w = w - 32
            self._field_rects[field["key"]]    = pygame.Rect(x0, y, input_w, 27)
            self._hint_btn_rects[field["key"]] = pygame.Rect(x0 + input_w + 4, y, 26, 27)
            y += 27 + 10

        y += 6
        self._submit_rect = pygame.Rect(x0, y, w, 36)

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._submitted:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._handle_click(event.pos)
            elif event.button == 4:
                self._scroll[self._active_pid] = max(
                    0, self._scroll[self._active_pid] - 28)
            elif event.button == 5:
                self._scroll[self._active_pid] = min(
                    self._scroll[self._active_pid] + 28,
                    self._max_scroll(self._active_pid))

        elif event.type == pygame.KEYDOWN:
            self._handle_key(event)

    def _handle_click(self, pos: tuple) -> None:
        # Platform tabs
        if self._r_left.collidepoint(pos):
            tab_h = _CONTENT_H // len(self._platforms)
            for i, pid in enumerate(self._platforms):
                r = pygame.Rect(self._r_left.x,
                                self._r_left.y + i * tab_h,
                                self._r_left.w, tab_h)
                if r.collidepoint(pos):
                    self._active_pid = pid
                    return

        if self._r_right.collidepoint(pos):
            self._active_key = None

            # Hint buttons
            for key, rect in self._hint_btn_rects.items():
                if rect.collidepoint(pos):
                    self._request_hint(key)
                    return

            # Input fields
            for key, rect in self._field_rects.items():
                if rect.collidepoint(pos):
                    self._active_key = key
                    return

            # Submit
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
            if len(self._inputs[self._active_key]) < 60:
                self._inputs[self._active_key] += event.unicode

    def _request_hint(self, key: str) -> None:
        level = self._hint_level[key]
        if level >= 2:
            self._set_feedback("No more hints for this field.")
            return
        self._hint_level[key] += 1
        self._hint_score_penalty += 15
        field = next(f for f in self._data["dossier_fields"] if f["key"] == key)
        hint  = field["hints"][level]
        self._set_feedback(f"Hint: {hint}  (-15 pts)")

    def _do_submit(self) -> None:
        if all(v.strip() == "" for v in self._inputs.values()):
            self._set_feedback("Fill in at least one field before submitting.")
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
                    self.game.save.set_artefact(
                        self._data["easter_egg_artefact_key"],
                        self._inputs[key].strip(),
                    )

        self._score     = max(0, score - self._hint_score_penalty)
        self._submitted = True

    def _set_feedback(self, msg: str, duration: float = 3.5) -> None:
        self._feedback   = msg
        self._feedback_t = duration

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._cursor_t += dt
        if self._cursor_t >= 0.5:
            self._cursor_on = not self._cursor_on
            self._cursor_t  = 0.0

        if self._feedback_t > 0:
            self._feedback_t -= dt

        if self._submitted:
            self._result_t += dt
            if self._result_t >= self._data["result_display_seconds"]:
                self._complete = True

    @property
    def is_complete(self) -> bool:
        return self._complete

    def get_score(self) -> int:
        return self._score

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_header(surface)
        self._draw_objective_bar(surface)
        self._draw_left(surface)
        self._draw_center(surface)
        self._draw_right(surface)
        self._draw_footer(surface)
        if self._submitted:
            self._draw_result_overlay(surface)

    # ── header ────────────────────────────────────────────────────────────────

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, self._r_header)
        pygame.draw.line(surface, BORDER,
                         (0, _HEADER_H), (SCREEN_WIDTH, _HEADER_H), 1)
        title = self._fh1.render(
            "ROOM 2  //  OSINT INVESTIGATOR", True, ACCENT_CYAN)
        surface.blit(title, (18, (_HEADER_H - title.get_height()) // 2))

        hint = self._fsm.render(
            "Browse platforms  ->  fill the dossier  ->  SUBMIT  |  ESC = Rooms  |  [?] = hint",
            True, TEXT_MUTED,
        )
        surface.blit(hint, (SCREEN_WIDTH - hint.get_width() - 18,
                            (_HEADER_H - hint.get_height()) // 2))

    # ── objective bar ─────────────────────────────────────────────────────────

    def _draw_objective_bar(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (12, 16, 28), self._r_objbar)
        pygame.draw.line(surface, BORDER,
                         (0, self._r_objbar.bottom),
                         (SCREEN_WIDTH, self._r_objbar.bottom), 1)

        label = self._fsm.render("FIND:", True, TEXT_MUTED)
        x = 18
        y = self._r_objbar.y + (self._r_objbar.h - label.get_height()) // 2
        surface.blit(label, (x, y))
        x += label.get_width() + 12

        for field in self._data["dossier_fields"]:
            key     = field["key"]
            filled  = bool(self._inputs[key].strip())
            correct = self._results.get(key, None)

            if correct is True:
                col, prefix = ACCENT_GREEN, "[OK] "
            elif correct is False:
                col, prefix = ACCENT_RED, "[X]  "
            elif filled:
                col, prefix = ACCENT_YELLOW, "[?]  "
            else:
                col, prefix = TEXT_DIM, "[ ]  "

            tag = self._fsm.render(prefix + field["label"], True, col)
            if x + tag.get_width() > SCREEN_WIDTH - 100:
                break
            surface.blit(tag, (x, y))
            x += tag.get_width() + 18

        # Hint penalty indicator
        if self._hint_score_penalty > 0:
            pen = self._fsm.render(
                f"Hint penalty: -{self._hint_score_penalty} pts", True, ACCENT_ORANGE
            )
            surface.blit(pen, (SCREEN_WIDTH - pen.get_width() - 18, y))

    # ── left: platform tabs ───────────────────────────────────────────────────

    def _draw_left(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, self._r_left)
        pygame.draw.line(surface, BORDER,
                         (_LEFT_W, _CONTENT_Y), (_LEFT_W, SCREEN_HEIGHT - _FOOTER_H), 1)

        tab_h   = _CONTENT_H // len(self._platforms)
        mx, my  = pygame.mouse.get_pos()

        for i, pid in enumerate(self._platforms):
            plat   = self._data["platforms"][pid]
            r      = pygame.Rect(self._r_left.x,
                                 self._r_left.y + i * tab_h,
                                 self._r_left.w, tab_h)
            active  = pid == self._active_pid
            hovered = r.collidepoint(mx, my)

            fill = BG_PANEL if active else (BG_MID if not hovered else (18, 24, 42))
            pygame.draw.rect(surface, fill, r)
            if active:
                pygame.draw.rect(surface, tuple(plat["color"]),
                                 pygame.Rect(r.x, r.y, 4, r.h))

            col   = TEXT_PRIMARY if active else TEXT_DIM
            label = self._fbody.render(plat["label"], True, col)
            surface.blit(label, (r.x + 10, r.centery - label.get_height() // 2))
            pygame.draw.line(surface, BORDER, (r.x, r.bottom - 1), (r.right, r.bottom - 1), 1)

    # ── center: profile + posts ───────────────────────────────────────────────

    def _draw_center(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_DARK, self._r_center)

        pid    = self._active_pid
        plat   = self._data["platforms"][pid]
        scroll = self._scroll[pid]

        clip = surface.get_clip()
        surface.set_clip(self._r_center)

        x0 = self._r_center.x + 14
        y  = self._r_center.y + 10 - scroll

        y = self._draw_profile_card(surface, plat, x0, y)
        y += 12

        for post in plat.get("posts", []):
            y = self._draw_post(surface, post, x0, y, plat["color"])
            y += 8

        surface.set_clip(clip)

        # Scroll shadow at top
        if scroll > 0:
            shadow = pygame.Surface((_CENTER_W, 20), pygame.SRCALPHA)
            for i in range(20):
                a = int(140 * (1 - i / 20))
                pygame.draw.line(shadow, (8, 10, 18, a), (0, i), (_CENTER_W, i))
            surface.blit(shadow, (self._r_center.x, self._r_center.y))

    def _draw_profile_card(self, surface: pygame.Surface,
                           plat: dict, x: int, y: int) -> int:
        profile = plat["profile"]
        w       = self._r_center.w - 28
        rows: list[tuple] = []

        if "display_name" in profile:
            rows.append((profile["display_name"], self._fh1, TEXT_PRIMARY))
        if "handle" in profile:
            rows.append((profile["handle"], self._fsm, TEXT_DIM))
        if "headline" in profile:
            rows.append((profile["headline"], self._fbody, ACCENT_CYAN))
        if profile.get("bio"):
            rows.append((profile["bio"], self._fsm, TEXT_DIM))
        if profile.get("location"):
            rows.append(("Location: " + profile["location"], self._fsm, ACCENT_GREEN))
        if profile.get("employer"):
            rows.append(("Employer: " + profile["employer"], self._fsm, ACCENT_GREEN))
        if profile.get("joined"):
            rows.append((profile["joined"], self._fsm, TEXT_MUTED))
        for exp in profile.get("experience", []):
            if not isinstance(exp, dict):
                continue
            rows.append((
                f"  {exp.get('title','?')}  @  {exp.get('company','?')}  ({exp.get('duration','?')})",
                self._fsm, TEXT_DIM,
            ))
        for edu in profile.get("education", []):
            if not isinstance(edu, dict):
                continue
            rows.append((
                f"  {edu.get('degree','?')}  -  {edu.get('institution','?')}  ({edu.get('year','?')})",
                self._fsm, TEXT_MUTED,
            ))

        gap   = 3
        card_h = sum(f.get_height() + gap for _, f, _ in rows) + 22
        card   = pygame.Rect(x, y, w, card_h)
        pygame.draw.rect(surface, BG_PANEL, card, border_radius=6)
        pygame.draw.rect(surface, tuple(plat["color"]), card, 1, border_radius=6)

        cy = y + 11
        for text, font, col in rows:
            s = font.render(text, True, col)
            surface.blit(s, (x + 12, cy))
            cy += font.get_height() + gap

        return y + card_h

    def _draw_post(self, surface: pygame.Surface,
                   post: dict, x: int, y: int, color: tuple) -> int:
        w      = self._r_center.w - 28
        lines  = self._wrap(post["text"], self._fbody, w - 24)
        card_h = (len(lines) * (self._fbody.get_height() + 2)
                  + self._fsm.get_height() + 22)

        # Subtle glow border on posts that contain a clue key — helps players notice them
        ck      = post.get("clue_key", "")
        has_hit = ck and self._results.get(ck) is True
        border  = ACCENT_GREEN if has_hit else BORDER

        card = pygame.Rect(x, y, w, card_h)
        pygame.draw.rect(surface, BG_MID, card, border_radius=4)
        pygame.draw.rect(surface, border, card, 1, border_radius=4)

        cy = y + 10
        for line in lines:
            s = self._fbody.render(line, True, TEXT_PRIMARY)
            surface.blit(s, (x + 12, cy))
            cy += self._fbody.get_height() + 2

        ts = self._fsm.render(post["timestamp"], True, TEXT_MUTED)
        surface.blit(ts, (x + 12, cy + 4))

        return y + card_h

    # ── right: dossier ────────────────────────────────────────────────────────

    def _draw_right(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, self._r_right)
        pygame.draw.line(surface, BORDER,
                         (self._r_right.x, _CONTENT_Y),
                         (self._r_right.x, SCREEN_HEIGHT - _FOOTER_H), 1)

        x0 = self._r_right.x + 14
        y  = self._r_right.y + 10

        # Title
        title = self._fh1.render("DOSSIER", True, ACCENT_ORANGE)
        surface.blit(title, (x0, y))
        y += title.get_height() + 4

        # Progress
        filled_count = sum(1 for v in self._inputs.values() if v.strip())
        prog = self._fsm.render(
            f"Fields filled:  {filled_count} / {len(self._data['dossier_fields'])}",
            True, ACCENT_GREEN if filled_count > 0 else TEXT_MUTED,
        )
        surface.blit(prog, (x0, y))
        y += prog.get_height() + 4

        pygame.draw.line(surface, BORDER,
                         (x0, y), (self._r_right.right - 14, y), 1)
        y += 12

        # Fields
        mx, my = pygame.mouse.get_pos()
        for field in self._data["dossier_fields"]:
            key    = field["key"]
            rect   = self._field_rects[key]
            hrect  = self._hint_btn_rects[key]
            active = self._active_key == key
            level  = self._hint_level[key]

            label_col = TEXT_DIM if not self._results.get(key) else ACCENT_GREEN
            label = self._fsm.render(field["label"], True, label_col)
            surface.blit(label, (x0, rect.y - self._fsm.get_height() - 3))

            # Input box
            pygame.draw.rect(surface, BG_DARK, rect, border_radius=3)
            pygame.draw.rect(surface,
                             ACCENT_CYAN if active else BORDER,
                             rect, 1, border_radius=3)

            val     = self._inputs[key]
            display = val + ("|" if active and self._cursor_on else "")
            ts      = self._finput.render(display, True, TEXT_PRIMARY)
            surface.blit(ts, (rect.x + 6,
                               rect.y + (rect.h - ts.get_height()) // 2))

            # Hint button [?]
            hint_hov = hrect.collidepoint(mx, my)
            hcol     = ACCENT_ORANGE if level < 2 else TEXT_MUTED
            hbg      = (40, 22, 0) if hint_hov and level < 2 else BG_PANEL
            pygame.draw.rect(surface, hbg, hrect, border_radius=3)
            pygame.draw.rect(surface, hcol, hrect, 1, border_radius=3)
            hs = self._fsm.render("?", True, hcol)
            surface.blit(hs, hs.get_rect(center=hrect.center))

        # Submit
        sub_hov  = self._submit_rect.collidepoint(mx, my)
        sub_fill = (0, 60, 32) if sub_hov else BG_PANEL
        pygame.draw.rect(surface, sub_fill, self._submit_rect, border_radius=4)
        pygame.draw.rect(surface, ACCENT_GREEN, self._submit_rect, 2, border_radius=4)
        slbl = self._fbody.render("SUBMIT DOSSIER", True, ACCENT_GREEN)
        surface.blit(slbl, slbl.get_rect(center=self._submit_rect.center))

        # Inline feedback (hints / errors)
        if self._feedback and self._feedback_t > 0:
            alpha  = min(1.0, self._feedback_t / 0.4)
            fb_col = tuple(int(c * alpha) for c in ACCENT_ORANGE)
            fb = self._fsm.render(self._feedback, True, fb_col)
            fy = self._submit_rect.bottom + 8
            # wrap if too long
            if fb.get_width() > self._r_right.w - 28:
                for part in self._wrap(self._feedback, self._fsm, self._r_right.w - 28):
                    ps = self._fsm.render(part, True, fb_col)
                    surface.blit(ps, (x0, fy))
                    fy += ps.get_height() + 2
            else:
                surface.blit(fb, (x0, fy))

    # ── footer ────────────────────────────────────────────────────────────────

    def _draw_footer(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, self._r_footer)
        pygame.draw.line(surface, BORDER,
                         (0, self._r_footer.y),
                         (SCREEN_WIDTH, self._r_footer.y), 1)
        tip = self._fsm.render(
            "Tip: People reveal more online than they realise. "
            "Look for username reuse, timestamps, location tags, and casual mentions.",
            True, TEXT_MUTED,
        )
        surface.blit(tip, (18,
                           self._r_footer.y + (self._r_footer.h - tip.get_height()) // 2))

    # ── result overlay ────────────────────────────────────────────────────────

    def _draw_result_overlay(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        surface.blit(overlay, (0, 0))

        cx  = SCREEN_WIDTH  // 2
        cy  = SCREEN_HEIGHT // 2
        box = pygame.Rect(cx - 300, cy - 200, 600, 400)
        pygame.draw.rect(surface, BG_PANEL, box, border_radius=8)
        pygame.draw.rect(surface, ACCENT_CYAN, box, 2, border_radius=8)

        y = box.y + 22
        t = self._fh1.render("DOSSIER SUBMITTED", True, ACCENT_CYAN)
        surface.blit(t, t.get_rect(centerx=cx, y=y));  y += t.get_height() + 8

        s_col = ACCENT_GREEN if self._score > 0 else ACCENT_RED
        sc    = self._fh1.render(
            f"Score:  {self._score} / {self._data['max_score']}", True, s_col
        )
        surface.blit(sc, sc.get_rect(centerx=cx, y=y));  y += sc.get_height() + 16

        for field in self._data["dossier_fields"]:
            key = field["key"]
            hit = self._results.get(key, False)
            col  = ACCENT_GREEN if hit else ACCENT_RED
            mark = "[OK]" if hit else "[--]"
            line = self._fbody.render(f"{mark}  {field['label']}", True, col)
            surface.blit(line, (box.x + 32, y));  y += line.get_height() + 6

        remaining = max(0.0, self._data["result_display_seconds"] - self._result_t)
        note = self._fsm.render(
            f"Returning to rooms in {remaining:.1f}s ...", True, TEXT_MUTED
        )
        surface.blit(note, note.get_rect(centerx=cx, y=box.bottom - 32))

    # ── helpers ───────────────────────────────────────────────────────────────

    def _max_scroll(self, pid: str) -> int:
        plat = self._data["platforms"][pid]
        h    = 240 + len(plat.get("posts", [])) * 130 + 30
        return max(0, h - _CONTENT_H)

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
