import pygame
from scenes.base_scene import BaseScene
from core.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ROOMS,
    BG_DARK, BG_MID, BG_PANEL,
    ACCENT_GREEN, ACCENT_CYAN, ACCENT_RED, ACCENT_ORANGE,
    TEXT_PRIMARY, TEXT_DIM, TEXT_MUTED, BORDER,
)

# Tier accent colours indexed by tier number (1-4)
_TIER_COLOR = {1: ACCENT_GREEN, 2: ACCENT_CYAN, 3: ACCENT_ORANGE, 4: ACCENT_RED}

# Card geometry
_CARD_W  = 248
_CARD_H  = 160
_COLS    = 4
_ROWS    = 2
_PAD_X   = (SCREEN_WIDTH  - _COLS * _CARD_W) // (_COLS + 1)
_PAD_Y_TOP = 120
_ROW_GAP = 60
_HEADER_H = 80


class WorldMap(BaseScene):
    def __init__(self, game):
        super().__init__(game)
        self._font_h1   = pygame.font.SysFont("consolas", 30, bold=True)
        self._font_room = pygame.font.SysFont("consolas", 16, bold=True)
        self._font_body = pygame.font.SysFont("consolas", 14)
        self._font_sm   = pygame.font.SysFont("consolas", 12)
        self._nodes: list[dict] = []

    def on_enter(self, **kwargs) -> None:
        self._build_nodes()

    def _build_nodes(self) -> None:
        self._nodes = []
        for i, room in enumerate(ROOMS):
            col = i % _COLS
            row = i // _COLS
            x = _PAD_X + col * (_CARD_W + _PAD_X)
            y = _PAD_Y_TOP + row * (_CARD_H + _ROW_GAP)
            rect = pygame.Rect(x, y, _CARD_W, _CARD_H)
            self._nodes.append({
                "room":    room,
                "rect":    rect,
                "cleared": self.game.save.is_cleared(room["id"]),
                "score":   self.game.save.get_score(room["id"]),
            })

    # ---------------------------------------------------------------- events

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.sm.transition("main_menu")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for node in self._nodes:
                if node["room"]["available"] and node["rect"].collidepoint(event.pos):
                    self.game.sm.transition("room_game", room_id=node["room"]["id"])

    # ---------------------------------------------------------------- update

    def update(self, dt: float) -> None:
        # Refresh cleared/score state each frame so returning from a room reflects instantly.
        for node in self._nodes:
            node["cleared"] = self.game.save.is_cleared(node["room"]["id"])
            node["score"]   = self.game.save.get_score(node["room"]["id"])

    # ---------------------------------------------------------------- draw

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BG_DARK)
        self._draw_header(surface)
        mx, my = pygame.mouse.get_pos()
        for node in self._nodes:
            self._draw_node(surface, node, (mx, my))

    def _draw_header(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, BG_MID, (0, 0, SCREEN_WIDTH, _HEADER_H))
        pygame.draw.line(surface, BORDER, (0, _HEADER_H), (SCREEN_WIDTH, _HEADER_H), 1)

        title = self._font_h1.render("WORLD MAP", True, ACCENT_CYAN)
        surface.blit(title, (30, 22))

        hint = self._font_sm.render(
            "Select a room  |  ESC -> Main Menu", True, TEXT_MUTED
        )
        surface.blit(hint, (SCREEN_WIDTH - hint.get_width() - 30, 32))

    def _draw_node(self, surface: pygame.Surface, node: dict, mouse_pos: tuple) -> None:
        room      = node["room"]
        rect      = node["rect"]
        available = room["available"]
        cleared   = node["cleared"]
        hovered   = available and rect.collidepoint(mouse_pos)
        tier_col  = _TIER_COLOR.get(room["tier"], TEXT_DIM)

        # Background fill
        if cleared:
            fill = (12, 38, 22)
        elif hovered:
            fill = (20, 28, 50)
        else:
            fill = BG_PANEL if available else (11, 13, 22)
        pygame.draw.rect(surface, fill, rect, border_radius=6)

        # Border
        if cleared:
            border_col = ACCENT_GREEN
        elif hovered:
            border_col = ACCENT_CYAN
        elif available:
            border_col = BORDER
        else:
            border_col = (22, 28, 45)
        pygame.draw.rect(surface, border_col, rect, 2, border_radius=6)

        # Tier stripe along the top edge
        stripe = pygame.Rect(rect.x + 2, rect.y + 2, rect.w - 4, 3)
        pygame.draw.rect(surface, tier_col if available else (30, 35, 55), stripe, border_radius=2)

        x0 = rect.x + 14

        # Room number
        num_col = ACCENT_GREEN if cleared else (ACCENT_CYAN if available else TEXT_MUTED)
        num  = self._font_room.render(f"Room {room['number']}", True, num_col)
        surface.blit(num, (x0, rect.y + 16))

        # Title
        t_col = TEXT_PRIMARY if available else TEXT_MUTED
        title = self._font_body.render(room["title"], True, t_col)
        surface.blit(title, (x0, rect.y + 40))

        # Tier badge
        tier  = self._font_sm.render(f"Tier {room['tier']}", True, tier_col if available else TEXT_MUTED)
        surface.blit(tier, (x0, rect.y + 62))

        # Status area
        if cleared:
            score_s = self._font_room.render(f"{node['score']} pts", True, ACCENT_GREEN)
            surface.blit(score_s, (rect.right - score_s.get_width() - 14, rect.y + 16))
            done = self._font_sm.render("CLEARED", True, ACCENT_GREEN)
            surface.blit(done, (rect.right - done.get_width() - 14, rect.y + 40))
        elif not available:
            lock = self._font_sm.render("LOCKED", True, TEXT_MUTED)
            surface.blit(lock, lock.get_rect(center=rect.center))
        elif hovered:
            enter = self._font_sm.render("[ ENTER ]", True, ACCENT_CYAN)
            surface.blit(enter, enter.get_rect(
                centerx=rect.centerx,
                y=rect.bottom - enter.get_height() - 14,
            ))
