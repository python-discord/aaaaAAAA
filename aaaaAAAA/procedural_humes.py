import random
import sys
from collections import namedtuple
from colorsys import hls_to_rgb
from pathlib import Path
from typing import Optional

from PIL import Image, ImageChops

ProceduralDucky = namedtuple("ProceduralDucky", "image hat equipment outfit")
DuckyColors = namedtuple("DuckyColors", "eye_main eye_wing wing body beak")
Color = tuple[int, int, int]

DUCKY_SIZE = (600, 1194)
ASSETS_PATH = Path("assets/duck-builder")

HAT_CHANCE = .7
EQUIPMENT_CHANCE = .4
OUTFIT_CHANCE = .5


def make_ducky() -> ProceduralDucky:
    """Generate a fully random ducky and returns a ProceduralDucky object."""
    return ProceduralDuckyGenerator().generate()


def _load_image_assets(file_path: str) -> list[tuple[str, Image]]:
    return [
        (filename.stem, Image.open(filename))
        for filename in (ASSETS_PATH / file_path).iterdir()
        if not filename.is_dir()
    ]


class ProceduralDuckyGenerator:
    """Temporary class used to generate a ducky."""

    templates = {
        10: Image.open(ASSETS_PATH / "manduck/variation 2/manduck_2_pants.png"),
        9: Image.open(ASSETS_PATH / "manduck/manduck_bill.png"),
        8: Image.open(ASSETS_PATH / "manduck/manduck_head.png"),
        7: Image.open(ASSETS_PATH / "manduck/manduck_eye.png"),
        6: Image.open(ASSETS_PATH / "manduck/variation 2/equipment/manduck_2_radio.png"),
        5: Image.open(ASSETS_PATH / "manduck/variation 2/outfits/manduck_2_belt.png"),
        4: Image.open(ASSETS_PATH / "manduck/variation 2/manduck_2_shirt.png"),
        3: Image.open(ASSETS_PATH / "manduck/variation 2/manduck_2_hands.png"),
        2: Image.open(ASSETS_PATH / "manduck/variation 2/outfits/manduck_2_beard.png"),
        1: Image.open(ASSETS_PATH / "manduck/hats/manduck_hat_durag.png")
    }

    # hats = _load_image_assets("manduck/hats")
    # equipments = _load_image_assets("manduck/variation 2/equipment")
    # outfits = _load_image_assets("manduck/variation 2/outfits")

    def __init__(self) -> None:
        self.output: Image.Image = Image.new("RGBA", DUCKY_SIZE, color=(0, 0, 0, 0))
        self.colors = self.make_colors()

        self.hat = None
        self.equipment = None
        self.outfit = None

    def generate(self) -> ProceduralDucky:
        """Actually generate the ducky."""
        self.apply_layer(self.templates[10])
        self.apply_layer(self.templates[9])
        self.apply_layer(self.templates[8])
        self.apply_layer(self.templates[7])
        self.apply_layer(self.templates[6])
        self.apply_layer(self.templates[5], self.colors.beak)
        self.apply_layer(self.templates[4], self.colors.body)

        self.apply_layer(self.templates[3], self.colors.wing)
        self.apply_layer(self.templates[2], self.colors.eye_wing)
        self.apply_layer(self.templates[1], self.colors.eye_main)

        return ProceduralDucky(self.output, self.hat, self.equipment, self.outfit)

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
    def make_colors(cls) -> DuckyColors:
        """Create a matching DuckyColors object."""
        hue = random.random()
        dark_variant = random.choice([True, False])
        eye, wing, body, beak = (cls.make_color(hue, dark_variant) for i in range(4))

        # Lower the eye light
        eye_main = (eye[0], max(.1, eye[1] - .7), eye[2])
        eye_wing = (eye[0], min(.9, eye[1] + .4), eye[2])
        # Shift the hue of the beck
        beak = (beak[0] + .1 % 1, beak[1], beak[2])

        scalar_colors = [hls_to_rgb(*color_pair) for color_pair in (eye_main, eye_wing, wing, body, beak)]
        colors = (tuple(int(color * 256) for color in color_pair) for color_pair in scalar_colors)

        return DuckyColors(*colors)


# If this file is executed we generate a random ducky and save it to disk
# A second argument can be given to seed the duck (that sounds a bit weird doesn't it)
if __name__ == "__main__":
    if len(sys.argv) > 1:
        random.seed(sys.argv[1])

    ducky = make_ducky()
    print(*("{0}: {1}".format(key, value) for key, value in ducky._asdict().items()), sep="\n")
    ducky.image.save("ducky.png")
    print("Ducky saved to disk!")
