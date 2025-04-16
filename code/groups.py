from settings import *

class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = pygame.Vector2()

    def draw(self, target_pos):
        self.offset.x = -(target_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(target_pos[1] - WINDOW_HEIGHT / 2)
        
        visible_sprites = []
        for sprite in self.sprites():
            if hasattr(sprite, 'rect'):
                if (abs(sprite.rect.centerx - target_pos[0]) < (WINDOW_WIDTH / 2) + 100 and
                    abs(sprite.rect.centery - target_pos[1]) < (WINDOW_HEIGHT / 2) + 100):
                    visible_sprites.append(sprite)

        ground_sprites = [sprite for sprite in visible_sprites if hasattr(sprite, 'ground')]
        for sprite in ground_sprites:
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)

        object_sprites = [sprite for sprite in visible_sprites if not hasattr(sprite, 'ground')]
        for sprite in sorted(object_sprites, key = lambda sprite: sprite.rect.centery):
            self.display_surface.blit(sprite.image, sprite.rect.topleft + self.offset)
