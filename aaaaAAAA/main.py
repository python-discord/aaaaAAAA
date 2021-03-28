import random

import arcade

from aaaaAAAA import _sprites, constants


class MyGame(arcade.Window):
    """
    Main application class.

    NOTE: Go ahead and delete the methods you don't need.
    If you do need a method, delete the 'pass' and replace it
    with your own code. Don't leave 'pass' in this program.
    """

    def __init__(self, width: int, height: int, title: str):
        super().__init__(width, height, title)

        self.height = height
        self.width = width

        self.ducky_list = arcade.SpriteList()

        # List of ducks we are draggingw with the mouse
        self.held_ducks = None

        # Original location of ducks we are dragging in case they need to go back.
        self.held_ducks_original_pos = None

        arcade.set_background_color(arcade.color.WARM_BLACK)

    def setup(self) -> None:
        """Set up the game variables. Call to re-start the game."""
        self.background = arcade.load_texture("img/aaaaAAAA.png")

        self.held_ducks = []
        self.held_ducks_original_pos = []
        for _ in range(10):
            ducky = _sprites.Ducky(random.choice(constants.DUCKY_LIST), 0.25)

            ducky.position = random.randrange(self.width), random.randrange(self.height)

            self.ducky_list.append(ducky)

    def on_draw(self) -> None:
        """Render the screen."""
        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        arcade.draw_lrwh_rectangle_textured(
            0, 0, self.width, self.height, self.background
        )

        self.ducky_list.draw()

    def on_mouse_motion(self, x: float, y: float, delta_x: float, delta_y: float) -> None:
        """Called whenever the mouse moves."""
        for duck in self.held_ducks:
            duck.center_x += delta_x
            duck.center_y += delta_y

    def on_mouse_press(self, x: float, y: float, button: int, key_modifiers: int) -> None:
        """Called when the user presses a mouse button."""
        # Get all the ducks user has clicked on
        ducks = arcade.get_sprites_at_point((x, y), self.ducky_list)

        # Are there any clicked?
        if len(ducks) > 0:

            # Get the top one
            primary_duck = ducks[-1]

            self.held_ducks = [primary_duck]
            self.held_ducks_original_pos = [self.held_ducks[0].position]
            self.pull_to_top(self.held_ducks[0])

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        """Called when a user releases a mouse button."""
        # If we don't have any held ducks, who cares
        if len(self.held_ducks) == 0:
            return

        # We are no longer holding cards
        self.held_ducks = []

    def pull_to_top(self, duck: arcade.Sprite) -> None:
        """Pull duck to top of rendering order (last to render, looks on-top)."""
        # Find the index of the duck
        index = self.ducky_list.index(duck)
        # Loop and pull all the other cards down towards the zero end
        for i in range(index, len(self.ducky_list) - 1):
            self.ducky_list[i] = self.ducky_list[i + 1]
        # Put this card at the right-side/top/size of list
        self.ducky_list[len(self.ducky_list) - 1] = duck


def main() -> None:
    """Main method."""
    game = MyGame(
        constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, constants.SCREEN_TITLE
    )
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
