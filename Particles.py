from enum import Enum
import math
import pygame as pg
import random


class Particle(pg.sprite.Sprite):
    def __init__(
        self,
        position: pg.Vector2,
        velocity: pg.Vector2,
        image: pg.Surface,
        group: pg.sprite.Group,
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

        group.add(self)

    def step(self, gravity_x: float, gravity_y: float, dt: float):
        self.velocity.x += gravity_x * dt
        self.velocity.y += gravity_y * dt

        self.true_position.x += self.velocity.x * dt
        self.true_position.y += self.velocity.y * dt

        self.rect.center = self.true_position

        if self.transform_policy:
            self.transform_policy.apply_policy(self)


class TransformPolicy:
    class Transform(Enum):
        STRETCH = "stretch"
        POINT_DELTA = "point_delta"
        STRETCH_POINT = "roto_stretch"

    def __init__(
        self, transforms: tuple[Transform], caching: bool, preserve_image: bool
    ):
        self._transforms = tuple(transforms)
        self._chache = {}
        self._use_chache = caching
        self._preserve_image = preserve_image

    def apply_policy(self, particle: Particle):
        transform_map = {
            TransformPolicy.Transform.STRETCH: (
                TransformPolicy._apply_stretch,
                TransformPolicy._get_stretch_lossy,
            ),
            TransformPolicy.Transform.POINT_DELTA: (
                TransformPolicy._apply_direction,
                TransformPolicy._get_direction_lossy,
            ),
            TransformPolicy.Transform.STRETCH_POINT: (
                TransformPolicy._apply_rotostretch,
                TransformPolicy._get_stretch_point_lossy,
            ),
        }

        transform_methods = [TransformPolicy._reset_image]
        cache_keys = [particle.original_image]
        for tranform in self._transforms:
            transform_method, cache_key_method = transform_map[tranform]
            cache_key = cache_key_method(particle)

            transform_methods.append(transform_method)
            cache_keys.append(cache_key)

        cache_keys = tuple(cache_keys)
        if cache_keys in self._chache:
            particle.image = self._chache[cache_keys]
        else:
            for transform in transform_methods:
                transform(particle)

            self._chache[cache_keys] = particle.image

    @staticmethod
    def _apply_stretch(particle: Particle):
        particle.image = pg.transform.scale(
            particle.image, TransformPolicy._get_stretch(particle)
        )

    @staticmethod
    def _apply_direction(particle: Particle):
        particle.image = pg.transform.rotate(
            particle.image, TransformPolicy.get_direction(particle)
        )

    @staticmethod
    def _apply_rotostretch(particle: Particle):
        TransformPolicy._apply_stretch(particle)
        TransformPolicy._apply_direction(particle)

    @staticmethod
    def _get_stretch_point_lossy(particle):
        return (
            TransformPolicy._get_stretch_lossy(particle),
            TransformPolicy._get_direction_lossy(particle),
        )

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
    def _get_stretch_lossy(particle: Particle):
        x, y = TransformPolicy._get_stretch(particle)
        return round(x), round(y)

    @staticmethod
    def get_direction(particle: Particle):
        angle = math.atan2(particle.velocity.x, particle.velocity.y)
        deg = math.degrees(angle) + 180

        return deg

    @staticmethod
    def _reset_image(particle: Particle):
        particle.image = particle.original_image

    @staticmethod
    def _get_direction_lossy(particle: Particle):
        return round(TransformPolicy.get_direction(particle))


def debug_animation():
    def render_text(surface, text_lines):
        for idx, text_line in enumerate(text_lines):
            text = font.render(text_line, True, (255, 255, 255), (0, 0, 0))
            surface.blit(text, (25, (idx + 1) * 25))

    def get_delta_time():
        clock.tick()
        try:
            dt = 1 / clock.get_fps() * 30
        except ZeroDivisionError:
            dt = 1

        return dt

    def create_particle(particle_image, particle_group):
        position = pg.Vector2(pg.mouse.get_pos())
        velocity = pg.Vector2(
            (random.random() * 2 - 1) * 10, (random.random() * 2 - 1) * 10
        )

        Particle(
            position,
            velocity,
            particle_image,
            particle_group,
            cull_chance=0.1,
            transform_policy=PARTICLE_TRANSFORM_POLICY,
        )

    def update_particles(particle_group):
        for particle in particle_group:
            particle.step(0, 0.5, delta_time)
            if particle.true_position.y > 810:
                particle_group.remove(particle)

    pg.init()
    window = pg.display.set_mode((800, 800))

    clock = pg.time.Clock()
    font = pg.font.Font(None, 32)

    particle_group = pg.sprite.Group()
    particle_image = pg.Surface((20, 20), pg.SRCALPHA).convert_alpha()
    pg.draw.rect(
        particle_image,
        (255, 255, 255),
        pg.Rect(2, 2, 16, 16),
    )

    while True:
        pg.display.update()
        surface = pg.Surface(window.get_size())
        delta_time = get_delta_time()

        render_text(
            surface,
            [
                f"FPS: {clock.get_fps()}",
                f"Particles: {len(particle_group)}",
            ],
        )

        create_particle(particle_image, particle_group)
        update_particles(particle_group)

        particle_group.draw(surface)
        window.blit(surface, (0, 0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                break


if __name__ == "__main__":

    CULL_RATE = 0.1
    PARTICLE_TRANSFORM_POLICY = TransformPolicy(
        (
            # TransformPolicy.Transform.STRETCH,
            # TransformPolicy.Transform.POINT_DELTA,
            TransformPolicy.Transform.STRETCH_POINT,
        ),
        True,
        True,
    )

    debug_animation()
