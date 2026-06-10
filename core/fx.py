"""
Shared visual effects for the corrupted-memories aesthetic.
All surfaces are pre-rendered and cached on first use — zero allocation overhead at 60 FPS.
"""
import pygame

_cache: dict = {}


def scanlines(surface: pygame.Surface, alpha: int = 26) -> None:
    """Overlay subtle horizontal scanlines for a CRT phosphor look."""
    w, h = surface.get_size()
    key = (w, h, alpha, "scan")
    if key not in _cache:
        scan = pygame.Surface((w, h), pygame.SRCALPHA)
        for y in range(0, h, 3):
            pygame.draw.line(scan, (0, 0, 0, alpha), (0, y), (w, y))
        _cache[key] = scan
    surface.blit(_cache[key], (0, 0))


def vignette(surface: pygame.Surface, strength: int = 110) -> None:
    """Dark radial vignette — edges darker, centre untouched."""
    w, h = surface.get_size()
    key = (w, h, strength, "vig")
    if key not in _cache:
        v = pygame.Surface((w, h), pygame.SRCALPHA)
        # Dark base over the whole surface
        v.fill((0, 0, 0, strength // 4))
        # Punch a transparent ellipse in the centre
        cx, cy = w // 7, h // 7
        pygame.draw.ellipse(v, (0, 0, 0, 0),
                             pygame.Rect(cx, cy, w - cx * 2, h - cy * 2))
        _cache[key] = v
    surface.blit(_cache[key], (0, 0))


def clear_cache() -> None:
    """Free all cached surfaces (call on resolution change)."""
    _cache.clear()
