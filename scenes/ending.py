"""
Ending scene — cinematic conclusion when all available rooms are cleared.
Stages:
  0  fragment convergence animation (auto, ~2.8 s)
  1  memory returning  (typewriter, SPACE to advance)
  2  virus collapsing  (typewriter, SPACE to advance)
  3  system restored   (typewriter, SPACE to advance)
  4  statistics + buttons
"""
import math
import pygame
import core.fx as fx
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ROOMS,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE, ACCENT_GOLD,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

_CHARS_PER_SEC    = 40.0
_STAGE_0_DURATION = 2.8     # auto-advance from stage 0 after this many seconds

_STORIES: dict[int, str] = {
    1: "\n".join([
        "The fragments rush back. Not all at once — but in waves.",
        "",
        "First: the weight of how much you had left exposed.",
        "The profile. The coordinates. The name that wasn't yours,",
        "but taught you how little truly stays hidden.",
        "",
        "Then: the sensation of a lock giving way.",
        "Not forced. Just understood.",
        "",
        "Your name. Your purpose. The reason you entered this place.",
        "It all returns.",
    ]),
    2: "\n".join([
        "The virus fractures.",
        "",
        "It fed on confusion — on the gaps between",
        "what you knew and what you thought you knew.",
        "",
        "But you filled those gaps.",
        "You read the profiles others left unguarded.",
        "You understood the locks others trusted blindly.",
        "",
        "Without confusion to feed on, it loses its hold.",
        "Sector by sector, the corruption clears.",
    ]),
    3: "\n".join([
        "The exit materialises.",
        "For the first time since you arrived, you can see it clearly.",
        "",
        "You step through — carrying more than you came with.",
        "Every technique proven. Every weakness understood.",
        "",
        "These are not borrowed skills.",
        "They are yours now.",
        "",
        "Identity restored.   Threat eliminated.   Mission complete.",
    ]),
}

# Fragment slot constants — match intro.py so stage 0 starts from the same row
_N     = len(ROOMS)
_SW    = 60
_SH    = 52
_SGAP  = 12
_SX0   = (SCREEN_WIDTH - (_N * _SW + (_N - 1) * _SGAP)) // 2
_SY    = 290
_CX    = SCREEN_WIDTH  // 2
_CY    = SCREEN_HEIGHT // 2


class Ending(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._font_h1   = pygame.font.SysFont("consolas", 32, bold=True)
        self._font_h2   = pygame.font.SysFont("consolas", 22, bold=True)
        self._font_h3   = pygame.font.SysFont("consolas", 20, bold=True)
        self._font_body = pygame.font.SysFont("consolas", 17)
        self._font_sm   = pygame.font.SysFont("consolas", 13)
        self._font_btn  = pygame.font.SysFont("consolas", 18, bold=True)
        self._font_stat = pygame.font.SysFont("consolas", 22, bold=True)
        self._font_frag = pygame.font.SysFont("consolas", 12)
        self._asurf     = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    def on_enter(self, skip_to_stats: bool = False, **kwargs) -> None:
        self._time    = 0.0
        self._stage_t = 0.0
        self._text    = ""
        self._char_idx = 0.0
        self._skip    = False
        self._btns: list[dict] = []

        avail          = [r for r in ROOMS if r["available"]]
        self._cleared  = [r for r in avail if self.game.save.is_cleared(r["id"])]
        self._n_avail  = len(avail)
        self._score    = sum(self.game.save.get_score(r["id"]) for r in self._cleared)

        self.game.audio.stop_ambient()
        self._stage = 4 if skip_to_stats else 0
        self._init_stage(self._stage)

    def on_exit(self) -> None:
        self.game.audio.start_ambient()

    # ── stage management ─────────────────────────────────────────────────────

    def _init_stage(self, n: int) -> None:
        self._stage    = n
        self._stage_t  = 0.0
        self._skip     = False
        self._char_idx = 0.0
        self._text     = _STORIES.get(n, "")
        if n == 4:
            self._build_buttons()

    def _build_buttons(self) -> None:
        cx    = SCREEN_WIDTH // 2
        y     = 580
        btn_w = 220
        gap   = 20
        bx    = cx - (3 * btn_w + 2 * gap) // 2
        self._btns = [
            {"label": "MEMORY ARCHIVE",     "key": "archive",  "col": ACCENT_CYAN,
             "rect": pygame.Rect(bx,              y, btn_w, 44)},
            {"label": "CONTINUE EXPLORING", "key": "rooms",    "col": ACCENT_GREEN,
             "rect": pygame.Rect(bx + btn_w + gap, y, btn_w, 44)},
            {"label": "PLAY AGAIN",         "key": "new_game", "col": ACCENT_ORANGE,
             "rect": pygame.Rect(bx + 2 * (btn_w + gap), y, btn_w, 44)},
        ]

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            k = event.key
            if self._stage == 0:
                if k in (pygame.K_SPACE, pygame.K_RETURN):
                    self._init_stage(1)
            elif self._stage in (1, 2, 3):
                if k in (pygame.K_SPACE, pygame.K_RETURN):
                    if not self._skip:
                        self._skip = True         # reveal full text first
                    else:
                        self._init_stage(self._stage + 1)
                elif k == pygame.K_ESCAPE:
                    self._init_stage(4)           # skip to stats
            elif self._stage == 4:
                if k == pygame.K_ESCAPE:
                    self.game.audio.play("click")
                    self.game.sm.transition("rooms")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._stage == 4:
                mx, my = event.pos
                for btn in self._btns:
                    if btn["rect"].collidepoint(mx, my):
                        self.game.audio.play("click")
                        if btn["key"] == "new_game":
                            self.game.save.reset()
                            self.game.sm.transition("intro")
                        else:
                            self.game.sm.transition(btn["key"])

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float) -> None:
        self._time    += dt
        self._stage_t += dt
        if self._stage == 0 and self._stage_t >= _STAGE_0_DURATION:
            self._init_stage(1)
        elif self._stage in (1, 2, 3) and not self._skip:
            self._char_idx = min(
                len(self._text), self._char_idx + _CHARS_PER_SEC * dt
            )
            if self._char_idx >= len(self._text):
                self._skip = True

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        if   self._stage == 0:         self._draw_s0(surface)
        elif self._stage in (1, 2, 3): self._draw_story(surface)
        elif self._stage == 4:         self._draw_stats(surface)
        fx.scanlines(surface, alpha=16)

    # ── stage 0: fragment convergence ────────────────────────────────────────

    def _draw_s0(self, surface: pygame.Surface) -> None:
        t  = self._stage_t
        cx, cy = _CX, _CY

        # Concentric cyan pulse rings
        for ri in range(4):
            phase = (t * 0.85 + ri * 0.27) % 1.0
            rr    = int(phase * 380)
            ra    = max(0, int(90 * (1.0 - phase)))
            if rr > 0 and ra > 0:
                self._asurf.fill((0, 0, 0, 0))
                pygame.draw.circle(self._asurf, (48, 242, 242, ra), (cx, cy), rr, 2)
                surface.blit(self._asurf, (0, 0))

        # Fragment chips flying from row → center
        arrive_t = _N * 0.18 + 0.55   # when the last chip reaches center
        for i, room in enumerate(ROOMS):
            ts   = i * 0.18
            te   = ts + 0.55
            frac = 0.0 if t < ts else 1.0 if t >= te else (
                lambda r: r * r * (3.0 - 2.0 * r)
            )((t - ts) / 0.55)

            sx   = _SX0 + i * (_SW + _SGAP) + _SW // 2
            sy   = _SY  + _SH // 2
            px   = int(sx + (cx - sx) * frac)
            py   = int(sy + (cy - sy) * frac)
            half = max(2, int((_SW // 2) * (1.0 - frac * 0.78)))
            col  = ACCENT_GOLD if self.game.save.is_cleared(room["id"]) else TEXT_MUTED
            chip = pygame.Rect(px - half, py - half, half * 2, half * 2)
            pygame.draw.rect(surface, BG_PANEL, chip, border_radius=3)
            pygame.draw.rect(surface, col,      chip, 1, border_radius=3)

        # Expanding gold burst rings after all chips converge
        burst_t = t - (arrive_t + 0.06)
        if burst_t > 0:
            for bi in range(5):
                bti = burst_t - bi * 0.10
                if bti <= 0:
                    continue
                br = int(bti * 530)
                ba = max(0, int(200 * (1.0 - bti * 1.05)))
                if br > 0 and ba > 0:
                    self._asurf.fill((0, 0, 0, 0))
                    pygame.draw.circle(
                        self._asurf, (*ACCENT_GOLD, ba),
                        (cx, cy), br, max(1, 3 - bi),
                    )
                    surface.blit(self._asurf, (0, 0))

            # Central green glow
            ga = min(160, int(burst_t * 280))
            self._asurf.fill((0, 0, 0, 0))
            pygame.draw.circle(self._asurf, (*ACCENT_GREEN, ga), (cx, cy), 30)
            surface.blit(self._asurf, (0, 0))

        # Status label
        if t < arrive_t:
            lbl_text = "FRAGMENTS CONVERGING..."
            lbl_col  = ACCENT_CYAN
        else:
            lbl_text = "MEMORY RESTORATION INITIATED"
            lbl_col  = ACCENT_GREEN
        lbl = self._font_h3.render(lbl_text, True, lbl_col)
        surface.blit(lbl, lbl.get_rect(centerx=cx, y=cy + 145))

        hint = self._font_sm.render("SPACE to skip", True, TEXT_MUTED)
        surface.blit(hint, hint.get_rect(centerx=cx, y=SCREEN_HEIGHT - 28))

    # ── stages 1-3: typewriter story ─────────────────────────────────────────

    _STAGE_META: dict = {
        1: ("MEMORY RETURNING",  ACCENT_CYAN),
        2: ("VIRUS COLLAPSING",  ACCENT_RED),
        3: ("SYSTEM RESTORED",   ACCENT_GREEN),
    }

    def _draw_story(self, surface: pygame.Surface) -> None:
        s          = self._stage
        cx         = SCREEN_WIDTH // 2
        hdr, hcol  = self._STAGE_META[s]

        # Radial colour tint shifting from red (stage 1) → green (stage 3)
        tprog = (s - 1) / 2.0
        self._asurf.fill((0, 0, 0, 0))
        pygame.draw.circle(
            self._asurf,
            (int(210 * (1.0 - tprog)), int(190 * tprog), 0, 18),
            (cx, SCREEN_HEIGHT // 2), SCREEN_WIDTH,
        )
        surface.blit(self._asurf, (0, 0))

        # Header bar
        pygame.draw.rect(surface, BG_MID, (0, 0, SCREEN_WIDTH, 66))
        pygame.draw.line(surface, hcol, (0, 66), (SCREEN_WIDTH, 66), 1)
        surface.blit(
            self._font_h3.render(hdr, True, hcol),
            self._font_h3.render(hdr, True, hcol).get_rect(centerx=cx, y=20),
        )

        # Stage progress dots
        for si in range(1, 4):
            dc = hcol if si <= s else BORDER
            pygame.draw.circle(
                surface, dc, (cx - 30 + (si - 1) * 30, 56),
                4, 0 if si <= s else 1,
            )

        # Text box
        cw   = 700
        bx   = cx - cw // 2
        y    = 84
        lh   = self._font_body.get_height() + 5
        visible = self._text if self._skip else self._text[:int(self._char_idx)]
        lines   = visible.split("\n")

        box_h = 22
        for ln in lines:
            box_h += lh if ln else lh // 2
        box_h = max(220, box_h + 14)

        box_r = pygame.Rect(bx, y, cw, box_h)
        pygame.draw.rect(surface, BG_PANEL, box_r, border_radius=6)
        pygame.draw.rect(surface, hcol,    box_r, 1, border_radius=6)
        pygame.draw.rect(surface, hcol,
                         pygame.Rect(bx, y + 12, 3, box_h - 24), border_radius=2)

        ty = y + 18
        for ln in lines:
            if not ln:
                ty += lh // 2
                continue
            surface.blit(self._font_body.render(ln, True, TEXT_PRIMARY), (bx + 18, ty))
            ty += lh

        if not self._skip and int(self._time * 2) % 2 == 0:
            csr  = self._font_body.render("█", True, hcol)
            last = lines[-1] if lines else ""
            surface.blit(csr, (bx + 18 + self._font_body.size(last)[0] + 2, ty - lh))

        # Fragment flash memories below box (shown once text is revealed)
        if self._skip and self._cleared:
            fy = box_r.bottom + 16
            fh = self._font_sm.render("[ RECOVERED MEMORIES ]", True, TEXT_MUTED)
            surface.blit(fh, fh.get_rect(centerx=cx, y=fy))
            fy += fh.get_height() + 8
            for room in self._cleared[:3]:
                frag = room.get("memory_fragment") or ""
                sent = frag.split(".")[0]
                if sent:
                    trunc = sent[:76] if len(sent) > 76 else sent
                    fs = self._font_frag.render(
                        f"{room['title']}:  \"{trunc}...\"", True, ACCENT_GOLD
                    )
                    surface.blit(fs, fs.get_rect(centerx=cx, y=fy))
                    fy += fs.get_height() + 5

        # Navigation hint
        if self._skip:
            nh = ("SPACE = continue" if s < 3 else
                  "SPACE = view results  |  ESC = skip to results")
        else:
            nh = "SPACE to skip  |  ESC = jump to results"
        surface.blit(
            self._font_sm.render(nh, True, TEXT_MUTED),
            self._font_sm.render(nh, True, TEXT_MUTED).get_rect(
                centerx=cx, y=SCREEN_HEIGHT - 28
            ),
        )

    # ── stage 4: statistics ───────────────────────────────────────────────────

    def _draw_stats(self, surface: pygame.Surface) -> None:
        cx = SCREEN_WIDTH // 2

        # Soft green ambient glow at top
        gr = int(260 + 80 * abs(math.sin(self._time * 1.1)))
        self._asurf.fill((0, 0, 0, 0))
        pygame.draw.circle(self._asurf, (*ACCENT_GREEN, 14), (cx, 0), gr)
        surface.blit(self._asurf, (0, 0))

        # Header bar
        pygame.draw.rect(surface, BG_MID, (0, 0, SCREEN_WIDTH, 78))
        pygame.draw.line(surface, ACCENT_GREEN, (0, 78), (SCREEN_WIDTH, 78), 2)
        h1 = self._font_h1.render("SYSTEM RESTORED", True, ACCENT_GREEN)
        surface.blit(h1, h1.get_rect(centerx=cx, y=10))
        h2 = self._font_sm.render(
            "VIRUS DEFEATED  //  ALL MEMORY FRAGMENTS RECOVERED", True, ACCENT_CYAN
        )
        surface.blit(h2, h2.get_rect(centerx=cx, y=52))

        # ── 2×2 stats grid ────────────────────────────────────────────────────
        nc    = len(self._cleared)
        na    = self._n_avail
        pct   = int(nc / max(1, na) * 100)

        panel_w = 800
        panel   = pygame.Rect(cx - panel_w // 2, 96, panel_w, 280)
        pygame.draw.rect(surface, BG_MID,       panel, border_radius=8)
        pygame.draw.rect(surface, ACCENT_GREEN, panel, 2, border_radius=8)

        grid = [
            ("ROOMS CLEARED",    f"{nc} / {na}",        ACCENT_GREEN),
            ("MEMORY FRAGMENTS", f"{nc} / {na}",        ACCENT_GOLD),
            ("TOTAL SCORE",      f"{self._score} pts",  ACCENT_CYAN),
            ("COMPLETION",       f"{pct}%",             ACCENT_GREEN),
        ]
        cw    = panel_w // 2 - 30
        gap20 = 20
        cells = [
            pygame.Rect(panel.x + gap20,              panel.y + gap20,  cw, 110),
            pygame.Rect(panel.x + panel_w // 2 + 10, panel.y + gap20,  cw, 110),
            pygame.Rect(panel.x + gap20,              panel.y + 150,   cw, 110),
            pygame.Rect(panel.x + panel_w // 2 + 10, panel.y + 150,   cw, 110),
        ]
        for cell, (label, value, vcol) in zip(cells, grid):
            pygame.draw.rect(surface, BG_PANEL, cell, border_radius=5)
            pygame.draw.rect(surface, BORDER,   cell, 1, border_radius=5)
            surface.blit(
                self._font_sm.render(label, True, TEXT_MUTED),
                (cell.x + 14, cell.y + 14),
            )
            vs = self._font_stat.render(value, True, vcol)
            surface.blit(vs, vs.get_rect(centerx=cell.centerx, y=cell.y + 52))

        # ── recovered fragment excerpts ───────────────────────────────────────
        fy = panel.bottom + 22
        fhdr = self._font_sm.render("[ RECOVERED MEMORY FRAGMENTS ]", True, TEXT_MUTED)
        surface.blit(fhdr, fhdr.get_rect(centerx=cx, y=fy))
        fy += fhdr.get_height() + 10

        for room in self._cleared[:3]:
            frag = room.get("memory_fragment") or ""
            if frag:
                title_s = self._font_sm.render(room["title"].upper(), True, ACCENT_GOLD)
                surface.blit(title_s, (cx - 380, fy))
                fy += title_s.get_height() + 3

                sent = frag.split(".")[0]
                if len(sent) > 90:
                    sent = sent[:90].rsplit(" ", 1)[0]
                ex = self._font_frag.render(f"  \"{sent}...\"", True, TEXT_DIM)
                surface.blit(ex, (cx - 380, fy))
                fy += ex.get_height() + 10

        # Fragment tracker dots
        fy += 6
        dot_r     = 5
        dot_space = 20
        dots_w    = (na - 1) * dot_space + dot_r * 2
        dx        = cx - dots_w // 2
        avail_ids = {r["id"] for r in ROOMS if r["available"]}
        for j, room in enumerate(r for r in ROOMS if r["id"] in avail_ids):
            is_c = self.game.save.is_cleared(room["id"])
            pygame.draw.circle(
                surface, ACCENT_GOLD if is_c else BORDER,
                (dx + j * dot_space, fy + dot_r), dot_r, 0 if is_c else 1,
            )

        # ── buttons ───────────────────────────────────────────────────────────
        mx, my = pygame.mouse.get_pos()
        for btn in self._btns:
            hov  = btn["rect"].collidepoint((mx, my))
            col  = btn["col"]
            if hov:
                if col == ACCENT_GREEN:  fill = (0, 22, 18)
                elif col == ACCENT_CYAN: fill = (0, 18, 30)
                else:                    fill = (28, 14, 0)
            else:
                fill = BG_PANEL
            bc  = col if hov else BORDER
            pygame.draw.rect(surface, fill, btn["rect"], border_radius=5)
            pygame.draw.rect(surface, bc,   btn["rect"], 2, border_radius=5)
            txt = self._font_btn.render(btn["label"], True, col if hov else TEXT_DIM)
            surface.blit(txt, txt.get_rect(center=btn["rect"].center))

        esc = self._font_sm.render("ESC = return to rooms", True, TEXT_MUTED)
        surface.blit(esc, esc.get_rect(centerx=cx, y=SCREEN_HEIGHT - 24))
