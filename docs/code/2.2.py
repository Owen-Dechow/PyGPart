from PyGPart import Particle, transforms
from PygPart.transforms import TransformPolicy
import pygame as pg
import random


def create_particle(group, image):
    POSITION = pg.Vector2(400, 400)
    VELOCITY = pg.Vector2(
        (random.random() * 2 - 1) * 200,
        (random.random() * 2 - 1) * 200,
    )

    Particle(POSITION, VELOCITY, image, group, transform_policy=TRANSFORM_POLICY)


def update_particles(group, dt):
    for particle in group:
        X_GRAVITY = 0
        Y_GRAVITY = 600
        particle.step(X_GRAVITY, Y_GRAVITY, dt)


def render_text(surface, text_lines, font):
    for idx, text_line in enumerate(text_lines):
        text = font.render(text_line, True, (255, 255, 255), (0, 0, 0))
        surface.blit(text, (25, (idx + 1) * 25))


def animation():
    pg.init()
    window = pg.display.set_mode((800, 800))
    clock = pg.time.Clock()
    font = pg.font.Font(None, 32)

    group = pg.sprite.Group()
    image = pg.Surface((20, 20), pg.SRCALPHA).convert_alpha()
    pg.draw.rect(
        image,
        (255, 255, 255),
        pg.Rect(2, 2, 16, 16),
    )

    while True:
        try:
            dt = 1 / clock.get_fps()
        except ZeroDivisionError:
            dt = 1

        update_particles(group, dt)
        create_particle(group, image)
        group.draw(window)

        clock.tick()
        pg.display.update()
        window.fill((0, 0, 0))

        render_text(
            window,
            [
                f"FPS: {clock.get_fps()}",
            ],
            font,
        )

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                break


if __name__ == "__main__":
    TRANSFORM_POLICY = TransformPolicy(
        transforms.StretchY,
        transforms.PointDelta,
    )

    animation()
