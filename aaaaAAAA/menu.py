from typing import Optional

import arcade
from arcade.gui import UIGhostFlatButton, UIManager
from arcade.gui.ui_style import UIStyle
from arcade_curtains import BaseScene, Curtains

from aaaaAAAA import constants
from aaaaAAAA.game import DuckScene


# Classes
class MenuUIManager(UIManager):
    """A custom UI manager to play a hover sound when an element is hovered."""

    hover_sound = arcade.load_sound("assets/audio/fx/plop_1.mp3")

    def __init__(self, window: Optional[arcade.Window] = None, attach_callbacks: bool = True, **kwargs):
        super().__init__(window, attach_callbacks, **kwargs)
        self.already_hovered = False

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> None:
        """Play a hover sound is an element is newly hovered."""
        super().on_mouse_motion(x, y, dx, dy)

        if self.hovered_element and not self.already_hovered:
            self.already_hovered = True
            arcade.play_sound(self.hover_sound)
        elif self.already_hovered and not self.hovered_element:
            self.already_hovered = False


class MenuButton(UIGhostFlatButton):
    """Generic menu button. Applies the desired style and enlargement on hovering."""

    UNHOVER_WIDTH = 300
    UNHOVER_HEIGHT = 60
    HOVER_WIDTH = 310
    HOVER_HEIGHT = 65

    def __init__(self, text: str, center_x: int = 0, center_y: int = 0):
        super().__init__(
            text,
            center_x,
            center_y,
            width=self.UNHOVER_WIDTH,
            height=self.UNHOVER_HEIGHT,
            style=UIStyle(border_width=0)
        )

        self.set_style_attrs(
            font_color=arcade.color.WHITE,
            font_color_hover=arcade.color.WHITE,
            font_color_press=arcade.color.WHITE,
            font_name="assets/fonts/LuckiestGuy-Regular.ttf",
            font_size=35
        )

    def on_hover(self) -> None:
        """Triggered when the mouse is over the sprite."""
        self.width = self.HOVER_WIDTH
        self.height = self.HOVER_HEIGHT

    def on_unhover(self) -> None:
        """Triggered when the mouse leaves the sprite."""
        self.width = self.UNHOVER_WIDTH
        self.height = self.UNHOVER_HEIGHT


class GameButton(MenuButton):
    """A button to start the game."""

    def on_click(self) -> None:
        """
        This callback will be triggered if the Clickable is pressed, focused, and MOUSE_RELEASE event is triggered.

        In case of multiple UIElements are overlapping, the last added to UIManager will be focused on MOUSE_RELEASE,
        so that only that one will trigger on_click.

        Starts the game by transitioning to the game view.
        """
        super().on_click()

        arcade.get_window().menu.curtains.set_scene('swimming_scene')


class ExitButton(MenuButton):
    """An exit button to close the game."""

    def on_click(self) -> None:
        """
        This callback will be triggered if the Clickable is pressed, focused, and MOUSE_RELEASE event is triggered.

        In case of multiple UIElements are overlapping, the last added to UIManager will be focused on MOUSE_RELEASE,
        so that only that one will trigger on_click.

        Closes the game window.
        """
        super().on_click()
        arcade.close_window()


class MenuScene(BaseScene):
    """Main menu view."""

    background_music = arcade.load_sound("assets/audio/music/Title Screen.mp3")

    def __init__(self):
        """Initialize the view."""
        arcade.set_background_color(arcade.color.WHITE)
        self.background: arcade.Texture = None
        self.ui_manager = MenuUIManager()

        self.background_player = None
        super().__init__()

    def setup(self) -> None:
        """Sets the background and the buttons."""
        self.background = arcade.load_texture("assets/title-screen/title_screen_no_buttons.png")
        self.ui_manager.purge_ui_elements()

        buttons = {"NEW GAME": GameButton, "HIGH SCORES": MenuButton, "SETTINGS": MenuButton, "EXIT GAME": ExitButton}
        x_coor = constants.SCREEN_WIDTH // 4.2  # Empirically chosen to be centered under the top left text.

        for i, (name, button) in enumerate(buttons.items()):
            self.ui_manager.add_ui_element(
                button(name, center_x=x_coor, center_y=constants.SCREEN_HEIGHT * 2 // 3 - i * 75)
            )

        self.background_player = arcade.play_sound(self.background_music)

    def draw(self) -> None:
        """
        Called when this view should draw.

        Draws in the background image.
        """
        arcade.start_render()
        self.background.draw_sized(
            constants.SCREEN_WIDTH // 2,
            constants.SCREEN_HEIGHT // 2,
            constants.SCREEN_WIDTH,
            constants.SCREEN_HEIGHT
        )

    def enter_scene(self, previous_scene: BaseScene) -> None:
        """Called when this view is shown."""
        self.setup()

    def leave_scene(self, next_scene: BaseScene) -> None:
        """Called when this view is not shown anymore."""
        self.ui_manager.unregister_handlers()
        if self.background_player and self.background_player.playing:
            arcade.stop_sound(self.background_player)


class MenuView(arcade.View):
    """Main application class."""

    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.WARM_BLACK)
        self.curtains = Curtains(self)
        self.curtains.add_scene('main_menu', MenuScene())
        self.curtains.add_scene('swimming_scene', DuckScene())
        self.curtains.set_scene('main_menu')
