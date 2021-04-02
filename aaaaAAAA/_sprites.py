from math import degrees, sin
from random import randint, shuffle
from typing import Optional

import arcade
from arcade_curtains import KeyFrame, Sequence

from aaaaAAAA import constants

DUCKY_SPEED = 240


class Ducky(arcade.Sprite):
    """Ducky sprite."""

    def __init__(self, ducky_name: str, scale: float = 1, *args, **kwargs):
        self.image_file_name = f"assets/{ducky_name}.png"
        super().__init__(self.image_file_name, scale,
                         hit_box_algorithm="None", flipped_horizontally=True,
                         *args, **kwargs)
        self.path_seq = self.sequence_gen(random=True)
        self.pondhouse_seq = self.sequence_gen(random=True, loop=True)
        self.pond_seq = self.sequence_gen(random=True, loop=True, pond=True)

    @staticmethod
    def expand(self: arcade.Sprite, x: float, y: float) -> None:
        """Slightly grow the sprite size."""
        self.width *= 1.1
        self.height *= 1.1
        self.draw()

    @staticmethod
    def shrink(self: arcade.Sprite, x: float, y: float) -> None:
        """Slightly retract the sprite size."""
        self.width /= 1.1
        self.height /= 1.1
        self.draw()

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
