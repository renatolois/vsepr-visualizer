from typing import List, Optional
import glm
from model import Model
from transform import Transform


class Entity:
    def __init__(
        self,
        model: Optional[Model] = None,
        transform: Optional[Transform] = None
    ) -> None:
        if transform is None:
            transform = Transform()

        self.model: Optional[Model] = model
        self.transform: Transform = transform
        self.parent: Optional['Entity'] = None
        self.children: List['Entity'] = []

    def get_transform(self) -> Transform:
        return self.transform

    def set_transform(self, transform: Transform) -> None:
        self.transform = transform

    def set_translation(self, pos: glm.vec3) -> None:
        self.transform.set_position(pos)

    def set_rotation(self, rotation: glm.quat) -> None:
        self.transform.set_rotation(rotation)

    def set_scale(self, scale: glm.vec3) -> None:
        self.transform.set_scale(scale)

    def get_model(self) -> Optional[Model]:
        return self.model

    def get_model_matrix(self) -> glm.mat4:
        return self.transform.get_model_matrix()

    def add_child(self, child: 'Entity') -> None:
        child.parent = self
        self.children.append(child)

    def get_children(self) -> List['Entity']:
        return self.children
