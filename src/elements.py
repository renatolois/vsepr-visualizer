import glm
from atom import Atom


class Hydrogen(Atom):
    def __init__(self, radius=None, color=None, **kwargs):
        cloud_radius = radius if radius is not None else 1.0
        super().__init__(
            nucleus_radius=cloud_radius * 0.3,
            nucleus_color=color if color is not None else glm.vec4(0.9, 0.9, 0.9, 1.0),
            electron_radius=cloud_radius * 0.1,
            electron_cloud_radius=cloud_radius,
            electron_cloud_num_electrons=1,
            **kwargs
        )


class Helium(Atom):
    def __init__(self, radius=None, color=None, **kwargs):
        cloud_radius = radius if radius is not None else 1.0
        super().__init__(
            nucleus_radius=cloud_radius * 0.3,
            nucleus_color=color if color is not None else glm.vec4(0.8, 0.9, 1.0, 1.0),
            electron_radius=cloud_radius * 0.1,
            electron_cloud_radius=cloud_radius,
            electron_cloud_num_electrons=2,
            **kwargs
        )


class Carbon(Atom):
    def __init__(self, radius=None, color=None, **kwargs):
        cloud_radius = radius if radius is not None else 1.0
        super().__init__(
            nucleus_radius=cloud_radius * 0.3,
            nucleus_color=color if color is not None else glm.vec4(0.3, 0.3, 0.3, 1.0),
            electron_radius=cloud_radius * 0.1,
            electron_cloud_radius=cloud_radius,
            electron_cloud_num_electrons=4,
            **kwargs
        )


class Nitrogen(Atom):
    def __init__(self, radius=None, color=None, **kwargs):
        cloud_radius = radius if radius is not None else 1.0
        super().__init__(
            nucleus_radius=cloud_radius * 0.3,
            nucleus_color=color if color is not None else glm.vec4(0.1, 0.1, 0.9, 1.0),
            electron_radius=cloud_radius * 0.1,
            electron_cloud_radius=cloud_radius,
            electron_cloud_num_electrons=5,
            **kwargs
        )


class Oxygen(Atom):
    def __init__(self, radius=None, color=None, **kwargs):
        cloud_radius = radius if radius is not None else 1.0
        super().__init__(
            nucleus_radius=cloud_radius * 0.3,
            nucleus_color=color if color is not None else glm.vec4(0.9, 0.1, 0.1, 1.0),
            electron_radius=cloud_radius * 0.1,
            electron_cloud_radius=cloud_radius,
            electron_cloud_num_electrons=6,
            **kwargs
        )


class Fluorine(Atom):
    def __init__(self, radius=None, color=None, **kwargs):
        cloud_radius = radius if radius is not None else 1.0
        super().__init__(
            nucleus_radius=cloud_radius * 0.3,
            nucleus_color=color if color is not None else glm.vec4(0.5, 0.8, 0.2, 1.0),
            electron_radius=cloud_radius * 0.1,
            electron_cloud_radius=cloud_radius,
            electron_cloud_num_electrons=7,
            **kwargs
        )


class Neon(Atom):
    def __init__(self, radius=None, color=None, **kwargs):
        cloud_radius = radius if radius is not None else 1.0
        super().__init__(
            nucleus_radius=cloud_radius * 0.3,
            nucleus_color=color if color is not None else glm.vec4(1.0, 0.5, 0.8, 1.0),
            electron_radius=cloud_radius * 0.1,
            electron_cloud_radius=cloud_radius,
            electron_cloud_num_electrons=8,
            **kwargs
        )


class Sulfur(Atom):
    def __init__(self, radius=None, color=None, **kwargs):
        cloud_radius = radius if radius is not None else 1.0
        super().__init__(
            nucleus_radius=cloud_radius * 0.3,
            nucleus_color=color if color is not None else glm.vec4(1.0, 0.9, 0.0, 1.0),
            electron_radius=cloud_radius * 0.1,
            electron_cloud_radius=cloud_radius,
            electron_cloud_num_electrons=6,
            **kwargs
        )


class Chlorine(Atom):
    def __init__(self, radius=None, color=None, **kwargs):
        cloud_radius = radius if radius is not None else 1.0
        super().__init__(
            nucleus_radius=cloud_radius * 0.3,
            nucleus_color=color if color is not None else glm.vec4(0.5, 0.8, 0.1, 1.0),
            electron_radius=cloud_radius * 0.1,
            electron_cloud_radius=cloud_radius,
            electron_cloud_num_electrons=7,
            **kwargs
        )