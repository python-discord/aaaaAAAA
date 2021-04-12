from math import degrees, sin
from random import randint, shuffle
from typing import Optional, Union

import PIL.Image
import arcade
from arcade.texture import Texture
from arcade_curtains import KeyFrame, Sequence

from aaaaAAAA import constants
from aaaaAAAA.ducky_generation.procedural_duck_people import make_manducky
from aaaaAAAA.ducky_generation.procedural_duckies import make_ducky

DUCKY_SPEED = 240


class PydisSprite(arcade.Sprite):
    """Base sprite type."""

    def __lt__(self, other: arcade.Sprite):
        """Compare two sprites by their sprite list texture ids."""
        # Fixes a bug in arcade.Sprite where the code for overlapping sprites is
        # not updated for how sprite lists now work with textures
        if not other.sprite_lists:
            return self
        if not self.sprite_lists:
            return other
        return max(i.texture_id for i in self.sprite_lists) < max(i.texture_id for i in other.sprite_lists)


class Ducky(PydisSprite):
    """Ducky sprite."""

    ducks = arcade.SpriteList()

    def __init__(self, scale: float = 1, *args, **kwargs):
        ducky = make_ducky()
        self.ducky_name = f"{ducky.hat}-{ducky.equipment}-{ducky.outfit}"
        manducky = make_manducky(ducky)
        self.ducky_name = f"{ducky.hat}-{ducky.equipment}-{ducky.outfit}"
        self.man_ducky_name = f"{manducky.hat}-{manducky.equipment}-{manducky.outfit}"

        super().__init__(scale=scale, flipped_horizontally=True, *args, **kwargs)
        for name, texture in ((self.ducky_name, ducky), (self.man_ducky_name, manducky)):
            self.append_texture(
                Texture(name, texture.image.transpose(PIL.Image.FLIP_LEFT_RIGHT), hit_box_algorithm="None"))
        self.texture = self.textures[0]

        self.hat = ducky.hat
        self.equipment = ducky.equipment
        self.outfit = ducky.outfit

        self.path_seq = self.sequence_gen(random=False)
        self.pondhouse_seq = self.sequence_gen(random=True, loop=True)
        self.pond_seq = self.sequence_gen(random=True, loop=True, pond=True)
        self.off_screen = self._off_screen
        self.ducks.append(self)

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
                     pond: Optional[bool] = False,
                     shift: Optional[list[tuple[float, float]]] = None) -> Sequence:
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
        if shift:
            points = shift
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

    def manify(self) -> Sequence:
        """Return a sequence to move the ducky to the pondhouse viewer."""
        x1, y1 = 0, constants.SCREEN_HEIGHT * .3
        x2, y2 = constants.SCREEN_WIDTH * .175, constants.SCREEN_HEIGHT * .3

        seq = Sequence()
        seq.add_keyframes((0, KeyFrame(position=(x1, y1), alpha=0, scale=.21, angle=0)),
                          (.5, KeyFrame(position=(x1 + 30, y1 + 7), scale=.35, angle=0)))
        for t, pos in enumerate(range(int(x1), int(x2), 10), start=2):
            if t % 2:
                seq.add_keyframe(t/2, KeyFrame(position=(pos, y1 + 7)))
            else:
                seq.add_keyframe(t/2, KeyFrame(position=(pos, y1)))
            seq.add_keyframe((t+1)/2, KeyFrame(position=(x2, y2), angle=0))

        return seq

    def duckify(self) -> Sequence:
        """Return a sequence to move the ducky to the pondhouse viewer."""
        x1, y1 = self.position
        x2, y2 = .3 * constants.SCREEN_WIDTH, .3 * constants.SCREEN_HEIGHT

        seq = Sequence()
        for t, pos in enumerate(range(int(x1), int(x2), 10)):
            if t % 2:
                seq.add_keyframe(t/2, KeyFrame(position=(pos, y1 + 7)))
            else:
                seq.add_keyframe(t/2, KeyFrame(position=(pos, y1)))
            seq.add_keyframe((t+1)/2, KeyFrame(position=(x2, y2), angle=0))
        seq.add_keyframes(
            ((t+2)/2, KeyFrame(position=(x2, y2), scale=.21)),
            ((t+3)/2, KeyFrame(position=(x2, y2), scale=.07)))

        return seq

    def __repr__(self) -> str:
        """Return debug representation."""
        return f"<{self.__class__.__name__} {self.ducky_name=}>"

    def next_move(self) -> Union[Sequence, None]:
        """Create a sequence to progress the duck to the next point."""
        x, y = self.center_x / constants.SCREEN_WIDTH, self.center_y / constants.SCREEN_HEIGHT
        pos = min(constants.POINTS_HINT, key=lambda pos_xy: (abs(x-pos_xy[0]), abs(y-pos_xy[1])))
        if pos == constants.POINTS_HINT[-1]:
            return
        pos_index = constants.POINTS_HINT.index(pos)
        return self.sequence_gen(shift=constants.POINTS_HINT[pos_index:pos_index+2])


class Lily(PydisSprite):
    """Lily sprites."""

    lilies = arcade.SpriteList()

    def __init__(self, scale: float = 1, position: tuple[float, float] = (0, 0), *args, **kwargs):
        super().__init__(scale=scale, *args, **kwargs)
        self.lily = randint(1, 4)
        self.position = position
        paths = [f"assets/foliage/lillies/png/Lily {self.lily} - {colour}.png"
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

    def change_texture(self, colour: Optional[int] = 0) -> None:
        """Change the texture used by the sprite."""
        self.texture = self.textures[colour]
