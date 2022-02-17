import pygame
import sys
import jeu
from button import Button

pygame.init()

SCREEN = pygame.display.set_mode((1500, 600))
pygame.display.set_caption("Menu")

BG = pygame.image.load("sprites/BackgroundMenu.png")


def get_font(size):
    return pygame.font.Font("Font/Retro.ttf", size)


def play():
    jeu.main()


def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(750, 100))

        PLAY_BUTTON = Button(image=pygame.image.load("sprites/Play Rect.png"), pos=(750, 250), text_input="PLAY",
                             font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("sprites/Quit Rect.png"), pos=(750, 450), text_input="QUIT",
                             font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


main_menu()
