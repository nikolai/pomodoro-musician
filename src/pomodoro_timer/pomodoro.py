import pygame
import time
import sys
import os
import io
import wave
import struct
from pygame import mixer

# Инициализация pygame
pygame.init()
mixer.init()

# Загрузка и установка иконки окна (ДО создания окна!)
def load_icon():
    """Загружает иконку приложения для окна"""
    icon_paths = []
    
    # Проверяем пути относительно исполняемого файла (для PyInstaller)
    if getattr(sys, 'frozen', False):
        # Запущено как собранное приложение
        base_path = sys._MEIPASS
        icon_paths.append(os.path.join(base_path, "resources", "icon.png"))
    else:
        # Запущено из исходников - проверяем несколько возможных путей
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        
        icon_paths.extend([
            os.path.join(project_root, "resources", "icon.png"),
            os.path.join(script_dir, "..", "..", "resources", "icon.png"),
            os.path.join("resources", "icon.png"),
        ])
    
    for path in icon_paths:
        if os.path.exists(path):
            try:
                # Загружаем PNG (icns pygame не поддерживает напрямую)
                if path.endswith('.png'):
                    icon = pygame.image.load(path)
                    # Конвертируем в формат, подходящий для иконки (32x32 или 64x64)
                    icon = pygame.transform.smoothscale(icon, (64, 64))
                    return icon
            except Exception as e:
                print(f"Не удалось загрузить иконку из {path}: {e}")
                continue
    
    # Если иконка не найдена, выводим предупреждение
    if not getattr(sys, 'frozen', False):
        print("⚠️  Иконка не найдена. Запустите scripts/create_icon.py для создания иконки.")
    return None

# Устанавливаем иконку ПЕРЕД созданием окна (важно!)
app_icon = load_icon()
if app_icon:
    pygame.display.set_icon(app_icon)

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
WIDTH, HEIGHT = 500, 560
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

# Создание звука метронома в памяти (короткий «тик» ~80мс)
def create_tick_sound():
    try:
        sample_rate = 44100
        duration = 0.08  # короткий щелчок (~80 мс)
        num_samples = int(sample_rate * duration)

        # Формируем WAV в памяти
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)          # моно
            wav_file.setsampwidth(2)          # 16-бит PCM
            wav_file.setframerate(sample_rate)

            import random
            frames = bytearray()

            # Параметры составляющих клика
            # Короткая высокочастотная атака (похожа на механический щелчок)
            transient_freq = 3500.0
            transient_tau = 0.004   # 4 мс экспон. затухание
            # Низкая «деревянная» составляющая
            body_freq = 650.0
            body_tau = 0.018        # 18 мс
            # Шумовая составляющая (узкий щелчок с затуханием)
            noise_tau = 0.010       # 10 мс

            for i in range(num_samples):
                t = i / sample_rate

                # Экспоненциальные огибающие
                env_transient = math.exp(-t / transient_tau)
                env_body = math.exp(-t / body_tau)
                env_noise = math.exp(-t / noise_tau)

                # Компоненты сигнала
                transient = math.sin(2 * math.pi * transient_freq * t) * env_transient
                body = math.sin(2 * math.pi * body_freq * t) * env_body
                noise = (random.random() * 2 - 1) * env_noise

                # Смешиваем компоненты для «часового тика»
                sample = 0.55 * transient + 0.25 * body + 0.20 * noise

                # Ограничение и упаковка
                val = max(-1.0, min(1.0, sample * 0.7))
                frames += struct.pack('<h', int(val * 32767))

            wav_file.writeframes(frames)

        buffer.seek(0)
        snd = mixer.Sound(file=buffer)
        snd.set_volume(0.22)  # мягкий, но читаемый уровень
        return snd
    except Exception:
        return None

# math понадобится для генерации тика
import math
tick_sound = create_tick_sound()

class Settings:
    def __init__(self):
        self.work_time = 25  # минуты
        self.short_break = 5  # минуты
        self.long_break = 15  # минуты
        self.metronome_enabled = True
        self.metronome_interval = 1.0  # секунды между тиками
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

        # Окно настроек (современный дизайн) — увеличено для видимости метронома
        settings_rect = pygame.Rect(40, 30, WIDTH - 80, HEIGHT - 60)

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

        y_offset += 60

        # Настройки метронома
        metro_status = "ВКЛ" if self.metronome_enabled else "ВЫКЛ"
        metro_text = self.small_font.render(f"Метроном: {metro_status}", True, TEXT_COLOR)
        screen.blit(metro_text, (settings_rect.x + 40, y_offset))

        # Кнопка переключателя метронома
        metro_toggle = pygame.Rect(settings_rect.right - 200, y_offset - 5, 80, 35)
        self.draw_setting_button(screen, metro_toggle, metro_status, PRIMARY_COLOR if self.metronome_enabled else BUTTON_SHADOW)

        # Период тика (в секундах)
        y_offset += 45
        interval_display = f"Период тика: {self.metronome_interval:.1f} c"
        interval_text = self.small_font.render(interval_display, True, TEXT_COLOR)
        screen.blit(interval_text, (settings_rect.x + 40, y_offset))

        interval_minus = pygame.Rect(settings_rect.right - 120, y_offset - 5, 45, 35)
        interval_plus = pygame.Rect(settings_rect.right - 65, y_offset - 5, 45, 35)
        self.draw_setting_button(screen, interval_minus, "-", PRIMARY_COLOR)
        self.draw_setting_button(screen, interval_plus, "+", PRIMARY_COLOR)

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
            'metro_toggle': metro_toggle,
            'interval_minus': interval_minus,
            'interval_plus': interval_plus,
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
        elif 'metro_toggle' in buttons and buttons['metro_toggle'].collidepoint(mouse_pos):
            self.metronome_enabled = not self.metronome_enabled
            return True
        elif 'interval_minus' in buttons and buttons['interval_minus'].collidepoint(mouse_pos):
            self.metronome_interval = max(0.3, round(self.metronome_interval - 0.1, 1))
            return True
        elif 'interval_plus' in buttons and buttons['interval_plus'].collidepoint(mouse_pos):
            self.metronome_interval = min(2.0, round(self.metronome_interval + 0.1, 1))
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
        self.last_metronome_tick_time = time.time()
        # Анимация фоновых нот
        self._init_background_notes()
        self._last_bg_ticks = pygame.time.get_ticks()

    def start(self):
        self.is_running = True
        now = time.time()
        self.last_update_time = now  # Обновляем временную метку
        self.last_metronome_tick_time = now

    def pause(self):
        self.is_running = False

    def reset(self):
        self.is_running = False
        self.remaining_time = self.settings.get_work_time_seconds()
        self.is_work_time = True
        self.session_count = 0
        self.last_metronome_tick_time = time.time()

    def toggle(self):
        self.is_running = not self.is_running
        if self.is_running:
            self.last_metronome_tick_time = time.time()

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

            # Звук метронома во время работы
            if self.is_work_time and self.settings.metronome_enabled and tick_sound:
                if current_time - self.last_metronome_tick_time >= self.settings.metronome_interval - 1e-6:
                    tick_sound.play()
                    self.last_metronome_tick_time = current_time
        # Обновляем анимацию фоновых нот
        now_ticks = pygame.time.get_ticks()
        dt_ms = max(1, now_ticks - self._last_bg_ticks)
        self._last_bg_ticks = now_ticks
        self._update_background_notes(dt_ms / 1000.0)

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
        now = time.time()  # Обновляем временную метку
        self.last_update_time = now
        self.last_metronome_tick_time = now

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

    def _init_background_notes(self):
        """Создает список фоновых нот с позициями и скоростями"""
        import random
        self._bg_colors = [
            (239, 71, 111, 70),
            (6, 214, 160, 70),
            (88, 86, 214, 60),
            (255, 180, 0, 60),
            (0, 150, 255, 60),
        ]
        self._bg_notes = []
        # Крупные
        for _ in range(8):
            self._bg_notes.append({
                'x': random.uniform(30, WIDTH - 30),
                'y': random.uniform(30, HEIGHT - 30),
                'size': random.uniform(26, 42),
                'color': random.choice(self._bg_colors),
                'vx': random.uniform(-15, 15) / 100.0,  # пикс/кадр ~ медленно
                'vy': random.uniform(-10, 10) / 100.0,
            })
        # Мелкие
        for _ in range(18):
            self._bg_notes.append({
                'x': random.uniform(20, WIDTH - 20),
                'y': random.uniform(20, HEIGHT - 20),
                'size': random.uniform(12, 20),
                'color': random.choice(self._bg_colors),
                'vx': random.uniform(-20, 20) / 100.0,
                'vy': random.uniform(-15, 15) / 100.0,
            })

    def _update_background_notes(self, dt):
        """Обновляет позиции нот; мягкое движение и обёртка по краям"""
        speed_scale = 12.0  # базовый множитель скорости (px/сек)
        for n in self._bg_notes:
            n['x'] += n['vx'] * speed_scale * dt
            n['y'] += n['vy'] * speed_scale * dt
            # Обёртка
            if n['x'] < -40: n['x'] = WIDTH + 40
            if n['x'] > WIDTH + 40: n['x'] = -40
            if n['y'] < -40: n['y'] = HEIGHT + 40
            if n['y'] > HEIGHT + 40: n['y'] = -40

    def draw_stars(self, screen):
        """Рендерит фоновые ноты с альфой"""
        bg = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for n in self._bg_notes:
            self.draw_note(bg, n['x'], n['y'], n['size'], n['color'])
        screen.blit(bg, (0, 0))

    def draw_violin_key(self, screen, x, y, size, color):
        """Рисует скрипичный ключ (treble clef)"""
        import math
        
        line_width = 2
        
        # Рисуем скрипичный ключ через серию точек, образующих изогнутую линию
        points = []
        
        # Нижняя часть (хвост)
        for i in range(10):
            t = i / 9.0
            px = x - size * 0.2 * (1 - t)
            py = y + size * 0.8 + size * 0.4 * t
            points.append((px, py))
        
        # Подъём вверх
        for i in range(8):
            t = i / 7.0
            angle = math.pi * 0.5 * (1 - t)
            px = x + size * 0.3 * math.cos(angle)
            py = y + size * 0.5 - size * 0.3 * math.sin(angle)
            points.append((px, py))
        
        # Верхняя петля (правая часть)
        for i in range(12):
            t = i / 11.0
            angle = math.pi * 0.3 + math.pi * 1.2 * t
            px = x + size * 0.4 * math.cos(angle)
            py = y - size * 0.2 + size * 0.5 * math.sin(angle)
            points.append((px, py))
        
        # Средняя часть и нижняя петля
        for i in range(15):
            t = i / 14.0
            angle = math.pi * 1.5 + math.pi * 1.3 * (1 - t)
            px = x + size * 0.35 * math.cos(angle)
            py = y + size * 0.2 + size * 0.4 * math.sin(angle)
            points.append((px, py))
        
        # Рисуем линию через все точки
        for i in range(len(points) - 1):
            pygame.draw.line(screen, color, points[i], points[i + 1], line_width)

    def draw_note(self, screen, x, y, size, color):
        """Рисует музыкальную ноту. Стебель привязан к эллипсу, чтобы не расходился."""
        # Приводим координаты к int один раз, чтобы линия и эллипс совпадали по пикселям
        rect_x = int(round(x - size * 0.3))
        rect_y = int(round(y - size * 0.2))
        rect_w = int(round(size * 0.6))
        rect_h = int(round(size * 0.4))

        note_rect = pygame.Rect(rect_x, rect_y, rect_w, rect_h)
        pygame.draw.ellipse(screen, color, note_rect)

        # Стебель: от правого края эллипса вверх
        stem_width = 2
        stem_height = int(round(size * 0.8))
        stem_x = note_rect.right - 1  # правая граница эллипса
        stem_y_top = note_rect.top
        pygame.draw.line(screen, color, (stem_x, stem_y_top), (stem_x, stem_y_top - stem_height), stem_width)

    def format_time(self, seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def draw(self, screen):
        # Фон
        screen.fill(BG_COLOR)

        # Рисуем декоративные музыкальные ноты на фоне
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
