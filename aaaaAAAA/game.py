import datetime
import random
from enum import IntEnum
from itertools import chain
from random import choice
from typing import Optional

import arcade
from PIL import Image
from arcade import Texture
from arcade.gui import UIImageButton, UIManager
from arcade_curtains import BaseScene, Curtains

from aaaaAAAA import _sprites, constants

TEXT_RGB = (70, 89, 134)
FONT = "assets/fonts/LuckiestGuy-Regular.ttf"

RULES = {
    "Royal Party - Crowns Only": lambda ducky: ducky.hat == "crown",
    "Face Warmers - Beards Only": lambda ducky: ducky.outfit == "beard",
    "Biblical Pool - Halos and Horns\nOnly": lambda ducky: ducky.hat in ("horns", "halo"),
    "Safe Space - No weapons": lambda ducky: not (ducky.equipment in ("baseball_bat", "lightsaber", "Sword")),
    "Magical Night - Wizardry": lambda ducky: ducky.hat == "wizard" or ducky.equipment == "wand",
    "Celebrators - Ducks that have\nsomething to\ncelebrate": lambda ducky: ducky.hat in ("mortarboard", "party")
}


class Colour(IntEnum):
    """Sprite colors."""

    GREEN = 0
    YELLOW = 1
    PURPLE = 2
    BLACK = 3


class Toxicity(IntEnum):
    """Toxicity levels for the overworld."""

    HEALTHY = 0
    DECAYING = 1
    DISGUSTING = 2
    TOXIC = 3
    DEADLY = 4


def load_scaled_texture(name: str, path: str, size: float) -> arcade.Texture:
    """Load a texture from a path with a specific size in relation to the window."""
    window = arcade.get_window()
    size = (window.width * size, window.height * size)
    image = Image.open(path)
    image.thumbnail(size)
    return arcade.Texture(name, image, hit_box_algorithm="Detailed")


class AllowButton(UIImageButton):
    """A class representing the button to allow ducks into the pond."""

    def __init__(self, scene: "DuckScene"):
        released = load_scaled_texture("allow_released", "assets/overworld/buttons/allow_button.png", 0.18)
        pressed = load_scaled_texture("allow_pressed", "assets/overworld/buttons/allow_button_depressed.png", 0.18)
        window = arcade.get_window()
        self.scene = scene
        super().__init__(released, press_texture=pressed,
                         center_x=window.width * 0.735,
                         center_y=window.height * 0.085)

    def on_release(self) -> None:
        """Call the allow action."""
        self.scene.allow()
        super().on_release()


class AnnihilateButton(UIImageButton):
    """A class representing the button to annihilate ducks."""

    def __init__(self, scene: "DuckScene"):
        released = load_scaled_texture("annihilate_released", "assets/overworld/buttons/annihilate_button.png", 0.18)
        pressed = load_scaled_texture("annihilate_pressed",
                                      "assets/overworld/buttons/annihilate_button_depressed.png", 0.18)
        window = arcade.get_window()
        self.scene = scene
        super().__init__(released, press_texture=pressed,
                         center_x=window.width * 0.575,
                         center_y=window.height * 0.12)

    def on_release(self) -> None:
        """Call the allow action."""
        self.scene.deny()
        super().on_release()


class DuckScene(BaseScene):
    """Scene showing Ducks moving down the river to the pondhouse."""

    def __init__(self, debug: Optional[bool] = False):
        self.debug = debug
        super().__init__()

    def setup(self) -> None:
        """Setup the scene assets."""
        window = arcade.get_window()
        scale = window.width / constants.SCREEN_WIDTH

        self.toxicity = Toxicity.HEALTHY
        self.toxicity_assets = [
            {
                "level": Toxicity.HEALTHY,
                "lily_color": Colour.GREEN,
                "overworld": arcade.load_texture("assets/overworld/overworld_healthy_no_lilies.png"),
                "music": arcade.load_sound("assets/audio/music/Overworld - Healthy.mp3")
            },
            {
                "level": Toxicity.DECAYING,
                "lily_color": Colour.YELLOW,
                "overworld": arcade.load_texture("assets/overworld/overworld_decaying_no_lilies.png"),
                "music": arcade.load_sound("assets/audio/music/Overworld - Decaying.mp3")
            },
            {
                "level": Toxicity.DISGUSTING,
                "lily_color": Colour.YELLOW,
                "overworld": arcade.load_texture("assets/overworld/overworld_disgusting_no_lilies.png"),
                "music": arcade.load_sound("assets/audio/music/Overworld - Disgusting.mp3")
            },
            {
                "level": Toxicity.TOXIC,
                "lily_color": Colour.PURPLE,
                "overworld": arcade.load_texture("assets/overworld/overworld_toxic_no_lilies.png"),
                "music": arcade.load_sound("assets/audio/music/Overworld - Toxic.mp3")
            },
            {
                "level": Toxicity.DEADLY,
                "lily_color": Colour.BLACK,
                "overworld": arcade.load_texture("assets/overworld/overworld_deadly_no_lilies.png"),
                "music": arcade.load_sound("assets/audio/music/Overworld - Deadly.mp3")
            },
        ]

        # Play all the music at the same time, but set volumes to 0 for all but the active one.
        # This way, hopefully, we'll be able to switch between them smoothly.
        for asset in self.toxicity_assets:
            level = asset['level']
            if level == self.toxicity:
                player = arcade.play_sound(asset["music"], looping=True)
            else:
                player = arcade.play_sound(asset["music"], looping=True, volume=0.0)

            self.toxicity_assets[level]["player"] = player

        self.background = arcade.load_texture("assets/overworld/overworld_healthy_no_lilies.png")

        self.pondhouse = arcade.Sprite("assets/overworld/pondhouse/pondhouse_cropped.png", scale=scale)
        self.pondhouse.position = (window.width * .66, window.height * .76)

        self.teller_window = arcade.Sprite("assets/overworld/teller window/teller_window.png", scale=scale)
        self.teller_window.position = (self.teller_window.width / 2, self.teller_window.height / 2)

        self.lilies = _sprites.Lily.lilies
        self.ducks = _sprites.Ducky.ducks
        self.path_queued_ducks = arcade.SpriteList()
        self.pond_ducks = arcade.SpriteList()
        self.pondhouse_ducks = arcade.SpriteList()
        self.leader = _sprites.Ducky(0.07)
        self.seq = self.leader.path_seq

        for x, y in constants.FOLIAGE_POND:
            pos = constants.SCREEN_WIDTH * x, constants.SCREEN_HEIGHT * y
            lily = _sprites.Lily(scale=.075, position=pos)
            self.events.hover(lily, lily.float_about)

        self.ui_manager = UIManager()

        self.rule = random.choice(list(RULES.keys()))
        self.current_duck = 0

        self.streak = 0
        self.game_end = datetime.datetime.now() + datetime.timedelta(minutes=2)

        self.passed = 0
        self.failed = 0
        self.start = datetime.datetime.now()

    def add_a_ducky(self, dt: Optional[float] = None) -> None:
        """Add a ducky to the scene, register some events and start animating."""
        if not constants.POINTS_HINT:
            return
        ducks = len(self.ducks) + len(self.path_queued_ducks)
        if ducks + len(self.pond_ducks) >= constants.DUCKS or ducks >= len(constants.POINTS_HINT):
            arcade.unschedule(self.add_a_ducky)
            return
        ducky = _sprites.Ducky(0.07)
        self.events.hover(ducky, ducky.expand)
        self.events.out(ducky, ducky.shrink)
        seq = ducky.path_seq
        duration = len(constants.POINTS_HINT) - len(self.ducks) - len(self.path_queued_ducks)
        seq.add_callback(duration-1, lambda: self.move_to_path_queue(ducky))
        self.animations.fire(ducky, seq)

    def enter_scene(self, previous_scene: BaseScene) -> None:
        """Start adding duckies on entering the scene."""
        self.ui_manager.add_ui_element(AllowButton(self))
        self.ui_manager.add_ui_element(AnnihilateButton(self))
        if not self.debug:
            arcade.schedule(self.add_a_ducky, len(constants.POINTS_HINT)*10/constants.DUCKS)

    def leave_scene(self, next_scene: BaseScene) -> None:
        """Called when leaving the scene."""
        self.ui_manager.unregister_handlers()

    def alter_toxicity(self, change_by: int) -> None:
        """Handle toxicity-related changes."""
        self.toxicity += change_by

        if self.toxicity == Toxicity.DEADLY:
            self.end_game()
            return

        assets = self.toxicity_assets[self.toxicity]
        lily_color = assets["lily_color"]
        music_player = assets["player"]
        overworld = assets["overworld"]
        all_music_players = [asset["player"] for asset in self.toxicity_assets]

        # Set the lilies to the right toxicity
        for lily in self.lilies:
            lily.change_texture(lily_color)

        # Set the background
        self.background = overworld

        # Silence the players
        for player in all_music_players:
            player.volume = 0.0

        # Set the main player to play
        music_player.volume = 1.0

    def draw_background(self, background: Texture) -> None:
        """Draw the correct background for the current toxicity."""
        self.background = background

    def draw(self) -> None:
        """Draw the background environment."""
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(
            0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, self.background
        )

        background = self.toxicity_assets[self.toxicity]["overworld"]
        self.draw_background(background)

        # Draw rule
        name, description = self.rule.upper().split(" - ")

        name = arcade.draw_text(
            name, 800, 290, TEXT_RGB, 70,
            align="center", anchor_x="center", anchor_y="center",
            font_name=FONT
        )

        description = arcade.draw_text(
            description, 800, 270, TEXT_RGB, 70,
            align="center", anchor_x="center", anchor_y="top",
            font_name=FONT
        )

        name.scale = 0.3
        description.scale = 0.25

        # Draw remaining time
        remaining = self.game_end - datetime.datetime.now()
        if remaining.total_seconds() <= 0:
            self.end_game()

        arcade.draw_text(str(remaining.seconds), 30, 650, TEXT_RGB, 35, font_name=FONT)

        super().draw()
        self.pondhouse.draw()
        self.teller_window.draw()

    def allow(self) -> None:
        """Allow the current duck into the pond."""
        if len(self.path_queued_ducks) == 0:
            return
        ducky = self.path_queued_ducks.pop(0)

        self.pondhouse_ducks.append(ducky)
        self.grant_entry(ducky)

        if RULES[self.rule](ducky):
            self.award_point()
        else:
            self.retract_point()

        self.update_rule()
        self.progress()

    def deny(self) -> None:
        """Deny the current duck from the pond."""
        if len(self.path_queued_ducks) == 0:
            return
        ducky = self.path_queued_ducks.pop(0)

        self.explode(ducky)

        if not RULES[self.rule](ducky):
            self.award_point()
        else:
            self.retract_point()

        self.update_rule()
        self.progress()

    def update_rule(self) -> None:
        """Update the game rule if enough ducks have been proccessed."""
        if self.current_duck >= 4:
            self.current_duck = 0

            new_rule = random.choice(list(RULES.keys()))
            while new_rule == self.rule:
                new_rule = random.choice(list(RULES.keys()))
            self.rule = new_rule

        else:
            self.current_duck += 1

    def award_point(self) -> None:
        """Award point for a correct choice."""
        self.passed += 1

        self.game_end = self.game_end + datetime.timedelta(seconds=5)

        if self.streak < 0:
            self.streak = 0

        self.streak += 1
        if self.streak >= 3:
            self.alter_toxicity(-1)
            self.streak = 0

    def retract_point(self) -> None:
        """Retract point for an incorrect choice."""
        self.failed += 1

        if self.streak > 0:
            self.streak = 0

        self.streak -= 1
        if self.streak <= -2:
            self.alter_toxicity(+1)
            self.streak = 0

    def explode(self, ducky: arcade.Sprite) -> None:
        """Blow up a denied duck."""
        # Super impressive explosions
        ducky.width = 0

    def move_to_path_queue(self, ducky: _sprites.Ducky) -> None:
        """Move the ducky into the path_queue spritelist."""
        # self.ducks.remove(ducky)
        self.path_queued_ducks.append(ducky)
        self.animations.kill(ducky)
        self.progress()

    def enter_pondhouse(self, ducky: _sprites.Ducky) -> None:
        """Duckies that are circling outside the pondhouse waiting to be processed."""
        self.path_queued_ducks.remove(ducky)
        if len(self.pondhouse_ducks) == 0:
            self.show_human_ducky(ducky)
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

    def end_game(self) -> None:
        """Immediately end the round."""
        # Cleanup
        self.ui_manager.unregister_handlers()
        self.curtains.scenes.pop("swimming_scene")

        # Switch over to game over scene
        self.curtains.add_scene("game_over_scene", GameOverView(self.passed, self.failed, self.start))
        self.curtains.set_scene("game_over_scene")

    def progress(self, dt: Optional[float] = 0) -> None:
        """Progress the ducks on the path."""
        for ducky in self.path_queued_ducks:
            move = ducky.next_move()
            if move:
                self.animations.fire(ducky, move)
            else:
                self.enter_pondhouse(ducky)

    def show_human_ducky(self, ducky: Optional[_sprites.Ducky]) -> None:
        """Show the human version of the ducky in the teller. Remove it if None."""
        print(f"DEBUG: showing human ducky {ducky}")
        # TODO: actual code

    def destroy_ducky(self, ducky: _sprites.Ducky) -> None:
        """Trigger the destroy animation on the ducky currently inside the teller."""
        print(f"DEBUG: destroying ducky {ducky}")
        # TODO: actual code

    def decrease_health(self) -> None:
        """Decrease the player's health points."""
        print("DEBUG: decreasing health")
        self.health -= 1
        self.overworld_texture_blend = 0.0
        for lily in self.lilies:
            lily.change_texture(self.lily_color[self.health])

        if self.health == 0:
            self.game_over()

    def game_over(self) -> None:
        """End the game."""
        # Cancel animations
        self.animations.animations.clear()
        # Stop new duckies
        arcade.unschedule(self.add_a_ducky)
        # Clear the waiting line
        while not self.pondhouse_ducks.empty():
            self.pondhouse_ducks.get()
        # Remove the ducky from the teller
        self.show_human_ducky(None)
        # Put the duckies upside down
        for ducky in chain(self.pond_ducks, self.ducks):
            ducky.deceased()


class QuitButton(UIImageButton):
    """A class representing the button to quit the game."""

    def __init__(self):
        released = load_scaled_texture("exit", "assets/overworld/buttons/exit_button.png", 0.16)
        window = arcade.get_window()
        super().__init__(released, center_x=window.width * 0.735, center_y=window.height * 0.085)

    def on_release(self) -> None:
        """Call the allow action."""
        super().on_click()
        arcade.close_window()


class MenuButton(UIImageButton):
    """A class representing the button to return to main menu."""

    def __init__(self, scene: "GameOverView"):
        released = load_scaled_texture("menu_released", "assets/overworld/buttons/menu_button.png", 0.18)
        pressed = load_scaled_texture("allow_pressed", "assets/overworld/buttons/allow_button_depressed.png", 0.18)
        released = load_scaled_texture("allow_pressed", "assets/overworld/buttons/allow_button_depressed.png", 0.18)
        window = arcade.get_window()
        self.scene = scene
        super().__init__(released, press_texture=pressed, center_x=window.width * 0.575, center_y=window.height * 0.12)

    def on_release(self) -> None:
        """Call the allow action."""
        self.scene.curtains.scenes.pop("game_over_scene")
        self.scene.ui_manager.unregister_handlers()

        self.scene.curtains.set_scene("main_menu")


class GameOverView(BaseScene):
    """View for the game over screen."""

    def __init__(self, passed: int, failed: int, start_time: datetime.datetime):
        super().__init__()
        self.passed = passed
        self.failed = failed
        self.total_time = datetime.datetime.now() - start_time
        self.ui_manager = UIManager()

    def setup(self) -> None:
        """Setup game over view."""
        self.background = arcade.load_texture("assets/overworld/overworld_deadly.png")

    def enter_scene(self, previous_scene: BaseScene) -> None:
        """Called when entering the scene."""
        self.ui_manager.add_ui_element(MenuButton(self))
        self.ui_manager.add_ui_element(QuitButton())

    def draw(self) -> None:
        """Draw the game over screen."""
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(
            0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, self.background
        )

        message = f"""
        Total Play Time: {self.total_time.seconds}s
        Total Ducks: {self.passed + self.failed}

        Correct: {self.passed}
        Mistakes: {self.failed}
        """

        text = arcade.draw_text(
            message,
            200, 160, TEXT_RGB, 75, font_name=FONT,
            align="center", anchor_x="center", anchor_y="center"
        )

        text.scale = 0.45


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
        elif symbol == ord('t'):
            self.curtains.current_scene.alter_toxicity(+1)
        elif symbol == ord('y'):
            self.curtains.current_scene.alter_toxicity(-1)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        """Add clicked point to points_hint as % of width/height."""
        if self.debug:
            constants.POINTS_HINT.append((round(x/self.window.width, 3), round(y/self.window.height, 3)))
        print(x, y)


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
