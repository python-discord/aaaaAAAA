import random
import sys
from collections import namedtuple
from colorsys import hls_to_rgb
from pathlib import Path
from typing import Optional

from PIL import Image, ImageChops
from procedural_duckies import ProceduralDucky, make_ducky

ManDucky = namedtuple("ManDucky", "image hat equipment outfit")
DressColors = namedtuple("DressColors", "shirt pants")
Color = tuple[int, int, int]

DUCKY_SIZE = (600, 1194)
ASSETS_PATH = Path("assets/duck-builder")

HAT_CHANCE = .7
EQUIPMENT_CHANCE = .4
OUTFIT_CHANCE = .5


def make_manducky(ducky: ProceduralDucky) -> ManDucky:
    """Generate a fully random ducky and returns a ProceduralDucky object."""
    return ManDuckGenerator(ducky).generate()


def _load_image_assets(file_path: str) -> list[tuple[str, Image]]:
    return [
        (filename.stem, Image.open(filename))
        for filename in (ASSETS_PATH / file_path).iterdir()
        if not filename.is_dir()
    ]


class ManDuckGenerator:
    """Temporary class used to generate a duckyhuman."""

    def __init__(self, ducky: ProceduralDucky) -> None:
        self.output: Image.Image = Image.new("RGBA", DUCKY_SIZE, color=(0, 0, 0, 0))
        self.colors = ducky.colors

        self.variation = random.choice((1, 2))

        self.templates = {
            "head": Image.open(ASSETS_PATH / "manduck/manduck_head.png"),
            "eye": Image.open(ASSETS_PATH / "manduck/manduck_eye.png"),
            "bill": Image.open(ASSETS_PATH / "manduck/manduck_bill.png"),
            "hands": Image.open(ASSETS_PATH / f"manduck/variation {self.variation}/hands.png"),
        }

        if self.variation == 1:
            self.templates["dress"] = Image.open(ASSETS_PATH / f"manduck/variation {self.variation}/dress.png")
        if self.variation == 2:
            self.templates["shirt"] = Image.open(ASSETS_PATH / f"manduck/variation {self.variation}/shirt.png")
            self.templates["pants"] = Image.open(ASSETS_PATH / f"manduck/variation {self.variation}/pants.png")

        if ducky.hat:
            self.templates["hat"] = Image.open(ASSETS_PATH / f"manduck/hats/{ducky.hat}.png")
        if ducky.outfit:
            self.templates["outfit"] = Image.open(
                ASSETS_PATH / f"manduck/variation {self.variation}/outfits/{ducky.outfit}.png"
            )
        if ducky.equipment:
            self.templates["equipment"] = Image.open(
                ASSETS_PATH / f"manduck/variation {self.variation}/equipment/{ducky.equipment}.png"
            )

        self.hat = ducky.hat
        self.equipment = ducky.equipment
        self.outfit = ducky.outfit

    def generate(self) -> ManDucky:
        """Actually generate the ducky."""
        dress_colors = self.make_colors()

        if self.variation == 2:
            self.apply_layer(self.templates["pants"], dress_colors.pants)
        self.apply_layer(self.templates["bill"], self.colors.beak)
        self.apply_layer(self.templates["head"], self.colors.body)
        self.apply_layer(self.templates["eye"], self.colors.eye_main)
        if self.variation == 2:
            self.apply_layer(self.templates["shirt"], dress_colors.shirt)
        elif self.variation == 1:
            self.apply_layer(self.templates["dress"], dress_colors.shirt)
        if self.outfit and self.outfit != "bread":
            self.apply_layer(self.templates["outfit"])
        if self.equipment:
            self.apply_layer(self.templates["equipment"])
        self.apply_layer(self.templates["hands"], self.colors.wing)
        if self.outfit and self.outfit == "beard":
            self.apply_layer(self.templates["outfit"])
        if self.hat:
            self.apply_layer(self.templates["hat"])

        return ManDucky(self.output, self.hat, self.equipment, self.outfit)

    def apply_layer(self, layer: Image.Image, recolor: Optional[Color] = None) -> None:
        """Add the given layer on top of the ducky. Can be recolored with the recolor argument."""
        if recolor:
            layer = ImageChops.multiply(layer, Image.new("RGBA", DUCKY_SIZE, color=recolor))
        self.output.alpha_composite(layer)

    @staticmethod
    def make_color(hue: float, dark_variant: bool) -> tuple[float, float, float]:
        """Make a nice hls color to use in a duck."""
        saturation = 1
        lightness = random.uniform(.7, .85)

        # green and blue do not like high lightness, so we adjust this depending on how far from blue-green we are
        # hue_fix is the square of the distance between the hue and cyan (0.5 hue)
        hue_fix = (1 - abs(hue - 0.5))**2
        # magic fudge factors
        lightness -= hue_fix * 0.15
        if dark_variant:
            lightness -= hue_fix * 0.25
        saturation -= hue_fix * 0.1

        return hue, lightness, saturation

    @classmethod
    def make_colors(cls) -> DressColors:
        """Create a matching DuckyColors object."""
        hue = random.random()
        dark_variant = random.choice([True, False])
        shirt, pants = (cls.make_color(hue, dark_variant) for i in range(2))

        scalar_colors = [hls_to_rgb(*color_pair) for color_pair in (shirt, pants)]
        colors = (tuple(int(color * 256) for color in color_pair) for color_pair in scalar_colors)

        return DressColors(*colors)


# If this file is executed we generate a random ducky and save it to disk
# A second argument can be given to seed the duck (that sounds a bit weird doesn't it)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        random.seed(sys.argv[1])

    ducky = make_ducky()
    ducky = make_manducky(ducky)
    print(*("{0}: {1}".format(key, value) for key, value in ducky._asdict().items()), sep="\n")
    ducky.image.save("ducky.png")
    print("Ducky saved to disk!")
