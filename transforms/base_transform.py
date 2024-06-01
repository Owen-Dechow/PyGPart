from typing import TYPE_CHECKING
from typing import Hashable

if TYPE_CHECKING:
    from ..particle import Particle


class BaseTransform:
    @classmethod
    def apply(cls, particle: Particle): ...

    @classmethod
    def cache_key(cls, particle: Particle) -> Hashable: ...

    @staticmethod
    def reset(particle: Particle):
        particle.image = particle.original_image
