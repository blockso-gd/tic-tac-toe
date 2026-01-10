import pygame #PYGAME CE
import sys
import os

pygame.init()

class Slot:

    def __init__(self, x, y, w):
        w = w*.90
        self.rect = pygame.FRect(0, 0, w, w)
        self.rect.center = (x, y)
        self.surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.col = (0,0,0)
        self.state = 0 #0 is off, 1 is 0 and 2 is x

    def draw(self):
        pygame.display.get_surface().blit(self.surf, self.rect)

    def update(self, state: int):
        self.state = state
        linewidth = 20

        match self.state:
            case 1:
                self.col = (50,50,100)
                pygame.draw.circle(self.surf, self.col, (self.surf.width/2, self.surf.height/2), self.rect.w/2, linewidth)
            case 2:
                self.col = (100,50,50)
                pygame.draw.line(self.surf, self.col, (0,0), (self.surf.width, self.surf.height), linewidth)
                pygame.draw.line(self.surf, self.col, (self.surf.width,0), (0, self.surf.height), linewidth)

    def clear(self):
        self.surf.fill((0,0,0,0))
        self.state = 0

class Game:

    def __init__(self):
        screen_info = pygame.display.Info()

        self.SCREEN_WIDTH = screen_info.current_w
        self.SCREEN_HEIGHT = screen_info.current_h
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT), pygame.FULLSCREEN)
        self.Clock = pygame.time.Clock()

        self.HIGHEST_REFRESH_RATE = pygame.display.get_current_refresh_rate()
        self.currentRefreshRate = self.HIGHEST_REFRESH_RATE

        preferred_screen_axis = min(self.SCREEN_WIDTH, self.SCREEN_HEIGHT)*0.80

        self.grid = pygame.Surface((preferred_screen_axis, preferred_screen_axis), pygame.SRCALPHA)
        self.gridPos = ((self.SCREEN_WIDTH/2)-(self.grid.width/2),(self.SCREEN_HEIGHT/2)-(self.grid.height/2))
        line_width = 20
        pygame.draw.line(self.grid, (50,50,50), (self.grid.width*(1/3), 0), (self.grid.width*(1/3), self.grid.height), line_width)
        pygame.draw.line(self.grid, (50,50,50), (self.grid.width*(2/3), 0), (self.grid.width*(2/3), self.grid.height), line_width)
        pygame.draw.line(self.grid, (50,50,50), (0, self.grid.height*(1/3)), (self.grid.width, self.grid.height*(1/3)), line_width)
        pygame.draw.line(self.grid, (50,50,50), (0, self.grid.height*(2/3)), (self.grid.width, self.grid.height*(2/3)), line_width)

        self.slots = [[],[],[]]
        y = 1/6
        for row in range(3):
            x = 1/6
            for column in range(3):
                self.slots[row].append(Slot(self.gridPos[0]+x*self.grid.width, self.gridPos[1]+y*self.grid.height, self.grid.width/3))
                x += 1/3
            y += 1/3

        self.currentPlayer = True
        self.running = True
        self.movesDone = 0
        self.winner = None
        self.winLineCords = []

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

        move_audio_path = os.path.join(BASE_DIR, "move_audio")
        self.move_audios = list()

        for sound_effect in os.listdir(move_audio_path):
            self.move_audios.append(pygame.mixer.Sound(os.path.join(move_audio_path, sound_effect)))

        self.victory_font = pygame.font.Font(None, 50)
        self.victory_message = None

        self.end_audio = pygame.mixer.Sound(os.path.join(BASE_DIR, "end.mp3"))

    def checkWin(self):

        col_parent = [set(), set(), set()]
        diags = [set(), set()]

        for i in range(3):
            row = [c.state for c in self.slots[i]]
            if len(set(row)) == 1 and 0 not in row: return ("h", i, list(row)[0])
            diags[0].add(row[i])
            diags[1].add(row[2-i])

            for k in range(3):
                col_parent[k].add(row[k])

        for index, col in enumerate(col_parent):
            if len(col) == 1 and 0 not in col: return ("v", index, list(col)[0])

        for index, diag in enumerate(diags):
            if len(diag) == 1 and 0 not in diag: return ("d", index, list(diag)[0])

        if self.movesDone >= 9 and not self.winner:
            return (999,999,999)

    def slot_update(self):
        if not self.running: return

        if self.movesDone >= 5:
            win_message = self.checkWin()

            if win_message:
                self.victory_procedure(win_message)
                return

        mouse = pygame.mouse.get_just_pressed()

        for slot_f in self.slots: #slot_f is a list of slots (row)

            for  slot_i in slot_f:  #slot_i is an individual slot
                
                if slot_i.rect.collidepoint(pygame.mouse.get_pos()) and mouse[0] and slot_i.state == 0 :
                    slot_i.update(self.currentPlayer+1)

                    self.currentPlayer = not self.currentPlayer
                    self.movesDone += 1
                    self.move_audios[self.movesDone-1].play()        

    def draw_slots(self):
        for slot_f in self.slots: #slot_f is a list of slots (row)

            for  slot_i in slot_f:
                slot_i.draw()

    def victory_procedure(self, win_message):
        self.running = False
        self.winner = win_message[2]

        match self.winner:
            case 1:
                win_sign = "O"
            case 2:
                win_sign = "X"

        win_index = win_message[1]

        match win_message[0]:
            case "h":
                line_start = self.slots[win_index][0].rect.midleft#(self.gridPos[0] + win_message[1]*self.grid.width*1.6)
                line_end = self.slots[win_index][2].rect.midright

            case "v":
                line_start = self.slots[0][win_index].rect.midtop
                line_end = self.slots[2][win_index].rect.midbottom

            case "d":

                if win_index == 0:
                    line_start = self.slots[0][0].rect.topleft
                    line_end = self.slots[2][2].rect.bottomright
                elif win_index == 1:
                    line_start = self.slots[0][2].rect.topright
                    line_end = self.slots[2][0].rect.bottomleft

            case 999:
                self.victory_message = self.victory_font.render("Its a tie!", False, (50,50,50))
                pygame.mixer.stop()
                self.end_audio.play()
                return

            case _: return None

        self.winLineCords.append(line_start)
        self.winLineCords.append(line_end)
        self.victory_message = self.victory_font.render(f"{win_sign} has won! GG!", False, (50,50,50))
        pygame.mixer.stop()
        self.end_audio.play()

    def clear_grid(self):
        for slot_f in self.slots:
            for  slot_i in slot_f:
                slot_i.clear()
        self.currentPlayer = True
        self.movesDone = 0
        self.running = True
        self.winner = None
        self.winLineCords.clear()
        self.victory_message = None

    def run(self):
        while True:
            self.screen.fill((200,200,200))
            for event in pygame.event.get():

                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.clear_grid()

            self.screen.blit(self.grid, self.gridPos)

            self.slot_update()
            self.draw_slots()

            if self.winner and self.winner != 999:
                pygame.draw.line(self.screen, (230,230,230), self.winLineCords[0], self.winLineCords[1], 25)

            if self.winner:
                self.screen.blit(self.victory_message, (self.SCREEN_WIDTH/2-self.victory_message.size[0]/2, 10))

            pygame.display.update()
            self.Clock.tick(self.currentRefreshRate)
Game().run()
