from __future__ import particle
from typing import Hashable, TYPE_CHECKING
from base_transform import BaseTransform
from pygame import pg
import math


if TYPE_CHECKING:
    from .. import particle


class StretchY(BaseTransform):
    @classmethod
    def apply(cls, particle: particle.Particle):
        particle.image = pg.transform.scale(particle.image, cls._get_stretch(particle))

    @classmethod
    def cache_key(cls, particle: particle.Particle) -> Hashable:
        x, y = cls._get_stretch(particle)
        return round(x), round(y)

    @classmethod
    def _get_stretch(cls, particle: particle.Particle):
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


class PointDelta(BaseTransform):
    @classmethod
    def apply(cls, particle: particle.Particle):
        particle.image = pg.transform.rotate(
            particle.image, cls._get_point_delta(particle)
        )

    @classmethod
    def cache_key(cls, particle: particle.Particle) -> Hashable:
        return round(cls._get_point_delta(particle))

    @classmethod
    def _get_point_delta(cls, particle: particle.Particle):
        angle = math.atan2(particle.velocity.x, particle.velocity.y)
        deg = math.degrees(angle) + 180

        return deg


class ShrinkOverLife(BaseTransform):
    @classmethod
    def apply(cls, particle: particle.Particle):
        percentage = particle.age / particle.life_span
        scale = 1 - percentage
        size = particle.rect.width * scale, particle.rect.height * scale
        particle.image = pg.transform.scale(particle.image, size)

    @classmethod
    def cache_key(cls, particle: particle.Particle) -> Hashable:
        return round(cls._get_scale(particle) * 10)

    @classmethod
    def _get_scale(cls, particle: particle.Particle):
        percentage = particle.age / particle.life_span
        scale = 1 - percentage
        return scale
