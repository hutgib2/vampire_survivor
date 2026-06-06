from game.settings import *
from game.vampire_survivor import Game

def load_high_score():
    with open(join('assets', 'data', 'high_score.txt'), 'r') as file:
        content = file.read()
        highscore = int(content.split("=")[1])
        return highscore

def save_high_score(current_score):
    with open(join('assets', 'data', 'high_score.txt'), 'w') as file:
        file.write('highscore=' + str(current_score))


class HomeScreen:
    def __init__(self):
        self.home_screen_image = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'home.png')), (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.game_over_screen = pygame.transform.scale(pygame.image.load(join('assets', 'images', 'game_over.png')), (WINDOW_WIDTH, WINDOW_HEIGHT))
        # self.high_score = load_high_score()
        self.running = True
        self.background = self.home_screen_image
        self.font = pygame.font.Font(join('assets', 'images', 'Oxanium-Bold.ttf'), 40)
        self.pending_game = None
        
        # Draw homescreen
        screen.blit(self.background, (0, 0))
        # self.display_high_score()
        pygame.display.update()


    # def display_high_score(self):
    #     self.text_surf = self.font.render('high score = ' +str(self.high_score), True, 'gray25')
    #     self.text_rect = self.text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2 - 180 ,WINDOW_HEIGHT - 180))
    #     screen.blit(self.text_surf, self.text_rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.pending_game = Game()
            if event.type == pygame.QUIT:
                self.running = False

    async def run(self):
        print('RUNING HOMESCREEN')

        while self.running:
            self.handle_events()
            screen.blit(self.background, (0, 0))
            pygame.display.update()
            await asyncio.sleep(0)

            if self.pending_game:
                print('RUNING GAME')
                await self.pending_game.run()
                self.pending_game = None
                self.background = self.game_over_screen