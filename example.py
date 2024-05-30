import random
from particles import Particle, Transform, TransformPolicy
import pygame as pg


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
            cull_chance=CULL_RATE,
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

    def transform_policy_transform(p):
        Transform.stretch(p)
        Transform.point_delta(p)

    def transform_policy_data_func(p):
        return (Transform.get_stretch_lossy(p), Transform.get_point_delta_lossy(p))

    CULL_RATE = 0.1
    PARTICLE_TRANSFORM_POLICY = TransformPolicy(
        transform_policy_transform,
        transform_policy_data_func,
        use_cache=True,
        add_image_to_cache=False,
    )

    debug_animation()
