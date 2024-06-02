from typing import Hashable


class BaseTransform:
    @classmethod
    def apply(cls, particle): ...

    @classmethod
    def cache_key(cls, particle) -> Hashable: ...

    @staticmethod
    def reset(particle):
        particle.image = particle.original_image
