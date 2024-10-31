from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple
import random

import numpy as np
import tcod

from actions import Action, BumpAction, MeleeAction, MovementAction, WaitAction

if TYPE_CHECKING:
    from entity import Actor


class BaseAI(Action):
    def perform(self) -> None:
        raise NotImplementedError()

    def get_path_to(self, dest_x: int, dest_y: int) -> List[Tuple[int, int]]:
        """Вычислить и вернуть путь к целевой позиции.

Если допустимого пути нет, то возвращается пустой список.
        """
        # Скопируйте проходимый массив.
        cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)

        for entity in self.entity.gamemap.entities:
            # Проверьте, что сущность блокирует движение и стоимость не равна нулю (блокировка).
            if entity.blocks_movement and cost[entity.x, entity.y]:
                # Добавьте к стоимости заблокированной позиции.
                # Меньшее число означает, что больше врагов будут толпиться друг за другом в
                # коридорах. Большее число означает, что враги будут выбирать более длинные пути,
                # чтобы окружить игрока.
                cost[entity.x, entity.y] += 10

        # Создайте график из массива затрат и передайте этот график новому поисковику.
        graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
        pathfinder = tcod.path.Pathfinder(graph)

        pathfinder.add_root((self.entity.x, self.entity.y))  # Стартовая позиция

        # Вычислить путь до пункта назначения и удалить начальную точку.
        path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

        # Преобразовать из List[List[int]] в List[Tuple[int, int]].
        return [(index[0], index[1]) for index in path]


class HostileEnemy(BaseAI):
    def __init__(self, entity: Actor):
        super().__init__(entity)
        self.path: List[Tuple[int, int]] = []

    def perform(self) -> None:
        target = self.engine.player
        dx = target.x - self.entity.x
        dy = target.y - self.entity.y
        distance = max(abs(dx), abs(dy))  # Расстояние Чебышева (вычисление расстояния как максимума абсолютного значения разности между элементами.)

        if self.engine.game_map.visible[self.entity.x, self.entity.y]:
            if distance <= 1:
                return MeleeAction(self.entity, dx, dy).perform()

            self.path = self.get_path_to(target.x, target.y)

        if self.path:
            dest_x, dest_y = self.path.pop(0)
            return MovementAction(
                self.entity,
                dest_x - self.entity.x,
                dest_y - self.entity.y,
            ).perform()

        return WaitAction(self.entity).perform()


class ConfusedEnemy(BaseAI):
    """
    Растерянный враг будет бесцельно спотыкаться в течение определенного количества ходов, а затем вернется к своему предыдущему ИИ.
Если актер занимает клетку, в которую он случайно перемещается, он будет атаковать.
    """

    def __init__(self, entity: Actor, previous_ai: Optional[BaseAI], turns_remaining: int):
        super().__init__(entity)

        self.previous_ai = previous_ai
        self.turns_remaining = turns_remaining

    def perform(self) -> None:
        # Вернет ИИ в исходное состояние, если эффект исчерпал себя.
        if self.turns_remaining <= 0:
            self.engine.message_log.add_message(f"The {self.entity.name} is no longer confused.")
            self.entity.ai = self.previous_ai
        else:
            # Выберает случайное направление
            direction_x, direction_y = random.choice(
                [
                    (-1, -1),  # Северо-запад
                    (0, -1),  # Север
                    (1, -1),  # Северо-восток
                    (-1, 0),  # Запад
                    (1, 0),  # Восток
                    (-1, 1),  # Юго-запад
                    (0, 1),  # Юг
                    (1, 1),  # Юго-восток
                ]
            )

            self.turns_remaining -= 1

            # Actor попытается двигаться или атаковать в выбранном случайном направлении.
            # Возможно, Actor просто врежется в стену, теряя ход.
            return BumpAction(
                self.entity,
                direction_x,
                direction_y,
            ).perform()
