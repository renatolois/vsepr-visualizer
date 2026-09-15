import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
from main_math import main_math
from main_chemistry_bounds import main_chemistry_bounds

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption("MoleculaeXR - Launcher")

font = pygame.font.Font(None, 24)
font_small = pygame.font.Font(None, 20)
clock = pygame.time.Clock()

camera_id_str = "0"
input_active = False

def draw_button(text, y_pos, mouse_pos):
    rect = pygame.Rect(50, y_pos, 300, 45)
    color = (0, 120, 220) if rect.collidepoint(mouse_pos) else (0, 80, 160)
    pygame.draw.rect(screen, color, rect, border_radius=6)
    
    txt_surf = font.render(text, True, (255, 255, 255))
    screen.blit(txt_surf, (rect.centerx - txt_surf.get_width() // 2, rect.centery - txt_surf.get_height() // 2))
    return rect

def run_menu():
    global camera_id_str, input_active
    selected_option = None

    while selected_option is None:
        screen.fill((25, 25, 35))
        mouse_pos = pygame.mouse.get_pos()

        lbl_cam = font_small.render("Camera ID:", True, (200, 200, 200))
        screen.blit(lbl_cam, (50, 25))

        input_rect = pygame.Rect(140, 20, 210, 32)
        box_color = (60, 60, 80) if not input_active else (80, 80, 120)
        pygame.draw.rect(screen, box_color, input_rect, border_radius=4)
        pygame.draw.rect(screen, (100, 150, 255) if input_active else (100, 100, 100), input_rect, 2, border_radius=4)

        txt_cam = font.render(camera_id_str, True, (255, 255, 255))
        screen.blit(txt_cam, (input_rect.x + 10, input_rect.y + 7))

        btn_math_rect = draw_button("Math", 90, mouse_pos)
        btn_chem_rect = draw_button("Chemistry", 150, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False

                if btn_math_rect.collidepoint(event.pos):
                    selected_option = "math"
                elif btn_chem_rect.collidepoint(event.pos):
                    selected_option = "chem"

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_BACKSPACE:
                    camera_id_str = camera_id_str[:-1]
                elif event.unicode.isdigit():
                    camera_id_str += event.unicode

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    
    try:
        cam_id = int(camera_id_str) if camera_id_str else 0
    except ValueError:
        cam_id = 0

    return selected_option, cam_id


if __name__ == "__main__":
    try:
        choice, camera_id = run_menu()

        if choice == "math":
            main_math(camera_id=camera_id)
        elif choice == "chem":
            main_chemistry_bounds(camera_id=camera_id)
    except KeyboardInterrupt:
        exit(1)
