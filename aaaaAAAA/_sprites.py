from random import random

import arcade

DUCKY_SPEED = 240
ducky_list = []


class Ducky(arcade.Sprite):
    """Ducky sprite."""

    def __init__(
        self, ducky_name: str, scale: float = 1, points: list = None, *args, **kwargs
    ):
        self.image_file_name = f"assets/{ducky_name}.png"
        self.path = points[:]
        self.end = self.path.pop(0)
        super().__init__(
            self.image_file_name, scale, hit_box_algorithm="None", *args, **kwargs
        )
        arcade.schedule(self.swim, max(3, random() * 4))

    def update(self) -> None:
        """Update the position of the ducky."""
        self.center_x, self.center_y = self.end

    def swim(self, dt: float) -> None:
        """Have the duckies swim to their final path."""
        self.finish = self.path.pop(0)
        if not self.path:
            ducky_list.remove(self)
            arcade.unschedule(self.swim)
        else:
            self.progress = 0
            self.pp = lambda _: self.partial_position(
                self.finish, dt / DUCKY_SPEED * self.progress
            )
            arcade.schedule(self.pp, dt / DUCKY_SPEED)

    def partial_position(self, finish: tuple[float, float], dt: float) -> None:
        """Non-full position."""
        end_x, end_y = finish
        start_x, start_y = self.position
        self.end = start_x + ((end_x - start_x) * dt), start_y + (
            (end_y - start_y) * dt
        )
        self.progress += 0.05
        if self.progress == 1:
            arcade.unschedule(self.pp)
