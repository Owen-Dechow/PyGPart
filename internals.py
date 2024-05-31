import math
import pygame as pg
import random
from typing import Callable, Hashable


class Particle(pg.sprite.Sprite):
    def __init__(
        self,
        position: pg.Vector2,
        velocity: pg.Vector2,
        image: pg.Surface,
        group: pg.sprite.Group,
        life_span: float = 10,
        cull_chance: float = 0,
        transform_policy: "TransformPolicy" = None,
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


class Transform:
    @staticmethod
    def reset(particle: Particle):
        particle.image = particle.original_image

    @staticmethod
    def stretch(particle: Particle):
        particle.image = pg.transform.scale(
            particle.image, Transform._get_stretch(particle)
        )

    @staticmethod
    def point_delta(particle: Particle):
        particle.image = pg.transform.rotate(
            particle.image, Transform._get_point_delta(particle)
        )

    @staticmethod
    def scale_over_life(particle: Particle, start: float, end: float):
        difference = end - start
        percentage = particle.age / particle.life_span
        scale = difference * percentage + start
        size = particle.rect.width * scale, particle.rect.height * scale
        particle.image = pg.transform.scale(particle.image, size)

    @staticmethod
    def get_scale_over_life_lossy(particle: Particle, granularity: float):
        return round(particle.age * granularity)

    @staticmethod
    def _get_stretch(particle: Particle):
        total_delta = abs(particle.velocity.x) + abs(particle.velocity.y)
        if total_delta == 0:
            stretch = particle.rect.height
            compress = particle.rect.width
            return

        stretch_co = min(max(1, (50 + total_delta) / 50), 1.5)
        compress_co = 2 - stretch_co

        stretch = stretch_co * particle.rect.height
        compress = compress_co * particle.rect.width

        return compress, stretch

    @staticmethod
    def get_stretch_lossy(particle: Particle):
        x, y = Transform._get_stretch(particle)
        return round(x), round(y)

    @staticmethod
    def _get_point_delta(particle: Particle):
        angle = math.atan2(particle.velocity.x, particle.velocity.y)
        deg = math.degrees(angle) + 180

        return deg

    @staticmethod
    def get_point_delta_lossy(particle: Particle):
        return round(Transform._get_point_delta(particle))


class TransformPolicy:
    def __init__(
        self,
        transform_func: Callable[[Particle], None],
        data_func: Callable[[Particle], Hashable],
        use_cache: bool = False,
        add_image_to_cache: bool = False,
    ):
        self._transform_func = transform_func
        self._data_func = data_func
        self._cache = {}
        self._use_cache = use_cache
        self._add_image_to_cache = add_image_to_cache

    def apply_policy(self, particle: Particle):
        Transform.reset(particle)
        if self._use_cache:
            self._apply_cached(particle)
        else:
            self._apply_uncached(particle)

    def _apply_cached(self, particle: Particle):
        if self._add_image_to_cache:
            cache_key = (particle.original_image, self._data_func(particle))
        else:
            cache_key = self._data_func(particle)

        if cache_key in self._cache:
            particle.image = self._cache[cache_key]
        else:
            self._transform_func(particle)
            self._cache[cache_key] = particle.image

    def _apply_uncached(self, particle: Particle):
        self._transform_func(particle)
