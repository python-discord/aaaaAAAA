import arcade


class Ducky(arcade.Sprite):
    """Ducky sprite."""

    def __init__(self, ducky_name: str, scale: float = 1, *args, **kwargs):
        self.image_file_name = f"img/{ducky_name}.png"
        super().__init__(self.image_file_name, scale, hit_box_algorithm="None", *args, **kwargs)
