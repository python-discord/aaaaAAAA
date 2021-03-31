import random
from typing import Optional

import arcade

from aaaaAAAA import _sprites, constants


class MyGame(arcade.Window):
    """The game we are making."""

    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)
        self.height = height
        self.width = width
        self.ducky_list = arcade.SpriteList()
        arcade.set_background_color(arcade.color.WARM_BLACK)

    def setup(self) -> None:
        """Set up the game variables. Call to re-start the game."""
        self.background = arcade.load_texture("assets/main.png")
        self.points = [(0, 401), (21, 434), (42, 469), (63, 505), (94, 541), (140, 531), (185, 512), (212, 522),
                       (230, 549), (248, 533), (259, 498), (278, 449), (304, 414), (318, 397), (330, 429), (320, 414),
                       (351, 476), (374, 523), (389, 511), (418, 486), (444, 459), (473, 430), (521, 440), (538, 472),
                       (583, 472), (660, 487), (618, 438), (658, 437), (700, 398), (745, 482), (678, 453), (770, 395)]

        arcade.schedule(self.add_a_ducky, 3)

    def on_draw(self) -> None:
        """When a thing is drawn."""
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(
            0, 0, self.width, self.height, self.background
        )
        self.ducky_list.update()
        self.ducky_list.draw()

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """When buttons are pressed."""
        if symbol == 97:
            self.add_a_ducky()
        elif symbol == 112:
            print(self.points)

    def add_a_ducky(self, dt: Optional[float] = None) -> None:
        """Adding a ducky."""
        if not self.points:
            return
        ducky = _sprites.Ducky(random.choice(constants.DUCKY_LIST), 0.05, points=self.points)
        ducky.position = self.points[0]
        self.ducky_list.append(ducky)
        if len(self.ducky_list) >= 25:
            arcade.unschedule(self.add_a_ducky)


def main() -> None:
    """Main method."""
    game = MyGame(
        constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, constants.SCREEN_TITLE
    )
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
