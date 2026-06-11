import json
import os
from core.settings import SAVE_PATH


class SaveManager:
    def __init__(self):
        self._path = SAVE_PATH
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"cleared_rooms": {}, "artefacts": {}}

    def save(self) -> None:
        try:
            with open(self._path, "w") as f:
                json.dump(self._data, f, indent=2)
        except IOError:
            pass

    def mark_cleared(self, room_id: str, score: int) -> None:
        prev = self._data["cleared_rooms"].get(room_id, 0)
        self._data["cleared_rooms"][room_id] = max(prev, score)
        self.save()

    def is_cleared(self, room_id: str) -> bool:
        return room_id in self._data["cleared_rooms"]

    def get_score(self, room_id: str) -> int:
        return self._data["cleared_rooms"].get(room_id, 0)

    # Cross-room artefacts (e.g. pet name discovered in Room 2 -> usable in Room 3)
    def set_artefact(self, key: str, value) -> None:
        self._data["artefacts"][key] = value
        self.save()

    def get_artefact(self, key: str):
        return self._data["artefacts"].get(key)

    def reset(self) -> None:
        self._data = {"cleared_rooms": {}, "artefacts": {}}
        self.save()
