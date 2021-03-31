from dataclasses import dataclass
from enum import Enum
from operator import attrgetter
from typing import Iterable

from PIL import Image

from aaaaAAAA.procedural_duckies import ProceduralDucky, ProceduralDuckyGenerator


class AttireKind(Enum):
    """The possible kinds of attire a duck can wear."""

    HATS = attrgetter('hats')
    EQUIPMENTS = attrgetter('equipments')
    OUTFITS = attrgetter('outfits')


@dataclass()
class Attire:
    """A piece of attire a duck is wearing."""

    kind: AttireKind
    name: str

    @property
    def image(self) -> Image.Image:
        """Return the image corresponding to this piece of attire."""
        attire_list = self.kind.value(ProceduralDuckyGenerator)
        for name, image in attire_list:
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

    A rule has 3 lists, require, deny and subrules. In order for a duck to match, it needs to both:
    Have at least one of the the pieces of attire in require
    Have none of the pieces of attire in deny
    """

    def __init__(
            self,
            require: Iterable[Attire] = (),
            deny: Iterable[Attire] = (),
    ):
        self.require = list(require)
        self.deny = list(deny)

    @classmethod
    def random(cls, difficulty: int):
        """Create a random rule."""
        pass

    def matches(self, ducky: ProceduralDucky) -> bool:
        """Check whether the ducky matches this rule."""
        required_match = False
        for required in self.require:
            if required.worn_by(ducky):
                required_match = True
        deny_match = True
        for denied in self.deny:
            if denied.worn_by(ducky):
                deny_match = False
        return required_match and deny_match
