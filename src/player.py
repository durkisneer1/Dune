from src.core.utils import *

if TYPE_CHECKING:
    from main import Game


class Player:
    def __init__(self, game: "Game", colliders: list[pg.Rect]):
        self.game = game
        self.colliders = colliders

        self.image = import_image("assets/paul1.png")
        self.flipped = import_image("assets/paul2.png")

        self.pos = pg.Vector2(WIN_WIDTH / 2, WIN_HEIGHT / 2)
        self.rect = self.image.get_frect(center=self.pos)
        self.direction = pg.Vector2()
        self.speed = 100
        self.right = False

    def move(self):
        self.direction.xy = 0, 0
        if self.game.keys[pg.K_a]:
            self.direction.x -= 1
            self.right = False
        if self.game.keys[pg.K_d]:
            self.direction.x += 1
            self.right = True
        if self.game.keys[pg.K_w]:
            self.direction.y -= 1
        if self.game.keys[pg.K_s]:
            self.direction.y += 1

        if self.direction.length():
            self.direction.normalize_ip()
        velocity = self.direction * self.speed * self.game.dt

        self.pos.x += velocity.x
        self.rect.centerx = self.pos.x
        self.h_collide()
        self.pos.y += velocity.y
        self.rect.centery = self.pos.y
        self.v_collide()

        self.game.camera = self.game.camera.lerp(
            self.pos - pg.Vector2(WIN_WIDTH / 2, WIN_HEIGHT / 2),
            self.game.dt * 3
        )

    def h_collide(self):
        for collider in self.colliders:
            if self.rect.colliderect(collider):
                if self.direction.x > 0:
                    self.rect.right = collider.left
                elif self.direction.x < 0:
                    self.rect.left = collider.right
                self.pos.x = self.rect.centerx

    def v_collide(self):
        for collider in self.colliders:
            if self.rect.colliderect(collider):
                if self.direction.y > 0:
                    self.rect.bottom = collider.top
                elif self.direction.y < 0:
                    self.rect.top = collider.bottom
                self.pos.y = self.rect.centery

    def draw(self):
        img = self.image if self.right else self.flipped
        self.game.screen.blit(img, self.rect.move(-self.game.camera))
