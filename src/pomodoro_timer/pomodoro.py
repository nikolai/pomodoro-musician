import pygame
import time
import sys
import os
from pygame import mixer

# Инициализация pygame
pygame.init()
mixer.init()

# Константы
WORK_TIME = 25 * 60  # 25 минут в секундах
SHORT_BREAK = 5 * 60  # 5 минут в секундах
LONG_BREAK = 15 * 60  # 15 минут в секундах

# Современная цветовая палитра - минимализм
BG_COLOR = (250, 250, 252)  # Светло-серый фон
PRIMARY_COLOR = (88, 86, 214)  # Фиолетовый
PRIMARY_LIGHT = (120, 118, 242)  # Светло-фиолетовый
WORK_COLOR = (239, 71, 111)  # Красный для работы
BREAK_COLOR = (6, 214, 160)  # Бирюзовый для отдыха
TEXT_COLOR = (45, 45, 55)  # Темно-серый текст
TEXT_LIGHT = (120, 120, 135)  # Светло-серый текст
BUTTON_BG = (255, 255, 255)  # Белый фон кнопок
BUTTON_SHADOW = (220, 220, 230)  # Тень кнопок
SUCCESS_COLOR = (76, 175, 80)  # Зеленый
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Создание окна
WIDTH, HEIGHT = 500, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pomodoro Timer")

# Загрузка звуков
try:
    work_alarm_sound = mixer.Sound(os.path.join("resources", "sounds", "alarm.wav"))
except:
    print("Файл alarm.wav не найден. Создаем заглушку.")
    work_alarm_sound = None

try:
    break_alarm_sound = mixer.Sound(os.path.join("resources", "sounds", "break_alarm.wav"))
except:
    print("Файл break_alarm.wav не найден. Используем стандартный звук.")
    break_alarm_sound = None

class Settings:
    def __init__(self):
        self.work_time = 25  # минуты
        self.short_break = 5  # минуты
        self.long_break = 15  # минуты
        self.show_settings = False
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)

    def get_work_time_seconds(self):
        return self.work_time * 60

    def get_short_break_seconds(self):
        return self.short_break * 60

    def get_long_break_seconds(self):
        return self.long_break * 60

    def draw_settings(self, screen):
        if not self.show_settings:
            return None

        # Полупрозрачный фон-оверлей
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # Окно настроек (современный дизайн)
        settings_rect = pygame.Rect(50, 50, WIDTH - 100, HEIGHT - 100)

        # Тень окна
        shadow_rect = settings_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=20)

        # Основное окно
        pygame.draw.rect(screen, WHITE, settings_rect, border_radius=20)

        # Заголовок
        title = self.font.render("Настройки", True, TEXT_COLOR)
        screen.blit(title, (settings_rect.centerx - title.get_width()//2, settings_rect.y + 25))

        y_offset = settings_rect.y + 80

        # Настройка времени работы
        work_text = self.small_font.render(f"Работа: {self.work_time} мин", True, TEXT_COLOR)
        screen.blit(work_text, (settings_rect.x + 40, y_offset))

        # Кнопки для времени работы
        work_minus = pygame.Rect(settings_rect.right - 120, y_offset - 5, 45, 35)
        work_plus = pygame.Rect(settings_rect.right - 65, y_offset - 5, 45, 35)
        self.draw_setting_button(screen, work_minus, "-", WORK_COLOR)
        self.draw_setting_button(screen, work_plus, "+", WORK_COLOR)

        y_offset += 60

        # Настройка короткого перерыва
        short_text = self.small_font.render(f"Короткий перерыв: {self.short_break} мин", True, TEXT_COLOR)
        screen.blit(short_text, (settings_rect.x + 40, y_offset))

        # Кнопки для короткого перерыва
        short_minus = pygame.Rect(settings_rect.right - 120, y_offset - 5, 45, 35)
        short_plus = pygame.Rect(settings_rect.right - 65, y_offset - 5, 45, 35)
        self.draw_setting_button(screen, short_minus, "-", BREAK_COLOR)
        self.draw_setting_button(screen, short_plus, "+", BREAK_COLOR)

        y_offset += 60

        # Настройка длинного перерыва
        long_text = self.small_font.render(f"Длинный перерыв: {self.long_break} мин", True, TEXT_COLOR)
        screen.blit(long_text, (settings_rect.x + 40, y_offset))

        # Кнопки для длинного перерыва
        long_minus = pygame.Rect(settings_rect.right - 120, y_offset - 5, 45, 35)
        long_plus = pygame.Rect(settings_rect.right - 65, y_offset - 5, 45, 35)
        self.draw_setting_button(screen, long_minus, "-", PRIMARY_COLOR)
        self.draw_setting_button(screen, long_plus, "+", PRIMARY_COLOR)

        # Кнопка закрытия
        close_button = pygame.Rect(settings_rect.centerx - 60, settings_rect.bottom - 60, 120, 45)
        pygame.draw.rect(screen, PRIMARY_COLOR, close_button, border_radius=12)
        close_text = self.small_font.render("ЗАКРЫТЬ", True, WHITE)
        screen.blit(close_text, (close_button.centerx - close_text.get_width()//2, close_button.centery - close_text.get_height()//2))

        return {
            'work_minus': work_minus,
            'work_plus': work_plus,
            'short_minus': short_minus,
            'short_plus': short_plus,
            'long_minus': long_minus,
            'long_plus': long_plus,
            'close_button': close_button
        }

    def draw_setting_button(self, screen, rect, text, color):
        """Рисует кнопку настройки"""
        pygame.draw.rect(screen, color, rect, border_radius=8)
        text_surface = self.font.render(text, True, WHITE)
        screen.blit(text_surface, (rect.centerx - text_surface.get_width()//2, rect.centery - text_surface.get_height()//2))

    def handle_settings_click(self, mouse_pos, buttons):
        if not buttons:
            return False

        if buttons['work_minus'].collidepoint(mouse_pos) and self.work_time > 1:
            self.work_time -= 1
            return True
        elif buttons['work_plus'].collidepoint(mouse_pos) and self.work_time < 60:
            self.work_time += 1
            return True
        elif buttons['short_minus'].collidepoint(mouse_pos) and self.short_break > 1:
            self.short_break -= 1
            return True
        elif buttons['short_plus'].collidepoint(mouse_pos) and self.short_break < 30:
            self.short_break += 1
            return True
        elif buttons['long_minus'].collidepoint(mouse_pos) and self.long_break > 5:
            self.long_break -= 1
            return True
        elif buttons['long_plus'].collidepoint(mouse_pos) and self.long_break < 30:
            self.long_break += 1
            return True
        elif buttons['close_button'].collidepoint(mouse_pos):
            self.show_settings = False
            return True

        return False

class PomodoroTimer:
    def __init__(self, settings):
        self.settings = settings
        self.remaining_time = settings.get_work_time_seconds()
        self.is_running = False
        self.is_work_time = True
        self.session_count = 0
        # Современные шрифты
        self.time_font = pygame.font.SysFont('Arial', 72, bold=True)
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 18)
        self.button_font = pygame.font.SysFont('Arial', 16, bold=True)
        self.last_update_time = time.time()  # Добавляем временную метку

    def start(self):
        self.is_running = True
        self.last_update_time = time.time()  # Обновляем временную метку

    def pause(self):
        self.is_running = False

    def reset(self):
        self.is_running = False
        self.remaining_time = self.settings.get_work_time_seconds()
        self.is_work_time = True
        self.session_count = 0

    def toggle(self):
        self.is_running = not self.is_running

    def update(self):
        current_time = time.time()
        if self.is_running:
            # Обновляем время только если прошла至少 1 секунда
            if current_time - self.last_update_time >= 1.0:
                self.remaining_time -= 1
                self.last_update_time = current_time

                if self.remaining_time <= 0:
                    self.play_alarm()
                    self.switch_mode()

    def switch_mode(self):
        if self.is_work_time:
            self.session_count += 1
            if self.session_count % 4 == 0:
                self.remaining_time = self.settings.get_long_break_seconds()
            else:
                self.remaining_time = self.settings.get_short_break_seconds()
            self.is_work_time = False
        else:
            self.remaining_time = self.settings.get_work_time_seconds()
            self.is_work_time = True

        self.is_running = False
        self.last_update_time = time.time()  # Обновляем временную метку

    def play_alarm(self):
        if self.is_work_time:
            # Звук для завершения работы
            if work_alarm_sound:
                work_alarm_sound.play()
            else:
                print("\a")  # Системный beep
        else:
            # Весёлый звук для начала перерыва
            if break_alarm_sound:
                break_alarm_sound.play()
            else:
                # Альтернативный весёлый звук
                print("🎉 Время отдыха! 🎉")
                print("\a\a")  # Двойной beep

    def draw_stars(self, screen):
        """Рисует декоративные звёздочки на фоне"""
        import random
        random.seed(42)  # Фиксированный seed для одинакового расположения

        star_color = (180, 178, 230)  # Светло-фиолетовый цвет звёзд

        # Рисуем несколько звёздочек
        star_positions = [
            (50, 50), (100, 120), (WIDTH - 80, 70), (80, HEIGHT - 80),
            (WIDTH - 100, HEIGHT - 100), (WIDTH - 50, 150), (40, HEIGHT - 150),
            (150, 50), (WIDTH - 150, HEIGHT - 50), (250, 70)
        ]

        for pos in star_positions:
            if pos[0] < WIDTH and pos[1] < HEIGHT:
                self.draw_star(screen, pos[0], pos[1], 15, star_color)  # Увеличили размер с 8 до 15

    def draw_star(self, screen, x, y, size, color):
        """Рисует векторную звёздочку"""
        import math

        # Создаём точки для 5-конечной звезды
        points = []
        for i in range(10):
            angle = (i * 36 - 90) * math.pi / 180
            if i % 2 == 0:
                # Внешние точки
                r = size
            else:
                # Внутренние точки
                r = size * 0.4

            point_x = x + r * math.cos(angle)
            point_y = y + r * math.sin(angle)
            points.append((point_x, point_y))

        # Рисуем звезду
        if len(points) >= 3:
            pygame.draw.polygon(screen, color, points)

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def draw(self, screen):
        # Фон
        screen.fill(BG_COLOR)

        # Рисуем декоративные звёздочки на фоне
        self.draw_stars(screen)

        # Определяем цвет акцента в зависимости от режима
        accent_color = WORK_COLOR if self.is_work_time else BREAK_COLOR

        # Рисуем круговой прогресс-бар (декоративный)
        total_time = self.settings.get_work_time_seconds() if self.is_work_time else self.settings.get_short_break_seconds()
        progress = 1 - (self.remaining_time / total_time) if total_time > 0 else 0
        center = (WIDTH // 2, HEIGHT // 2 - 30)
        radius = 120

        # Фоновая окружность
        pygame.draw.circle(screen, WHITE, center, radius + 5)
        pygame.draw.circle(screen, BUTTON_SHADOW, center, radius + 5, 2)

        # Прогресс (дуга)
        if progress > 0:
            end_angle = -90 + (360 * progress)
            points = [center]
            for angle in range(-90, int(end_angle), 2):
                rad = angle * 3.14159 / 180
                x = center[0] + int(radius * -pygame.math.Vector2(0, 1).rotate(angle).x)
                y = center[1] + int(radius * -pygame.math.Vector2(0, 1).rotate(angle).y)
                points.append((x, y))
            if len(points) > 2:
                pygame.draw.polygon(screen, accent_color + (30,) if len(accent_color) == 3 else accent_color, points)

        # Внутренняя белая окружность
        pygame.draw.circle(screen, WHITE, center, radius - 8)

        # Отображение времени (большой шрифт)
        time_text = self.format_time(self.remaining_time)
        time_surface = self.time_font.render(time_text, True, TEXT_COLOR)
        time_rect = time_surface.get_rect(center=center)
        screen.blit(time_surface, time_rect)

        # Отображение режима (над временем, маленький текст)
        mode_text = "РАБОТА" if self.is_work_time else "ОТДЫХ"
        mode_surface = self.small_font.render(mode_text, True, accent_color)
        mode_rect = mode_surface.get_rect(center=(WIDTH//2, center[1] - 55))
        screen.blit(mode_surface, mode_rect)

        # Отображение сессий (под временем)
        if self.session_count > 0:
            sessions_text = f"Сессия {self.session_count}"
            sessions_surface = self.small_font.render(sessions_text, True, TEXT_LIGHT)
            sessions_rect = sessions_surface.get_rect(center=(WIDTH//2, center[1] + 55))
            screen.blit(sessions_surface, sessions_rect)

        # Кнопки внизу (современный дизайн)
        button_y = HEIGHT - 60

        # Кнопка старт/пауза
        start_button_text = "ПАУЗА" if self.is_running else "СТАРТ"
        start_button_rect = pygame.Rect(WIDTH//2 - 110, button_y, 100, 45)
        self.draw_modern_button(screen, start_button_rect, start_button_text, PRIMARY_COLOR, WHITE)

        # Кнопка сброса
        reset_button_rect = pygame.Rect(WIDTH//2 + 10, button_y, 100, 45)
        self.draw_modern_button(screen, reset_button_rect, "СБРОС", BUTTON_BG, TEXT_COLOR, border=True)

        # Кнопка настроек (в углу)
        settings_button_rect = pygame.Rect(WIDTH - 70, 20, 55, 45)
        self.draw_modern_button(screen, settings_button_rect, "SET", BUTTON_BG, TEXT_COLOR, border=True, small=True)

        # Отображаем настройки поверх всего если они открыты
        if self.settings.show_settings:
            settings_buttons = self.settings.draw_settings(screen)

        pygame.display.flip()

        # Возвращаем rect'ы кнопок для обработки кликов
        return start_button_rect, reset_button_rect, settings_button_rect

    def draw_modern_button(self, screen, rect, text, bg_color, text_color, border=False, small=False):
        """Рисует современную кнопку с тенью"""
        # Тень
        shadow_rect = rect.copy()
        shadow_rect.y += 2
        pygame.draw.rect(screen, BUTTON_SHADOW, shadow_rect, border_radius=12)

        # Основная кнопка
        pygame.draw.rect(screen, bg_color, rect, border_radius=12)

        # Граница (опционально)
        if border:
            pygame.draw.rect(screen, BUTTON_SHADOW, rect, 2, border_radius=12)

        # Текст
        font = self.small_font if small else self.button_font
        text_surface = font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

def main():
    clock = pygame.time.Clock()
    settings = Settings()
    timer = PomodoroTimer(settings)

    running = True
    while running:
        start_button_rect, reset_button_rect, settings_button_rect = timer.draw(screen)
        settings_buttons = settings.draw_settings(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    timer.toggle()
                elif event.key == pygame.K_r:
                    timer.reset()
                elif event.key == pygame.K_s:
                    settings.show_settings = not settings.show_settings
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    mouse_pos = pygame.mouse.get_pos()
                    if start_button_rect.collidepoint(mouse_pos):
                        timer.toggle()
                    elif reset_button_rect.collidepoint(mouse_pos):
                        timer.reset()
                    elif settings_button_rect.collidepoint(mouse_pos):
                        settings.show_settings = not settings.show_settings
                    elif settings_buttons and settings.handle_settings_click(mouse_pos, settings_buttons):
                        pass # Settings button handled

        if settings.show_settings:
            # If settings are shown, update settings and redraw
            settings_buttons = settings.draw_settings(screen)
        else:
            # If settings are not shown, update timer and redraw
            timer.update()

        clock.tick(60)  # Обновление с FPS 60 для плавного интерфейса

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
