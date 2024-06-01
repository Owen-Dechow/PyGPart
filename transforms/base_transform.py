from __future__ import particle
from typing import Hashable, TYPE_CHECKING

if TYPE_CHECKING:
    from .. import particle


class BaseTransform:
    @classmethod
    def apply(cls, particle: particle.Particle): ...

    @classmethod
    def cache_key(cls, particle: particle.Particle) -> Hashable: ...

    @staticmethod
    def reset(particle: particle.Particle):
        particle.image = particle.original_image
