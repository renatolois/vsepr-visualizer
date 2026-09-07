from typing import List, Optional
import glm
import OpenGL.GL as gl
from camera import Camera
from mesh import Mesh
from material import Material
from model import Model
from entity import Entity
from transform import Transform
from light import Light


class Renderer:
    def render_fullscreen_ortho_mat4(
        self,
        camera: Camera,
        mesh: Mesh,
        material: Material,
        transform: glm.mat4
    ) -> None:
        material.apply()
        mesh.bind()
        material.set_uniform("material.transform", transform)
        material.set_uniform("material.camera_view", camera.get_view_matrix())
        material.set_uniform(
            "material.camera_projection",
            camera.get_ortho_matrix()
        )

        gl.glDrawElements(
            gl.GL_TRIANGLES,
            mesh.get_indices_size(),
            gl.GL_UNSIGNED_INT,
            None
        )

    def render_fullscreen_ortho_transform(
        self,
        camera: Camera,
        mesh: Mesh,
        material: Material,
        transform: Transform
    ) -> None:
        self.render_fullscreen_ortho_mat4(
            camera,
            mesh,
            material,
            transform.get_model_matrix()
        )

    def render_fullscreen_ortho_model(
        self,
        camera: Camera,
        model: Model
    ) -> None:
        for piece in model.get_model_pieces():
            self.render_fullscreen_ortho_transform(
                camera,
                piece.mesh,
                piece.material,
                piece.transform
            )

    def render(
        self,
        camera: Camera,
        mesh: Mesh,
        material: Material,
        transform: glm.mat4,
        light: Optional[Light] = None
    ) -> None:
        material.apply()
        mesh.bind()
        material.set_uniform("material.transform", transform)
        material.set_uniform("material.camera_view", camera.get_view_matrix())
        material.set_uniform(
            "material.camera_projection",
            camera.get_projection_matrix()
        )

        if light is not None:
            material.set_uniform("light.translation", light.get_translation())
            material.set_uniform("light.color", light.get_color())
            material.set_uniform("light.intensity", light.get_intensity())

        gl.glDrawElements(
            gl.GL_TRIANGLES,
            mesh.get_indices_size(),
            gl.GL_UNSIGNED_INT,
            None
        )

    def render_transform(
        self,
        camera: Camera,
        mesh: Mesh,
        material: Material,
        transform: Transform,
        light: Optional[Light] = None
    ) -> None:
        self.render(
            camera,
            mesh,
            material,
            transform.get_model_matrix(),
            light
        )

    def render_model(
        self,
        camera: Camera,
        model: Model,
        light: Optional[Light] = None
    ) -> None:
        for piece in model.get_model_pieces():
            self.render_transform(
                camera,
                piece.mesh,
                piece.material,
                piece.transform,
                light
            )

    def render_entity(
        self,
        camera: Camera,
        entity: Entity,
        light: Optional[Light] = None,
        parent_transform: glm.mat4 = glm.mat4(1.0)
    ) -> None:
        model_matrix = parent_transform * entity.get_model_matrix()
        model = entity.get_model()

        if model is not None:
            for piece in model.get_model_pieces():
                final_transform = (
                        model_matrix * piece.transform.get_model_matrix()
                )

                self.render(
                    camera,
                    piece.mesh,
                    piece.material,
                    final_transform,
                    light
                )

        for child in entity.get_children():
            self.render_entity(camera, child, light, model_matrix)

    def render_entities(
        self,
        camera: Camera,
        entities: List[Entity],
        light: Optional[Light] = None
    ) -> None:
        for entity in entities:
            self.render_entity(camera, entity, light)

    def set_view_port(self, camera: Camera, w: int, h: int) -> None:
        if h == 0:
            print("Warning: renderer height is 0")
            return
        camera.set_aspect(float(w) / float(h))

    def clear(self) -> None:
        gl.glClear(gl.GL_DEPTH_BUFFER_BIT | gl.GL_COLOR_BUFFER_BIT)
