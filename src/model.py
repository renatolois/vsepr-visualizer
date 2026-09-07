from typing import List, Optional, Union
from mesh import Mesh
from material import Material
from transform import Transform


class ModelPiece:
    def __init__(
            self,
            mesh: Mesh,
            material: Material,
            transform: Transform
    ) -> None:
        self.mesh: Mesh = mesh
        self.material: Material = material
        self.transform: Transform = transform


class Model:
    def __init__(
        self,
        arg1: Optional[Union[List[ModelPiece], List[Mesh]]] = None,
        arg2: Optional[List[Material]] = None,
        arg3: Optional[List[Transform]] = None
    ) -> None:
        if arg2 is None and arg3 is None:
            if arg1 is None:
                self.model_pieces: List[ModelPiece] = []
            else:
                self.model_pieces = arg1
        else:
            meshs = arg1
            materials = arg2
            transforms = arg3

            if meshs is None or materials is None or transforms is None:
                raise ValueError("meshs, materials, and transforms must be provided")  # noqa:E501

            if len(meshs) != len(materials) or len(meshs) != len(transforms):
                raise ValueError(
                    "Resource size mismatch: Meshes, Materials, and Transforms must have the same count."  # noqa: E501
                )

            self.model_pieces: List[ModelPiece] = []
            for i in range(len(meshs)):
                self.model_pieces.append(
                    ModelPiece(
                        meshs[i],
                        materials[i],
                        transforms[i])
                )

    def get_model_pieces(self) -> List[ModelPiece]:
        return self.model_pieces
