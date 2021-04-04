import arcade

from aaaaAAAA import constants, menu


def main() -> None:
    """Main method."""
    window = arcade.Window(title=constants.SCREEN_TITLE, width=constants.SCREEN_WIDTH, height=constants.SCREEN_HEIGHT)
    window.show_view(menu.MenuView())
    arcade.run()


if __name__ == "__main__":
    main()
