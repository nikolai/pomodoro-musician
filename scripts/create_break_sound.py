import wave
import math
import struct

def create_break_sound():
    # Параметры звука - весёлая мелодия
    sample_rate = 44100
    duration = 2.0  # Немного длиннее для мелодии

    # Создаем простую мелодию (мажорное трезвучие)
    frequencies = [523.25, 659.25, 783.99]  # C5, E5, G5

    num_samples = int(sample_rate * duration)
    sound_data = []

    # Делим время на три части для каждой ноты
    note_duration = num_samples // 3

    for note_idx in range(3):
        frequency = frequencies[note_idx]
        start_sample = note_idx * note_duration
        end_sample = start_sample + note_duration

        for i in range(start_sample, end_sample):
            if i < num_samples:
                # Синусоидальный сигнал с плавным затуханием
                sample = math.sin(2 * math.pi * frequency * i / sample_rate)

                # Плавное затухание в конце каждой ноты
                note_progress = (i - start_sample) / note_duration
                if note_progress > 0.8:  # Затухание последних 20%
                    amplitude = 1.0 - (note_progress - 0.8) * 5
                else:
                    amplitude = 1.0

                sample *= amplitude * 0.7  # Общая громкость
                sample = int(sample * 32767)
                sound_data.append(sample)

    # Создание WAV файла
    with wave.open('break_alarm.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        bytes_data = b''
        for sample in sound_data:
            bytes_data += struct.pack('<h', sample)

        wav_file.writeframes(bytes_data)

    print("Файл break_alarm.wav успешно создан!")

if __name__ == "__main__":
    create_break_sound()
