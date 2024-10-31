from typing import Tuple

import numpy as np

# Структурированный тип плиточной графики, совместимый с Console.tiles_rgb.
graphic_dt = np.dtype(
    [
        ("ch", np.int32),  # кодовая позиция Unicode
        ("fg", "3B"),  # 3 беззнаковых байта для цветов RGB.
        ("bg", "3B"),
    ]
)

# Структура плитки, используемая для статически определенных данных плитки.
tile_dt = np.dtype(
    [
        ("walkable", bool),  # Истина, если по этой плитке можно ходить.
        ("transparent", bool),  # True, если эта плитка не блокирует поле зрения.
        ("dark", graphic_dt),  # Графика для случая, когда эта плитка не находится в поле зрения.
        ("light", graphic_dt),  # Графика для случая, когда плитка находится в поле зрения.
    ]
)


def new_tile(
    *,  # Обязательно используйте ключевые слова, чтобы порядок параметров не имел значения.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Вспомогательная функция для определения отдельных типов плитки"""
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


# SHROUD представляет собой неисследованные, невидимые плитки
SHROUD = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=graphic_dt)

floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("."), (100, 100, 100), (0, 0, 0)),
    light=(ord("."), (200, 200, 200), (0, 0, 0)),
)
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=(ord("0"), (100, 100, 100), (0, 0, 0)),
    light=(ord("0"), (200, 200, 200), (0, 0, 0)),
)
down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord(">"), (100, 100, 100), (0, 0, 0)),
    light=(ord(">"), (200, 200, 200), (0, 0, 0)),
)
