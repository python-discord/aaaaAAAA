from enum import IntEnum
from random import choice
from typing import Optional

import arcade
from arcade_curtains import BaseScene, Curtains

from aaaaAAAA import _sprites, constants


class Colour(IntEnum):
    """Enums for use as sprite colours."""

    Green = 0
    Yellow = 1
    Purple = 2
    Black = 3


class DuckScene(BaseScene):
    """Scene showing Ducks moving down the river to the pondhouse."""

    def __init__(self, debug: Optional[bool] = False):
        self.debug = debug
        super().__init__()

    def setup(self) -> None:
        """Setup the scene assets."""
        self.background = arcade.load_texture("assets/overworld/overworld_healthy_no_lilies.png")
        self.pondhouse = arcade.Sprite("assets/overworld/pondhouse/pondhouse_cropped.png", hit_box_algorithm="None")
        self.pondhouse.position = (constants.SCREEN_WIDTH * .67, constants.SCREEN_HEIGHT * .78)
        self.lilies = _sprites.Lily.lilies
        self.ducks = arcade.SpriteList()
        self.pond_ducks = arcade.SpriteList()
        self.pondhouse_ducks = arcade.SpriteList()
        self.leader = _sprites.Ducky(0.075)
        self.ducks.append(self.leader)
        self.seq = self.leader.path_seq
        for x, y in constants.FOLIAGE_POND:
            pos = constants.SCREEN_WIDTH * x, constants.SCREEN_HEIGHT * y
            lily = _sprites.Lily(scale=.075, position=pos)
            self.events.hover(lily, lily.float_about)

    def add_a_ducky(self, dt: Optional[float] = None) -> None:
        """Add a ducky to the scene, register some events and start animating."""
        if not constants.POINTS_HINT:
            return
        ducky = _sprites.Ducky(0.05)
        self.events.hover(ducky, ducky.expand)
        self.events.out(ducky, ducky.shrink)
        self.ducks.append(ducky)
        seq = ducky.path_seq
        seq.add_callback(seq.total_time, lambda: self.enter_pondhouse(ducky))
        self.animations.fire(ducky, seq)
        if len(self.ducks) >= constants.DUCKS:
            arcade.unschedule(self.add_a_ducky)

    def enter_scene(self, previous_scene: BaseScene) -> None:
        """Start adding duckies on entering the scene."""
        if not self.debug:
            self.animations.fire(self.leader, self.seq)
            arcade.schedule(self.add_a_ducky, len(constants.POINTS_HINT)*10/constants.DUCKS)

    def draw(self) -> None:
        """Draw the background environment."""
        if len(self.pondhouse_ducks) >= 20:
            self.background = arcade.load_texture("assets/overworld/overworld_deadly_no_lilies.png")
            for lily in self.lilies:
                lily.change_texture(Colour.Black)
            for duck in self.pond_ducks:
                self.animations.kill(duck)
                duck.deceased()
        elif len(self.pondhouse_ducks) > 15:
            for lily in self.lilies:
                lily.change_texture(Colour.Purple)
            self.background = arcade.load_texture("assets/overworld/overworld_toxic_no_lilies.png")
        elif len(self.pondhouse_ducks) > 10:
            self.background = arcade.load_texture("assets/overworld/overworld_disgusting_no_lilies.png")
        elif len(self.pondhouse_ducks) > 5:
            for lily in self.lilies:
                lily.change_texture(Colour.Yellow)
            self.background = arcade.load_texture("assets/overworld/overworld_decaying_no_lilies.png")
        else:
            for lily in self.lilies:
                lily.change_texture(Colour.Green)
            self.background = arcade.load_texture("assets/overworld/overworld_healthy_no_lilies.png")
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(
            0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, self.background
        )
        super().draw()
        self.pondhouse.draw()

    def enter_pondhouse(self, ducky: _sprites.Ducky) -> None:
        """Duckies that are circling outside the pondhouse waiting to be processed."""
        self.ducks.remove(ducky)
        self.pondhouse_ducks.append(ducky)
        self.animations.fire(ducky, ducky.pondhouse_seq)

    def grant_entry(self, ducky: Optional[_sprites.Ducky] = None) -> None:
        """Generic method to grant entry. - gateway to the pond."""
        if self.pondhouse_ducks:
            duck = ducky or choice(self.pondhouse_ducks)
            self.pondhouse_ducks.remove(duck)
            if len(self.pond_ducks) >= constants.POND:
                ducky_out = choice(self.pond_ducks.sprite_list)
                seq = ducky_out.off_screen()
                seq.add_callback(seq.total_time, lambda: self.pond_ducks.remove(ducky_out))
                self.animations.fire(ducky_out, seq)
            self.pond_ducks.append(duck)
            self.enter_pond(duck)

    def enter_pond(self, duck: _sprites.Ducky) -> None:
        """Grant a ducky entry into the pond."""
        self.animations.fire(duck, duck.pond_seq)


class GameView(arcade.View):
    """Main application class."""

    def __init__(self, debug: Optional[bool] = False):
        super().__init__()
        self.debug = debug
        if self.debug:
            constants.POINTS_HINT.clear()
        self.curtains = Curtains(self)
        self.curtains.add_scene('swimming_scene', DuckScene(self.debug))
        self.curtains.set_scene('swimming_scene')
        arcade.set_background_color(arcade.color.WARM_BLACK)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """
        For use only when debug=True.

        'a' to add a duck
        'p' to print the generated points_hint list
        'x' to clear the points
        'g' grant random duck entry
        """
        if not self.debug:
            pass  # temporarily remove this block
        if symbol == ord('a'):
            if self.curtains.current_scene == self.curtains.scenes['swimming_scene']:
                self.curtains.current_scene.add_a_ducky()
        elif symbol == ord('p'):
            print(constants.POINTS_HINT)
        elif symbol == ord('x'):
            constants.POINTS_HINT.clear()
        elif symbol == ord('g'):
            if self.curtains.current_scene == self.curtains.scenes['swimming_scene']:
                self.curtains.current_scene.grant_entry()

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        """Add clicked point to points_hint as % of width/height."""
        if self.debug:
            constants.POINTS_HINT.append((round(x/self.window.width, 3), round(y/self.window.height, 3)))


def main() -> None:
    """
    Main function.

    Can be run for a GameView in debug mode
    """
    window = arcade.Window(title=constants.SCREEN_TITLE, width=constants.SCREEN_WIDTH, height=constants.SCREEN_HEIGHT)
    arcade.set_window(window)
    game = GameView()
    window.show_view(game)
    arcade.run()


if __name__ == '__main__':
    main()
