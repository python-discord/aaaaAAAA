from math import degrees, sin
from random import randint, shuffle
from typing import Optional

import PIL.Image
import arcade
from arcade.texture import Texture
from arcade_curtains import KeyFrame, Sequence

from aaaaAAAA import constants
from aaaaAAAA.procedural_duckies import make_ducky

DUCKY_SPEED = 240


class Ducky(arcade.Sprite):
    """Ducky sprite."""

    def __init__(self, scale: float = 1, *args, **kwargs):
        ducky = make_ducky()
        ducky_name = f"{ducky.hat}-{ducky.equipment}-{ducky.outfit}"

        super().__init__(scale=scale, flipped_horizontally=True, *args, **kwargs)
        self.texture = Texture(ducky_name, ducky.image.transpose(PIL.Image.FLIP_LEFT_RIGHT), hit_box_algorithm="None")

        self.hat = ducky.hat
        self.equipment = ducky.equipment
        self.outfit = ducky.outfit

        self.path_seq = self.sequence_gen(random=False)
        self.pondhouse_seq = self.sequence_gen(random=True, loop=True)
        self.pond_seq = self.sequence_gen(random=True, loop=True, pond=True)
        self.off_screen = self._off_screen

    @staticmethod
    def expand(sprite: arcade.Sprite, x: float, y: float) -> None:
        """Slightly grow the sprite size."""
        sprite.width *= 1.1
        sprite.height *= 1.1

    @staticmethod
    def shrink(sprite: arcade.Sprite, x: float, y: float) -> None:
        """Slightly retract the sprite size."""
        sprite.width /= 1.1
        sprite.height /= 1.1

    @staticmethod
    def sequence_gen(random: Optional[bool] = False,
                     loop: Optional[bool] = False,
                     pond: Optional[bool] = False) -> Sequence:
        """
        Generate a Sequence for the ducky to follow.

        random: if true the transition between points will be between 2 and 5;
                additionally if pond is true will shuffle the pond points
        loop: sequence will loop and if pond is false will indicate to use the pondhouse points
        pond: indicates that the pond points are to be used
        """
        seq = Sequence(loop=loop)
        current = 0
        points = constants.POINTS_HINT
        if pond:
            points = constants.POND_HINT
            if random:
                shuffle(points)
        elif loop:
            points = constants.PONDHOUSE_HINT
            if constants.POINTS_HINT:
                points.insert(0, constants.POINTS_HINT[-1])
        for ((x1, y1), (x2, y2)) in zip(points[:-1], points[1:]):
            p1 = x1 * constants.SCREEN_WIDTH, y1 * constants.SCREEN_HEIGHT
            p2 = x2 * constants.SCREEN_WIDTH, y2 * constants.SCREEN_HEIGHT
            angle = degrees(sin((p2[0]-p1[0])/max((p2[1]-p1[1]), 1)))
            frames = 1
            if random:
                frames = randint(2, 5)
            seq.add_keyframes((current, KeyFrame(position=p1, angle=angle)),
                              (current+frames, KeyFrame(position=p2)))
            current += frames
        return seq

    def deceased(self) -> None:
        """Turn the Ducky upside down."""
        self.angle = 180

    def _off_screen(self) -> Sequence:
        """Return a sequence to move the ducky off screen."""
        x1, y1 = self.position
        x2, y2 = constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT * .64
        angle = degrees(sin((x2 - x1) / max((y2 - y1), 1)))
        seq = Sequence()
        seq.add_keyframes((0, KeyFrame(position=(x1, y1))),
                          (3, KeyFrame(position=(x2, y2), angle=angle)))
        return seq


class PondHouse(arcade.Sprite):
    """Pondhouse sprite."""

    def __init__(self, scale: float = 1, *args, **kwargs):
        super().__init__("assets/overworld/pondhouse/pondhouse_cropped.png", scale,
                         hit_box_algorithm="None", *args, **kwargs)

    @staticmethod
    def see_through(sprite: arcade.Sprite, x: float, y: float) -> None:
        """Make the sprite see through."""
        sprite.alpha = 75

    @staticmethod
    def opaque(sprite: arcade.Sprite, x: float, y: float) -> None:
        """Make the sprite opaque."""
        sprite.alpha = 255


class Lily(arcade.Sprite):
    """Lily sprites."""

    lilies = arcade.SpriteList()

    def __init__(self, scale: float = 1, position: tuple[float, float] = (0, 0), *args, **kwargs):
        super().__init__(scale=scale, *args, **kwargs)
        self.lily = randint(1, 4)
        self.position = position
        paths = [f"assets/foliage/lillies/png/Lily {self.lily} - {colour}-512.png"
                 for colour in ('Green', 'Yellow', 'Purple', 'Black')]
        for path in paths:
            self.append_texture(arcade.load_texture(path, hit_box_algorithm="None"))
        self.texture = self.textures[0]
        self.lilies.append(self)

    @staticmethod
    def float_about(sprite: arcade.Sprite, x: float, y: float) -> None:
        """Make the sprite move to x,y - position mouse enters the widget at."""
        sprite.center_x = x
        sprite.center_y = y

    def change_texture(self, colour: Optional[int] = 'Green') -> None:
        """Change the texture used by the sprite."""
        self.texture = self.textures[colour]
