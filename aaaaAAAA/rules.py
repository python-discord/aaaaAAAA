import random
from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from PIL import Image

from aaaaAAAA.procedural_duckies import ProceduralDucky, ProceduralDuckyGenerator


class AttireKind(Enum):
    """The possible kinds of attire a duck can wear."""

    HATS = ProceduralDuckyGenerator.hats
    EQUIPMENTS = ProceduralDuckyGenerator.equipments
    OUTFITS = ProceduralDuckyGenerator.outfits


@dataclass()
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
    def random(cls, difficulty: int):
        """
        Create a random rule of the given difficulty.

        Difficulty should be between 0 and 6.
        """
        allow = []
        if difficulty > 3:
            kinds = random.sample(list(Attire), difficulty - 3)
            for kind in kinds:
                allow.extend(attire for attire, _ in random.sample(kind.value, difficulty - 3))

        deny = []
        kinds = random.sample(list(Attire), min(difficulty, 3))
        for kind in kinds:
            deny.extend(attire for attire, _ in random.sample(kind.value, difficulty % 3 + 1))
        return cls(allow, deny)

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
