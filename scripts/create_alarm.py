import wave
import math
import struct

def create_alarm_sound():
    # Параметры звука
    sample_rate = 44100  # Частота дискретизации
    duration = 1.0  # Длительность звука в секундах
    frequency = 880  # Частота звука (A5)

    # Создание данных для звука
    num_samples = int(sample_rate * duration)
    sound_data = []

    for i in range(num_samples):
        # Синусоидальный сигнал
        sample = math.sin(2 * math.pi * frequency * i / sample_rate)
        # Добавляем небольшую амплитудную модуляцию для более интересного звука
        amplitude = 0.5 * (1 + math.sin(2 * math.pi * 2 * i / sample_rate))
        sample *= amplitude

        # Конвертируем в 16-битный PCM
        sample = int(sample * 32767)
        sound_data.append(sample)

    # Создание WAV файла
    with wave.open('alarm.wav', 'w') as wav_file:
        wav_file.setnchannels(1)  # Моно
        wav_file.setsampwidth(2)  # 16 бит
        wav_file.setframerate(sample_rate)

        # Конвертируем данные в байты
        bytes_data = b''
        for sample in sound_data:
            bytes_data += struct.pack('<h', sample)  # Little-endian 16-bit

        wav_file.writeframes(bytes_data)

    print("Файл alarm.wav успешно создан!")

if __name__ == "__main__":
    create_alarm_sound()
