import pygame as pg
import random
from .transforms import TransformPolicy


class Particle(pg.sprite.Sprite):
    def __init__(
        self,
        position: pg.Vector2,
        velocity: pg.Vector2,
        image: pg.Surface,
        group: pg.sprite.Group,
        life_span: float = 10,
        cull_chance: float = 0,
        transform_policy: TransformPolicy = None,
    ):
        if random.random() < cull_chance:
            return

        super().__init__()
        self.image = self.original_image = image
        self.velocity = velocity
        self.true_position = position
        self.rect = self.image.get_rect(center=position)
        self.last_state = None
        self.transform_policy = transform_policy
        self.life_span = life_span
        self.age = 0
        self.group = group

        group.add(self)

    def step(self, gravity_x: float, gravity_y: float, dt: float):
        self.age += dt
        if self.age >= self.life_span:
            self.group.remove(self)
            return

        self.velocity.x += gravity_x * dt
        self.velocity.y += gravity_y * dt

        self.true_position.x += self.velocity.x * dt
        self.true_position.y += self.velocity.y * dt

        self.rect.center = self.true_position

        if self.transform_policy:
            self.transform_policy.apply_policy(self)
