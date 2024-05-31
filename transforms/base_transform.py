from typing import Hashable
from __future__ import particles


class BaseTransform:
    @classmethod
    def apply(cls, particle: particles.Particle): ...

    @classmethod
    def cache_key(cls, particle: particles.Particle) -> Hashable: ...

    @staticmethod
    def reset(particle: particles.Particle):
        particle.image = particle.original_image
