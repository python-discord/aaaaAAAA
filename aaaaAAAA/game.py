from random import choice, randint, shuffle
from typing import Optional

import arcade
from arcade_curtains import BaseScene, Chain, Curtains, KeyFrame, Sequence

from aaaaAAAA import _sprites, constants


class DuckScene(BaseScene):
    """Scene showing Ducks moving down the river to the pondhouse."""

    def __init__(self, debug: Optional[bool] = False):
        self.debug = debug
        super().__init__()

    def setup(self) -> None:
        """Setup the scene assets."""
        self.background = arcade.load_texture("assets/overworld/overworld placeholder.png")
        self.pond = arcade.load_texture("assets/overworld/ponds/png/Blue pond.png")
        self.pondhouse = arcade.load_texture("assets/overworld/pondhouse.png")
        self.ducks = arcade.SpriteList()
        self.pondhouse_ducks = []
        self.leader = _sprites.Ducky(choice(constants.DUCKY_LIST), 0.075)
        self.ducks.append(self.leader)
        self.seq = self.sequence_gen()
        self.pond_seq = self.sequence_gen(random=True, loop=True, pond=True)
        self.pondhouse_seq = self.sequence_gen(random=True, loop=True)

    def add_a_ducky(self, dt: Optional[float] = None) -> None:
        """Add a ducky to the scene, register some events and start animating."""
        if not constants.POINTS_HINT:
            return
        ducky = _sprites.Ducky(choice(constants.DUCKY_LIST), 0.05)
        self.events.hover(ducky, ducky.expand)
        self.events.out(ducky, ducky.shrink)
        self.ducks.append(ducky)
        seq = self.sequence_gen(random=True)
        seq.add_callback(seq.total_time, lambda: self.enter_pondhouse(ducky))
        chain = Chain()
        chain.add_sequences(
            (ducky, seq),
            (ducky, self.pondhouse_seq)
        )
        self.animations.fire(None, chain)
        if len(self.ducks) >= constants.DUCKS:
            arcade.unschedule(self.add_a_ducky)

    def enter_scene(self, previous_scene: BaseScene) -> None:
        """Start adding duckies on entering the scene."""
        if not self.debug:
            self.animations.fire(self.leader, self.seq)
            arcade.schedule(self.add_a_ducky, len(constants.POINTS_HINT)*10/constants.DUCKS)

    def draw(self) -> None:
        """Draw the background environment."""
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(
            0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, self.background
        )
        arcade.draw_scaled_texture_rectangle(constants.SCREEN_WIDTH/2,
                                             constants.SCREEN_HEIGHT * .8,
                                             self.pond,
                                             constants.SCREEN_WIDTH/self.pond.image.width)
        super().draw()
        arcade.draw_scaled_texture_rectangle(constants.SCREEN_WIDTH * .67,
                                             constants.SCREEN_HEIGHT * .78,
                                             self.pondhouse)

    @staticmethod
    def sequence_gen(random: Optional[bool] = False,
                     loop: Optional[bool] = False,
                     pond: Optional[bool] = False) -> Sequence:
        """Generate a Sequence for the ducky to follow."""
        seq = Sequence(loop=loop)
        current = 0
        points = constants.POINTS_HINT
        if pond:
            points = constants.POND_HINT
            if random:
                shuffle(points)
        elif loop:
            points = constants.PONDHOUSE_HINT
        for ((x1, y1), (x2, y2)) in zip(points[:-1], points[1:]):
            p1 = x1 * constants.SCREEN_WIDTH, y1 * constants.SCREEN_HEIGHT
            p2 = x2 * constants.SCREEN_WIDTH, y2 * constants.SCREEN_HEIGHT
            frames = 1
            if random:
                frames = randint(1, 5)
            seq.add_keyframes((current, KeyFrame(position=p1)), (current+frames, KeyFrame(position=p2)))
            current += frames
        return seq

    def enter_pondhouse(self, ducky: _sprites.Ducky) -> None:
        """Duckies that are circling outside the pondhouse waiting to be processed."""
        self.pondhouse_ducks.append(ducky)
        print(self.pondhouse_ducks)

    def enter_pond(self, ducky: Optional[_sprites.Ducky] = None) -> None:
        """Grant a ducky entry into the pond."""
        if self.pondhouse_ducks:
            duck = ducky or choice(self.pondhouse_ducks)
            self.pondhouse_ducks.remove(duck)
            self.animations.fire(duck, self.pond_seq)

    def grant_entry(self) -> None:
        """Generic method to grant entry."""
        self.enter_pond()


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
            return
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
        constants.POINTS_HINT.append((round(x/self.window.width, 3), round(y/self.window.height, 3)))


def main() -> None:
    """
    Main function.

    Can be run for a GameView in debug mode
    """
    window = arcade.Window(title=constants.SCREEN_TITLE, width=constants.SCREEN_WIDTH, height=constants.SCREEN_HEIGHT)
    arcade.set_window(window)
    game = GameView(debug=True)
    window.show_view(game)
    arcade.run()


if __name__ == '__main__':
    main()
