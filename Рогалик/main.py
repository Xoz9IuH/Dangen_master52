#!/usr/bin/env python3
import traceback
from pygame import mixer
import tcod

import color
import exceptions
import input_handlers
import setup_game

def initialize_music():
    """Инициализация и воспроизведение фоновой музыки."""
    mixer.init()  # Инициализация микшера pygame
    mixer.music.load('Play.mp3') 
    mixer.music.set_volume(0.5)  # громкость (от 0.0 до 1.0)
    mixer.music.play(-1)  # Воспроизведение музыки в бесконечном цикле

def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
    """Если текущий обработчик событий имеет активный движок, сохраните его."""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(filename)
        print("Game saved.")


def main() -> None:
    screen_width = 80
    screen_height = 50

    tileset = tcod.tileset.load_tilesheet("data/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD)

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

    # Инициализация музыки
    initialize_music()

    with tcod.context.new(
        columns=screen_width,
        rows=screen_height,
        tileset=tileset,
        title="Dungeon Master",
        vsync=True,
    ) as context:
        root_console = tcod.Console(screen_width, screen_height, order="F")
        try:
            while True:
                root_console.clear()
                handler.on_render(console=root_console)
                context.present(root_console)

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_events(event)
                except Exception:
                    traceback.print_exc()
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(traceback.format_exc(), color.error)
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:
            pass  # Обработка выхода из игры

if __name__ == '__main__':
    main()