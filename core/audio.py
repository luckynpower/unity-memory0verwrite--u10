"""
Programmatic audio — no external files required.
All sounds are generated at startup using basic DSP.
Wraps gracefully if the mixer cannot initialise.
"""
import array
import math
import pygame

_SR = 44100  # sample rate


def _tone(freq: float, duration: float, volume: float = 0.45,
          attack: float = 0.008, release: float = 0.025) -> pygame.mixer.Sound:
    n = int(_SR * duration)
    buf = array.array("h")
    atk = int(_SR * attack)
    rel = int(_SR * release)
    for i in range(n):
        env = min(1.0, i / max(1, atk)) * min(1.0, (n - i) / max(1, rel))
        val = int(32767 * volume * env * math.sin(2 * math.pi * freq * i / _SR))
        val = max(-32767, min(32767, val))
        buf.append(val)
        buf.append(val)   # stereo
    return pygame.mixer.Sound(buffer=buf)


def _chord(freqs: list[float], duration: float,
           volume: float = 0.35) -> pygame.mixer.Sound:
    n = int(_SR * duration)
    buf = array.array("h", [0] * n * 2)
    amp = volume / len(freqs)
    for freq in freqs:
        start_offset = freqs.index(freq) * int(_SR * 0.12)
        for i in range(n):
            j = i + start_offset
            if j >= n:
                break
            rel = min(1.0, (n - j) / max(1, int(_SR * 0.06)))
            val = int(32767 * amp * rel * math.sin(2 * math.pi * freq * i / _SR))
            buf[j * 2]     = max(-32767, min(32767, buf[j * 2]     + val))
            buf[j * 2 + 1] = max(-32767, min(32767, buf[j * 2 + 1] + val))
    return pygame.mixer.Sound(buffer=buf)


def _ambient(duration: float = 4.0, volume: float = 0.22) -> pygame.mixer.Sound:
    """Low drone with slow tremolo — loops seamlessly."""
    n = int(_SR * duration)
    buf = array.array("h")
    for i in range(n):
        t = i / _SR
        # Fade in/out for seamless looping
        loop_env = min(1.0, i / (_SR * 0.3)) * min(1.0, (n - i) / (_SR * 0.3))
        tremolo  = 0.65 + 0.35 * math.sin(2 * math.pi * 0.4 * t)
        wave = (
            0.50 * math.sin(2 * math.pi * 55  * t) +
            0.25 * math.sin(2 * math.pi * 110 * t) +
            0.12 * math.sin(2 * math.pi * 165 * t) +
            0.08 * math.sin(2 * math.pi * 82.5 * t + math.pi * 0.3)
        ) * tremolo * loop_env
        val = int(32767 * volume * wave)
        val = max(-32767, min(32767, val))
        buf.append(val)
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)


def _fragment_fanfare() -> pygame.mixer.Sound:
    """Rising sweep used on the room-result screen."""
    duration = 1.2
    n = int(_SR * duration)
    buf = array.array("h")
    for i in range(n):
        t  = i / _SR
        progress = t / duration
        freq = 220 + 660 * (progress ** 1.5)   # accelerating rise
        env  = min(1.0, i / (_SR * 0.04)) * min(1.0, (n - i) / (_SR * 0.15))
        val  = int(32767 * 0.38 * env * math.sin(2 * math.pi * freq * t))
        val  = max(-32767, min(32767, val))
        buf.append(val)
        buf.append(val)
    return pygame.mixer.Sound(buffer=buf)


class AudioManager:
    """Single instance owned by Game.  Access via game.audio.play(name)."""

    def __init__(self):
        self._ok      = False
        self._sounds: dict[str, pygame.mixer.Sound] = {}
        self._ambient_sound: pygame.mixer.Sound | None = None
        self._muted   = False

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=_SR, size=-16, channels=2, buffer=512)
            self._sounds = {
                "click":    _tone(820,  0.07, volume=0.40),
                "hover":    _tone(620,  0.04, volume=0.18),
                "error":    _tone(180,  0.22, volume=0.32),
                "type":     _tone(1100, 0.028, volume=0.12),
                "success":  _chord([523, 659, 784], 0.55, volume=0.38),
                "fragment": _fragment_fanfare(),
            }
            self._ambient_sound = _ambient()
            self._ok = True
        except Exception:
            pass   # audio unavailable — game continues without it

    # ── public API ────────────────────────────────────────────────────────────

    def play(self, name: str) -> None:
        if not self._ok or self._muted:
            return
        s = self._sounds.get(name)
        if s:
            s.play()

    def start_ambient(self) -> None:
        if not self._ok or self._muted or not self._ambient_sound:
            return
        self._ambient_sound.play(loops=-1, fade_ms=1500)

    def stop_ambient(self) -> None:
        if self._ambient_sound:
            self._ambient_sound.fadeout(800)

    def toggle_mute(self) -> bool:
        self._muted = not self._muted
        if self._muted:
            pygame.mixer.pause()
        else:
            pygame.mixer.unpause()
        return self._muted
