from settings import *

def load_high_score():
    with open(join('..', 'data', 'high_score.txt'), 'r') as file:
        content = file.read()
        highscore = int(content.split("=")[1])
        return highscore

def save_high_score(current_score):
    with open(join('..', 'data', 'high_score.txt'), 'w') as file:
        file.write('highscore=' + str(current_score))


class HomeScreen:
    def __init__(self, display_surface, background):
        self.high_score = load_high_score()
        self.waiting = True
        self.display_surface = display_surface
        self.background = background
        self.font = pygame.font.Font(join('..', 'images', 'Oxanium-Bold.ttf'), 40)

        # Draw homescreen
        self.display_surface.blit(background, (0, 0))
        self.display_high_score()
        pygame.display.update()


    def display_high_score(self):
        self.text_surf = self.font.render('high score = ' +str(self.high_score), True, 'gray25')
        self.text_rect = self.text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2 - 180 ,WINDOW_HEIGHT - 180))
        self.display_surface.blit(self.text_surf, self.text_rect)

    def wait(self):
        while self.waiting:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return True
                if event.type == pygame.QUIT:
                    return False