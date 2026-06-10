"""
Room 2 — OSINT Investigator  (redesigned).

Three evidence tabs the player browses freely:
  1. Photo Metadata  — EXIF data reveals Location and Timezone
  2. Social Posts    — Cross-platform feed; one post names the target's pet
  3. Username Reuse  — Same @n3uroph0x handle across three platforms

Dossier panel (right): Name, Location, Timezone, Pet Name
Each field is submitted individually; no global SUBMIT button.
"""
import pygame
from rooms.base_room import BaseRoom
from rooms.osint.data import PUZZLE
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

_HEADER_H = 65
_FOOTER_H = 46
_BOTTOM   = SCREEN_HEIGHT - _FOOTER_H   # 674

# ── layout ────────────────────────────────────────────────────────────────────
_TAB_Y     = _HEADER_H + 6        # 71
_TAB_H     = 34
_CONTENT_Y = _HEADER_H + 48       # 113
_CONTENT_X = 14
_DIVIDER_X = 882                   # separates evidence area from dossier
_DOSSIER_X = _DIVIDER_X + 7
_DOSSIER_W = SCREEN_WIDTH - _DOSSIER_X - 6   # 385
_EV_W      = _DIVIDER_X - _CONTENT_X - 10    # evidence content width

# Dossier fixed-slot layout
_SLOT_H    = 116                   # height per dossier field slot
_DOSSIER_BASE_Y = _HEADER_H + 42  # first slot starts here


class Room(BaseRoom):
    """Room 2 — OSINT Investigator."""

    # ── setup ─────────────────────────────────────────────────────────────────

    def setup(self) -> None:
        self._data = PUZZLE
        self._tab  = 0   # 0=photo  1=posts  2=username-reuse

        self._fh1   = pygame.font.SysFont("consolas", 20, bold=True)
        self._fbody = pygame.font.SysFont("consolas", 15)
        self._fsm   = pygame.font.SysFont("consolas", 13)
        self._fmono = pygame.font.SysFont("consolas", 13)
        self._fxs   = pygame.font.SysFont("consolas", 11)

        fields = self._data["dossier_fields"]
        self._inputs:       dict[str, str]            = {f["key"]: "" for f in fields}
        self._results:      dict[str, bool | None]    = {f["key"]: None for f in fields}
        self._active:       str | None                = None
        self._hints:        dict[str, int]            = {f["key"]: 0 for f in fields}
        self._hint_visible: dict[str, bool]           = {f["key"]: False for f in fields}

        self._cursor_on = True
        self._cursor_t  = 0.0
        self._time      = 0.0

        # Populated each frame during draw — read in click handlers
        self._tab_rects:    list[pygame.Rect]      = []
        self._input_rects:  dict[str, pygame.Rect] = {}
        self._submit_rects: dict[str, pygame.Rect] = {}
        self._hint_rects:   dict[str, pygame.Rect] = {}

    # ── answer checking ───────────────────────────────────────────────────────

    def _check_answer(self, field_key: str, text: str) -> bool:
        fd     = next(f for f in self._data["dossier_fields"] if f["key"] == field_key)
        answer = fd["answer"]
        t      = text.strip()
        if fd.get("flexible"):
            for word in answer.lower().split():
                if len(word) > 3 and word in t.lower():
                    return True
            return answer.lower() in t.lower()
        return answer.lower() == t.lower()

    def _submit_field(self, key: str) -> None:
        text = self._inputs[key].strip()
        if not text:
            return
        fd      = next(f for f in self._data["dossier_fields"] if f["key"] == key)
        correct = self._check_answer(key, text)
        self._results[key] = correct
        if correct:
            if fd.get("easter_egg"):
                self.game.save.set_artefact(
                    self._data["easter_egg_artefact_key"], text
                )
            self.game.audio.play("success")
        else:
            self._inputs[key] = ""
            self.game.audio.play("error")
        self._active = None

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
        if event.type == pygame.KEYDOWN:
            self._handle_key(event)

    def _handle_click(self, pos: tuple) -> None:
        # Tabs
        for i, r in enumerate(self._tab_rects):
            if r.collidepoint(pos):
                self._tab = i
                self._active = None
                self.game.audio.play("click")
                return

        # Input field activation
        for fd in self._data["dossier_fields"]:
            key = fd["key"]
            if self._input_rects.get(key, pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
                if self._results[key] is not True:
                    if self._results[key] is False:
                        self._results[key] = None   # reset so player can retype
                    self._active = key
                    self.game.audio.play("click")
                return

        # Submit (GO) / Retry button
        for fd in self._data["dossier_fields"]:
            key = fd["key"]
            if self._submit_rects.get(key, pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
                if self._results[key] is False:
                    # RETRY: clear error state and focus the field
                    self._results[key] = None
                    self._active = key
                    self.game.audio.play("click")
                else:
                    self._submit_field(key)
                return

        # Hint button
        for fd in self._data["dossier_fields"]:
            key = fd["key"]
            if self._hint_rects.get(key, pygame.Rect(0, 0, 0, 0)).collidepoint(pos):
                if not self._hint_visible[key]:
                    self._hint_visible[key] = True
                else:
                    self._hints[key] = min(self._hints[key] + 1, len(fd["hints"]) - 1)
                self.game.audio.play("click")
                return

        self._active = None

    def _handle_key(self, event: pygame.event.Event) -> None:
        if not self._active:
            return
        k = event.key
        if k == pygame.K_BACKSPACE:
            self._inputs[self._active] = self._inputs[self._active][:-1]
        elif k in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._submit_field(self._active)
        elif event.unicode and event.unicode.isprintable():
            if len(self._inputs[self._active]) < 40:
                self._inputs[self._active] += event.unicode

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time     += dt
        self._cursor_t += dt
        if self._cursor_t >= 0.5:
            self._cursor_on = not self._cursor_on
            self._cursor_t  = 0.0

        # Room completes when all fields are correct
        if all(self._results.get(f["key"]) is True
               for f in self._data["dossier_fields"]):
            self._score    = sum(
                self._data["score_per_field"]
                for f in self._data["dossier_fields"]
                if self._results.get(f["key"])
            )
            self._complete = True

    # ── draw — top level ──────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_header(surface)
        self._draw_tabs(surface)
        pygame.draw.line(surface, BORDER,
                         (_DIVIDER_X, _HEADER_H), (_DIVIDER_X, _BOTTOM), 1)
        self._draw_dossier(surface)
        if   self._tab == 0: self._draw_photo_meta(surface)
        elif self._tab == 1: self._draw_social_posts(surface)
        else:                self._draw_username_reuse(surface)
        self._draw_footer(surface)

    # ── header ────────────────────────────────────────────────────────────────

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, (0, 0, SCREEN_WIDTH, _HEADER_H))
        pygame.draw.line(surface, BORDER, (0, _HEADER_H), (SCREEN_WIDTH, _HEADER_H), 1)
        t = self._fh1.render("ROOM 2  //  OSINT INVESTIGATOR", True, ACCENT_CYAN)
        surface.blit(t, (18, (_HEADER_H - t.get_height()) // 2))
        h = self._fsm.render("ESC = Rooms  |  M = toggle sound", True, TEXT_MUTED)
        surface.blit(h, (SCREEN_WIDTH - h.get_width() - 18,
                         (_HEADER_H - h.get_height()) // 2))

    # ── tabs ──────────────────────────────────────────────────────────────────

    def _draw_tabs(self, surface: pygame.Surface) -> None:
        labels = ["[1]  PHOTO METADATA", "[2]  SOCIAL POSTS", "[3]  USERNAME REUSE"]
        tab_w  = 248
        gap    = 10
        self._tab_rects = []
        for i, label in enumerate(labels):
            x = _CONTENT_X + i * (tab_w + gap)
            r = pygame.Rect(x, _TAB_Y, tab_w, _TAB_H)
            self._tab_rects.append(r)
            active = (i == self._tab)
            pygame.draw.rect(surface, ACCENT_CYAN if active else BG_PANEL, r, border_radius=4)
            pygame.draw.rect(surface, ACCENT_CYAN if active else BORDER,   r, 1, border_radius=4)
            ts = self._fsm.render(label, True, BG_DARK if active else TEXT_DIM)
            surface.blit(ts, ts.get_rect(center=r.center))

    # ── Evidence 1: Photo Metadata ────────────────────────────────────────────

    def _draw_photo_meta(self, surface: pygame.Surface) -> None:
        photo = self._data["photo"]
        y     = _CONTENT_Y
        x     = _CONTENT_X

        # Left: photo placeholder card
        ph_w, ph_h = 258, 186
        ph_r = pygame.Rect(x, y, ph_w, ph_h)
        pygame.draw.rect(surface, (10, 14, 26), ph_r, border_radius=5)
        pygame.draw.rect(surface, BORDER, ph_r, 1, border_radius=5)
        ico = self._fmono.render("[  JPG  ]", True, TEXT_MUTED)
        surface.blit(ico, ico.get_rect(center=(ph_r.centerx, ph_r.centery - 22)))
        fn = self._fsm.render(photo["filename"], True, TEXT_DIM)
        surface.blit(fn, fn.get_rect(centerx=ph_r.centerx, y=ph_r.centery))
        cap = self._fxs.render(photo["caption"], True, TEXT_MUTED)
        surface.blit(cap, cap.get_rect(centerx=ph_r.centerx, y=ph_r.bottom - 20))

        tip = self._fxs.render(
            "This photo was posted publicly. EXIF metadata is still attached.", True, ACCENT_CYAN
        )
        surface.blit(tip, (x, ph_r.bottom + 8))

        # Right: EXIF table
        ex = x + ph_w + 18
        ey = y
        ew = _DIVIDER_X - ex - 10

        hdr_r = pygame.Rect(ex, ey, ew, 26)
        pygame.draw.rect(surface, BG_PANEL, hdr_r, border_radius=3)
        exif_lbl = self._fbody.render("EXIF METADATA", True, ACCENT_CYAN)
        surface.blit(exif_lbl, (ex + 10, ey + 5))
        ey += hdr_r.h + 3

        kw         = int(ew * 0.38)
        row_h      = 28
        highlights = photo.get("highlight_rows", set())

        for idx, (key, val) in enumerate(photo["metadata"]):
            row_r = pygame.Rect(ex, ey, ew, row_h)
            hi    = idx in highlights
            if hi:
                pygame.draw.rect(surface, (0, 38, 58), row_r, border_radius=2)
                pygame.draw.rect(surface, ACCENT_CYAN, row_r, 1, border_radius=2)
            else:
                bg = BG_MID if idx % 2 == 0 else BG_PANEL
                pygame.draw.rect(surface, bg, row_r, border_radius=2)

            col = ACCENT_CYAN if hi else TEXT_MUTED
            vc  = ACCENT_CYAN if hi else TEXT_DIM
            ky  = row_r.centery - self._fsm.get_height() // 2
            surface.blit(self._fsm.render(key, True, col),  (ex + 10, ky))
            surface.blit(self._fmono.render(val, True, vc), (ex + kw + 10, ky))
            pygame.draw.line(surface, BORDER,
                             (ex + kw + 4, ey), (ex + kw + 4, ey + row_h), 1)
            ey += row_h + 2

        note = self._fxs.render(
            "The Location and Timezone fields reveal where and when the photo was taken.",
            True, TEXT_MUTED,
        )
        surface.blit(note, (ex, ey + 8))

    # ── Evidence 2: Social Posts ──────────────────────────────────────────────

    def _draw_social_posts(self, surface: pygame.Surface) -> None:
        y  = _CONTENT_Y
        x  = _CONTENT_X

        intro = self._fxs.render(
            "The investigation target is active across multiple platforms. All posts are publicly visible.",
            True, TEXT_MUTED,
        )
        surface.blit(intro, (x, y))
        y += intro.get_height() + 10

        for platform in self._data["social_platforms"]:
            if y > _BOTTOM - 48:
                break

            ph_r = pygame.Rect(x, y, _EV_W, 32)
            r, g, b = platform["color"]
            pygame.draw.rect(surface, (r // 5, g // 5, b // 5), ph_r, border_radius=4)
            pygame.draw.rect(surface, platform["color"], ph_r, 1, border_radius=4)
            pn = self._fbody.render(platform["name"], True, platform["color"])
            surface.blit(pn, (x + 10, ph_r.centery - pn.get_height() // 2))
            hn = self._fsm.render(platform["handle"], True, TEXT_DIM)
            surface.blit(hn, (x + 10 + pn.get_width() + 14,
                               ph_r.centery - hn.get_height() // 2))
            if platform["display_name"] != platform["handle"]:
                dn = self._fsm.render(f"  ({platform['display_name']})", True, TEXT_MUTED)
                surface.blit(dn, (x + 10 + pn.get_width() + 14 + hn.get_width(),
                                  ph_r.centery - dn.get_height() // 2))
            y += ph_r.h + 2

            for post in platform["posts"]:
                if y > _BOTTOM - 36:
                    break
                lines  = self._wrap(post["text"], self._fsm, _EV_W - 24)
                card_h = max(44, len(lines) * (self._fsm.get_height() + 2) + 20)
                card_r = pygame.Rect(x, y, _EV_W, card_h)
                hi     = post.get("highlight", False)
                if hi:
                    pygame.draw.rect(surface, (0, 38, 16), card_r, border_radius=3)
                    pygame.draw.rect(surface, ACCENT_GREEN, card_r, 1, border_radius=3)
                else:
                    pygame.draw.rect(surface, BG_MID, card_r, border_radius=3)
                    pygame.draw.rect(surface, BORDER, card_r, 1, border_radius=3)
                tc = TEXT_PRIMARY if hi else TEXT_DIM
                ty = y + 8
                for line in lines:
                    ls = self._fsm.render(line, True, tc)
                    surface.blit(ls, (x + 10, ty))
                    ty += ls.get_height() + 2
                ts = self._fxs.render(
                    post["timestamp"], True, ACCENT_GREEN if hi else TEXT_MUTED
                )
                surface.blit(ts, (x + _EV_W - ts.get_width() - 10,
                                  y + card_h - ts.get_height() - 6))
                y += card_h + 3
            y += 10

    # ── Evidence 3: Username Reuse ────────────────────────────────────────────

    def _draw_username_reuse(self, surface: pygame.Surface) -> None:
        y  = _CONTENT_Y
        x  = _CONTENT_X

        title = self._fbody.render(
            "SAME USERNAME DETECTED ACROSS PLATFORMS", True, ACCENT_ORANGE
        )
        surface.blit(title, (x, y))
        y += title.get_height() + 4

        sub = self._fxs.render(
            "When the same handle appears on multiple platforms, all activity can be linked to one person.",
            True, TEXT_DIM,
        )
        surface.blit(sub, (x, y))
        y += sub.get_height() + 16

        accounts = self._data["username_accounts"]
        n        = len(accounts)
        card_w   = (_EV_W - (n - 1) * 12) // n
        card_h   = 148
        card_y   = y

        for i, acc in enumerate(accounts):
            cx = x + i * (card_w + 12)
            cr = pygame.Rect(cx, card_y, card_w, card_h)
            r, g, b = acc["color"]
            pygame.draw.rect(surface, (r // 6, g // 6, b // 6), cr, border_radius=6)
            pygame.draw.rect(surface, acc["color"], cr, 2, border_radius=6)

            pn = self._fbody.render(acc["platform"], True, acc["color"])
            surface.blit(pn, pn.get_rect(centerx=cr.centerx, y=cr.y + 12))

            hn = self._fmono.render(acc["handle"], True, TEXT_PRIMARY)
            if hn.get_width() > card_w - 14:
                hn = self._fxs.render(acc["handle"], True, TEXT_PRIMARY)
            surface.blit(hn, hn.get_rect(centerx=cr.centerx, y=cr.y + 46))

            pygame.draw.line(surface, acc["color"],
                             (cr.x + 10, cr.y + 82), (cr.right - 10, cr.y + 82), 1)

            dn = self._fxs.render(acc["real_name"], True, TEXT_DIM)
            surface.blit(dn, dn.get_rect(centerx=cr.centerx, y=cr.y + 90))

        # Bracket connector
        bracket_y = card_y + card_h + 12
        pts_x     = [x + i * (card_w + 12) + card_w // 2 for i in range(n)]
        pygame.draw.line(surface, ACCENT_ORANGE,
                         (pts_x[0], bracket_y), (pts_x[-1], bracket_y), 2)
        for px in pts_x:
            pygame.draw.line(surface, ACCENT_ORANGE,
                             (px, card_y + card_h + 2), (px, bracket_y), 2)
            pygame.draw.circle(surface, ACCENT_ORANGE, (px, bracket_y), 4)

        mid_x = (pts_x[0] + pts_x[-1]) // 2
        msg   = self._fbody.render(
            "These accounts belong to the same person.", True, ACCENT_ORANGE
        )
        surface.blit(msg, msg.get_rect(centerx=mid_x, y=bracket_y + 10))

        ey = bracket_y + msg.get_height() + 26
        for line in [
            "Investigators cross-reference usernames to link activity across the internet.",
            "Even without real names, a unique handle connects every post to one individual.",
        ]:
            ls = self._fxs.render(line, True, TEXT_DIM)
            surface.blit(ls, (x, ey))
            ey += ls.get_height() + 4

    # ── Dossier panel ─────────────────────────────────────────────────────────

    def _draw_dossier(self, surface: pygame.Surface) -> None:
        dx = _DOSSIER_X
        dw = _DOSSIER_W

        pygame.draw.rect(surface, BG_PANEL,
                         pygame.Rect(dx, _HEADER_H, dw, _BOTTOM - _HEADER_H))

        hdr = self._fbody.render("TARGET DOSSIER", True, ACCENT_CYAN)
        surface.blit(hdr, (dx + 8, _HEADER_H + 8))
        pygame.draw.line(surface, BORDER,
                         (dx, _HEADER_H + 30), (dx + dw, _HEADER_H + 30), 1)

        self._input_rects  = {}
        self._submit_rects = {}
        self._hint_rects   = {}
        mx, my = pygame.mouse.get_pos()

        for i, fd in enumerate(self._data["dossier_fields"]):
            key    = fd["key"]
            result = self._results[key]
            active = self._active == key
            fy     = _DOSSIER_BASE_Y + i * _SLOT_H

            # Label
            lbl_col = (ACCENT_GREEN if result is True  else
                       ACCENT_RED   if result is False else
                       TEXT_MUTED)
            surface.blit(
                self._fsm.render(fd["label"] + ":", True, lbl_col),
                (dx + 8, fy),
            )

            # Input box
            inp_w = dw - 58
            inp_r = pygame.Rect(dx + 8, fy + 18, inp_w, 30)
            self._input_rects[key] = inp_r

            if result is True:
                fill, bc = (0, 26, 12), ACCENT_GREEN
            elif result is False:
                fill, bc = (28, 0, 0), ACCENT_RED
            else:
                fill = BG_MID
                bc   = ACCENT_CYAN if active else BORDER

            pygame.draw.rect(surface, fill, inp_r, border_radius=3)
            pygame.draw.rect(surface, bc,   inp_r, 1, border_radius=3)

            if result is True:
                txt = self._fmono.render(self._inputs[key], True, ACCENT_GREEN)
            elif result is False:
                txt = self._fmono.render("Try again", True, ACCENT_RED)
            else:
                cur = "|" if (active and self._cursor_on) else ""
                txt = self._fmono.render(self._inputs[key] + cur, True, TEXT_PRIMARY)
            surface.blit(txt, (inp_r.x + 6, inp_r.centery - txt.get_height() // 2))

            # GO / RETRY button
            go_r = pygame.Rect(inp_r.right + 4, fy + 18, 44, 30)
            if result is not True:
                self._submit_rects[key] = go_r
                go_h = go_r.collidepoint(mx, my)
                if result is False:
                    pygame.draw.rect(surface, (40, 0, 0) if go_h else BG_PANEL, go_r, border_radius=3)
                    pygame.draw.rect(surface, ACCENT_RED, go_r, 1, border_radius=3)
                    gol = self._fxs.render("RETRY", True, ACCENT_RED)
                else:
                    pygame.draw.rect(surface, (0, 40, 20) if go_h else BG_PANEL, go_r, border_radius=3)
                    pygame.draw.rect(surface, ACCENT_GREEN, go_r, 1, border_radius=3)
                    gol = self._fxs.render("GO", True, ACCENT_GREEN)
                surface.blit(gol, gol.get_rect(center=go_r.center))
            else:
                ok = self._fxs.render("[OK]", True, ACCENT_GREEN)
                surface.blit(ok, (go_r.x + 2, go_r.centery - ok.get_height() // 2))

            # "Incorrect" feedback or Hint button
            if result is False:
                err = self._fxs.render("Incorrect — click RETRY or the field to try again.", True, ACCENT_RED)
                surface.blit(err, (dx + 8, fy + 53))
                # Hint button shifted down
                hr = pygame.Rect(dx + 8, fy + 70, 60, 18)
                self._hint_rects[key] = hr
                hbh = hr.collidepoint(mx, my)
                pygame.draw.rect(surface, BG_PANEL, hr, border_radius=2)
                pygame.draw.rect(surface,
                                 (255, 180, 0) if hbh else ACCENT_ORANGE,
                                 hr, 1, border_radius=2)
                hl = self._fxs.render("? HINT", True, ACCENT_ORANGE)
                surface.blit(hl, hl.get_rect(center=hr.center))
            elif result is not True:
                hr = pygame.Rect(dx + 8, fy + 53, 60, 18)
                self._hint_rects[key] = hr
                hbh = hr.collidepoint(mx, my)
                pygame.draw.rect(surface, BG_PANEL, hr, border_radius=2)
                pygame.draw.rect(surface,
                                 (255, 180, 0) if hbh else ACCENT_ORANGE,
                                 hr, 1, border_radius=2)
                hl = self._fxs.render("? HINT", True, ACCENT_ORANGE)
                surface.blit(hl, hl.get_rect(center=hr.center))

            # Hint text
            hint_y = fy + 92 if result is False else fy + 75
            if self._hint_visible[key] and result is not True:
                hints     = fd["hints"]
                idx       = self._hints[key]
                hint_text = hints[min(idx, len(hints) - 1)]
                hy        = hint_y
                for hline in self._wrap(hint_text, self._fxs, dw - 18):
                    hs = self._fxs.render(hline, True, ACCENT_ORANGE)
                    surface.blit(hs, (dx + 8, hy))
                    hy += hs.get_height() + 2

        # Score
        score_y = _DOSSIER_BASE_Y + len(self._data["dossier_fields"]) * _SLOT_H + 6
        pygame.draw.line(surface, BORDER, (dx, score_y), (dx + dw, score_y), 1)
        score_y += 8

        done_count = sum(1 for f in self._data["dossier_fields"]
                         if self._results.get(f["key"]) is True)
        score  = done_count * self._data["score_per_field"]
        max_sc = self._data["max_score"]
        sc_col = ACCENT_GREEN if done_count == len(self._data["dossier_fields"]) else TEXT_DIM
        sc     = self._fbody.render(f"Score:  {score}  /  {max_sc}", True, sc_col)
        surface.blit(sc, (dx + 8, score_y))

        if done_count == len(self._data["dossier_fields"]):
            done = self._fsm.render("DOSSIER COMPLETE", True, ACCENT_GREEN)
            surface.blit(done, (dx + 8, score_y + sc.get_height() + 6))

    # ── footer ────────────────────────────────────────────────────────────────

    def _draw_footer(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, (0, _BOTTOM, SCREEN_WIDTH, _FOOTER_H))
        pygame.draw.line(surface, BORDER, (0, _BOTTOM), (SCREEN_WIDTH, _BOTTOM), 1)
        edu = self._fsm.render(
            "OSINT: Publicly available information can be combined to reveal sensitive details.",
            True, TEXT_MUTED,
        )
        surface.blit(edu, edu.get_rect(
            centerx=(_CONTENT_X + _DIVIDER_X) // 2,
            y=_BOTTOM + (_FOOTER_H - edu.get_height()) // 2,
        ))

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
