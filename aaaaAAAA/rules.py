import random
from dataclasses import dataclass
from enum import Enum
from functools import cache
from typing import Iterable

import arcade
from PIL import Image

from aaaaAAAA.constants import SCREEN_HEIGHT, SCREEN_WIDTH
from aaaaAAAA.procedural_duckies import ProceduralDucky, ProceduralDuckyGenerator, make_ducky


class AttireKind(Enum):
    """The possible kinds of attire a duck can wear."""

    HATS = ProceduralDuckyGenerator.hats
    EQUIPMENTS = ProceduralDuckyGenerator.equipments
    OUTFITS = ProceduralDuckyGenerator.outfits


@dataclass(frozen=True)
class Attire:
    """A piece of attire a duck is wearing."""

    kind: AttireKind
    name: str

    @property
    def image(self) -> Image.Image:
        """Return the image corresponding to this piece of attire."""
        for name, image in self.kind.value:
            if name == self.name:
                return image
        raise ValueError(f'no attire of kind {self.kind} with the name {self.name} exists')

    def worn_by(self, ducky: ProceduralDucky) -> bool:
        """Return whether a ducky is wearing this piece of attire."""
        if self.kind is AttireKind.HATS:
            return self.name == ducky.hat
        if self.kind is AttireKind.EQUIPMENTS:
            return self.name == ducky.equipment
        if self.kind is AttireKind.OUTFITS:
            return self.name == ducky.outfit


class Rule:
    """
    Represents a predicate for ducks.

    A rule has 3 lists, allow and deny. In order for a duck to match, it needs to both:
    Have at least one of the the pieces of attire in require
    Have none of the pieces of attire in deny
    """

    def __init__(
            self,
            allow: Iterable[Attire] = (),
            deny: Iterable[Attire] = (),
    ):
        self.allow = list(allow)
        self.deny = list(deny)

    @classmethod
    def rand_attires(cls, n: int) -> list[Attire]:
        """Create n random attires."""
        return random.sample([
            Attire(kind, name)
            for kind in AttireKind
            for name, image in kind.value
        ], n)

    @classmethod
    def random(cls, difficulty: int) -> "Rule":
        """
        Create a random rule of the given difficulty.

        Difficulty should be between 0 and 6.
        """
        allow = set(cls.rand_attires(max(difficulty * 2 - 4, 0)))
        deny = set(cls.rand_attires((difficulty * 2 + 2) % 8))
        return cls(allow - deny, deny)

    def matches(self, ducky: ProceduralDucky) -> bool:
        """Check whether the ducky matches this rule."""
        allowed_match = not self.allow
        for allowed in self.allow:
            if allowed.worn_by(ducky):
                allowed_match = True
        deny_match = True
        for denied in self.deny:
            if denied.worn_by(ducky):
                deny_match = False
        return allowed_match and deny_match


class RuleView(arcade.View):
    """
    A view for testing out the rules.

    Once we have game, just take some methods from this and delete it.
    """

    def __init__(self):
        super().__init__()
        self.difficulty = 0
        self.score = 0
        self.answer = None
        self.rule = Rule.random(self.difficulty)
        self.current_duck = make_ducky()
        self.duck_texture = arcade.Texture('duck', self.current_duck.image)

    def setup(self) -> None:
        """This should set up your game and get it ready to play."""
        self.difficulty = 0
        self.score = 0
        self.current_duck = make_ducky()
        self.duck_texture = arcade.Texture('duck', self.current_duck.image)

    def on_show(self) -> None:
        """Called when switching to this view."""
        arcade.set_background_color(arcade.color.LIGHT_BLUE)

    def on_draw(self) -> None:
        """Draw everything for the game."""
        arcade.start_render()
        duck_dim = SCREEN_WIDTH * 2 / 3, SCREEN_HEIGHT - 210, 200, 200
        arcade.draw_xywh_rectangle_filled(*duck_dim, arcade.color.LIGHT_BLUE)
        arcade.draw_lrwh_rectangle_textured(*duck_dim, self.duck_texture)
        arcade.draw_text(
            f"Difficulty: {self.difficulty} Score: {self.score}",
            10, 10,
            arcade.color.ALIZARIN_CRIMSON
        )
        self.draw_rule(0, SCREEN_HEIGHT - 400)

    def on_update(self, delta_time: float) -> None:
        """Check for answers."""
        if self.answer is not None:
            if self.answer == self.rule.matches(self.current_duck):
                self.score += 1
            else:
                self.score -= 1
            self.answer = None
            self.current_duck = make_ducky()
            self.duck_texture = arcade.Texture(str(random.randrange(10**10)), self.current_duck.image)
            arcade.cleanup_texture_cache()
            self.rule = Rule.random(self.difficulty)

    def on_key_press(self, key: int, _modifiers: int) -> None:
        """
        Handle key presses.

        A - allow this duck
        D - deny this duck
        W - increase difficulty
        S - decrease difficulty
        """
        if key == arcade.key.A:
            self.answer = True
        if key == arcade.key.D:
            self.answer = False

        if key == arcade.key.W:
            self.difficulty = min(6, max(0, self.difficulty + 1))
        if key == arcade.key.S:
            self.difficulty = min(6, max(0, self.difficulty - 1))

    @cache
    def attire_texture(self, attire: Attire) -> arcade.Texture:
        """Get a texture for a piece of attire."""
        return arcade.Texture(attire.name, attire.image)

    def draw_attire(self, x: float, y: float, attire: Attire, width: float = 30) -> None:
        """Draw a piece of attire."""
        texture = self.attire_texture(attire)
        scale = width / texture.width
        texture.draw_scaled(x, y, scale)

    def draw_attire_row(self, x: float, y: float, attires: Iterable[Attire]) -> None:
        """Draw a row of attires."""
        width = 100
        for i, attire in enumerate(attires):
            self.draw_attire(x + width * i, y, attire, width)

    def draw_rule(self, x: float, y: float) -> None:
        """Draw the current rule."""
        if self.rule.allow:
            arcade.draw_text("+", x, y, arcade.color.GREEN, font_size=30)
            self.draw_attire_row(x + 80, y, self.rule.allow)
        if self.rule.deny:
            arcade.draw_text("-", x, y + 200, arcade.color.ALABAMA_CRIMSON, font_size=30)
            self.draw_attire_row(x + 80, y + 200, self.rule.deny)


if __name__ == '__main__':
    window = arcade.Window(title='rule test', width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    rule = RuleView()
    window.show_view(rule)
    arcade.run()
