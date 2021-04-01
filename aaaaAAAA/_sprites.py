import arcade

DUCKY_SPEED = 240


class Ducky(arcade.Sprite):
    """Ducky sprite."""

    def __init__(self, ducky_name: str, scale: float = 1, *args, **kwargs):
        self.image_file_name = f"assets/{ducky_name}.png"
        super().__init__(self.image_file_name, scale, hit_box_algorithm="None", *args, **kwargs)

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
