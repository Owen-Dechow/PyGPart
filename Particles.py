import pygame as pg
import math
import random


class Particle(pg.sprite.Sprite):
    roto_stretch_cache = {}

    def __init__(
        self,
        position: pg.Vector2,
        velocity: pg.Vector2,
        image: pg.Surface,
        group: pg.sprite.Group,
        cache_tag: str = None,
        cull_chance: float = 0,
    ):
        if random.random() < cull_chance:
            return

        super().__init__()
        self.image = self.original_image = image
        self.velocity = velocity
        self.true_position = position
        self.rect = self.image.get_rect(center=position)
        self.cache_tag = cache_tag
        self.last_state = None

        group.add(self)
        if cache_tag not in Particle.roto_stretch_cache:
            Particle.roto_stretch_cache[cache_tag] = {}

    def step(
        self,
        gravity_x: float,
        gravity_y: float,
        dt: float,
    ):
        self.velocity.x += gravity_x * dt
        self.velocity.y += gravity_y * dt

        self.true_position.x += self.velocity.x * dt
        self.true_position.y += self.velocity.y * dt

        self.rect.center = self.true_position

    def get_stretch(self):
        total_delta = abs(self.velocity.x) + abs(self.velocity.y)
        if total_delta == 0:
            stretch = self.rect.height
            compress = self.rect.width
            return

        stretch_co = min(max(1, (50 + total_delta) / 50), 1.5)
        compress_co = 2 - stretch_co

        stretch = stretch_co * self.rect.height
        compress = compress_co * self.rect.width

        return compress, stretch

    def get_direction(self):
        angle = math.atan2(self.velocity.x, self.velocity.y)
        deg = math.degrees(angle) + 180

        return deg

    def get_lossy_state(self):
        angle = round(self.get_direction() * 0.5)
        compress_ex, stretch_ex = self.get_stretch()
        compress, stretch = round(compress_ex * 0.5), round(stretch_ex * 0.5)
        return (angle, compress, stretch)

    def apply_stretch(self):
        self.image = pg.transform.scale(self.image, self.get_stretch())

    def apply_direction(self):
        self.image = pg.transform.rotate(self.image, self.get_direction())

    def apply_roto_stretch(self, use_cache=False, maintain_lossy=False):
        if maintain_lossy:
            state = self.get_lossy_state()
            if self.last_state == state:
                return
            else:
                self.last_state = state

        self.reset_image()

        if use_cache:
            key = self.get_lossy_state()
            if key in Particle.roto_stretch_cache:
                self.image = Particle.roto_stretch_cache[key]
                return

        self.apply_stretch()
        self.apply_direction()

        if use_cache:
            Particle.roto_stretch_cache[key] = self.image

    def reset_image(self):
        self.image = self.original_image


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

        Particle(position, velocity, particle_image, particle_group, cull_chance=0.1)

    def update_particles(particle_group):
        for particle in particle_group:
            particle.step(0, 0.5, delta_time)
            match PARTICAL_TRANSFORM:
                case ParticalTransforms.ROTO_STRETCH_LOSSY_UPDATE_CHACHE:
                    particle.apply_roto_stretch(use_cache=True, maintain_lossy=True)
                case ParticalTransforms.ROTO_STRETCH_LOSSY_UPDATE:
                    particle.apply_roto_stretch(use_cache=False, maintain_lossy=True)
                case ParticalTransforms.ROTO_STRETCH_CHACHE:
                    particle.apply_roto_stretch(use_cache=True, maintain_lossy=False)
                case ParticalTransforms.ROTO_STRETCH:
                    particle.apply_roto_stretch(use_cache=False, maintain_lossy=False)
                case ParticalTransforms.ROTO:
                    particle.reset()
                    particle.apply_roto()
                case ParticalTransforms.STRETCH:
                    particle.reset()
                    particle.apply_stretch()
                case ParticalTransforms.NORMAL:
                    ...
            if particle.rect.y > 810:
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

    class ParticalTransforms:
        ROTO_STRETCH_LOSSY_UPDATE_CHACHE = 1
        ROTO_STRETCH_CHACHE = 2
        ROTO_STRETCH_LOSSY_UPDATE = 3
        ROTO_STRETCH = 4
        ROTO = 5
        STRETCH = 6
        NORMAL = 7

    CULL_RATE = 0.1
    PARTICAL_TRANSFORM = ParticalTransforms.ROTO_STRETCH_LOSSY_UPDATE_CHACHE

    debug_animation()
