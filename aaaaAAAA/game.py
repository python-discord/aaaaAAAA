from random import choice, randint
from typing import Optional

from aaaaAAAA import _sprites, constants

import arcade
from arcade_curtains import BaseScene, KeyFrame, Sequence, Curtains


POINTS_HINT = [(0.0025, 0.665), (0.0575, 0.7883), (0.08375, 0.8467), (0.11875, 0.905),
               (0.18, 0.8767), (0.245, 0.845), (0.2725, 0.89), (0.29125, 0.9133),
               (0.29125, 0.9133), (0.33, 0.815), (0.33, 0.815), (0.3825, 0.69167),
               (0.4, 0.67167), (0.4175, 0.73167), (0.4175, 0.73167),
               (0.47, 0.87167), (0.5225, 0.8133), (0.5225, 0.8133),
               (0.59, 0.71167), (0.59, 0.71167), (0.60625, 0.72167)]


DUCKS = 36


class DuckScene(BaseScene):
    def __init__(self, debug=False):
        self.debug = debug
        super().__init__()

    def setup(self):
        self.background = arcade.load_texture("assets/main.png")
        self.ducks = arcade.SpriteList()
        self.leader = _sprites.Ducky(choice(constants.DUCKY_LIST), 0.075)
        self.ducks.append(self.leader)
        self.seq = self.sequence_gen()

    def add_a_ducky(self, dt: Optional[float] = None) -> None:
        """Add a ducky to the scene, register some events, start animating"""
        if not POINTS_HINT:
            return
        ducky = _sprites.Ducky(choice(constants.DUCKY_LIST), 0.05)
        self.events.hover(ducky, ducky.expand)
        self.events.out(ducky, ducky.shrink)
        self.ducks.append(ducky)
        seq = self.sequence_gen(random=True)
        self.animations.fire(ducky, seq)
        if len(self.ducks) >= DUCKS:
            arcade.unschedule(self.add_a_ducky)

    def enter_scene(self, previous_scene) -> None:
        if not self.debug:
            self.animations.fire(self.leader, self.seq)
            arcade.schedule(self.add_a_ducky, 3)

    def draw(self):
        """When a duck is drawn."""
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(
            0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, self.background
        )
        self.ducks.draw()

    @staticmethod
    def sequence_gen(random: Optional[bool] = False) -> Sequence:
        """Generate a Sequence for the ducky to follow"""
        seq = Sequence()
        current = 0
        for index, ((x1, y1), (x2, y2)) in enumerate(zip(POINTS_HINT[:-1], POINTS_HINT[1:])):
            p1 = x1 * constants.SCREEN_WIDTH, y1 * constants.SCREEN_HEIGHT
            p2 = x2 * constants.SCREEN_WIDTH, y2 * constants.SCREEN_HEIGHT
            frames = 1
            if random:
                frames = randint(1, 5)
            seq.add_keyframes((current, KeyFrame(position=p1)), (current+frames, KeyFrame(position=p2)))
            current += frames
        return seq


class GameView(arcade.View):
    def __init__(self, debug=False):
        super().__init__()
        self.debug = debug
        if self.debug:
            POINTS_HINT.clear()
        self.curtains = Curtains(self)
        self.curtains.add_scene('swimming_scene', DuckScene(self.debug))
        self.curtains.set_scene('swimming_scene')
        arcade.set_background_color(arcade.color.WARM_BLACK)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """
        'a' to add a duck
        'p' to print the generated points_hint list
        'x' to clear the points
        """
        if not self.debug:
            return
        if symbol == ord('a'):
            if self.curtains.current_scene == self.curtains.scenes['swimming_scene']:
                self.curtains.current_scene.add_a_ducky()
        elif symbol == ord('p'):
            print(POINTS_HINT)
        elif symbol == ord('x'):
            POINTS_HINT.clear()

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        """Add clicked point to points_hint as % of width/height"""
        POINTS_HINT.append((x/self.window.width, y/self.window.height))


def main():
    window = arcade.Window()
    arcade.set_window(window)
    game = GameView(debug=True)
    window.show_view(game)
    arcade.run()


if __name__ == '__main__':
    main()
