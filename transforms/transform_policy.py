from __future__ import particle
from typing import TYPE_CHECKING
from base_transform import BaseTransform


if TYPE_CHECKING:
    from .. import particle


class TransformPolicy:
    def __init__(
        self,
        *transforms: BaseTransform,
        use_cache: bool = False,
        add_image_to_cache: bool = False,
    ):
        self._transforms = tuple(transforms)
        self._cache = {}
        self._use_cache = use_cache
        self._add_image_to_cache = add_image_to_cache

    def apply_policy(self, particle: particle.Particle):
        BaseTransform.reset(particle)
        if self._use_cache:
            self._apply_cached(particle)
        else:
            self._apply_uncached(particle)

    def _apply_cached(self, particle: particle.Particle):
        cache_key_generator = (x.cache_key(particle) for x in self._transforms)

        if self._add_image_to_cache:
            cache_key = (particle.original_image, tuple(cache_key_generator))
        else:
            cache_key = tuple(cache_key_generator)

        if cache_key in self._cache:
            particle.image = self._cache[cache_key]

        else:
            for transform in self._transforms:
                transform.apply(particle)

            self._cache[cache_key] = particle.image

    def _apply_uncached(self, particle: particle.Particle):
        for transform in self._transforms:
            transform.apply(particle)
