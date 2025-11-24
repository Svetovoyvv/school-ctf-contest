import os
from pydub import AudioSegment

MORSE_TABLE = {
    "A": ".-",    "B": "-...",  "C": "-.-.",  "D": "-..",
    "E": ".",     "F": "..-.",  "G": "--.",   "H": "....",
    "I": "..",    "J": ".---",  "K": "-.-",   "L": ".-..",
    "M": "--",    "N": "-.",    "O": "---",   "P": ".--.",
    "Q": "--.-",  "R": ".-.",   "S": "...",   "T": "-",
    "U": "..-",   "V": "...-",  "W": ".--",   "X": "-..-",
    "Y": "-.--",  "Z": "--..",

    "0": "-----", "1": ".----", "2": "..---", "3": "...--",
    "4": "....-", "5": ".....", "6": "-....", "7": "--...",
    "8": "---..", "9": "----.",

    "_": "..--.-"
}

def text_to_morse_binary(text: str) -> str:
    """Перевод строки в двоичный Морзе: . → 0, - → 1"""
    result = []

    for ch in text.upper():
        if ch in MORSE_TABLE:
            morse = MORSE_TABLE[ch]
            binary = morse.replace('.', '0').replace('-', '1')
            result.append(binary)
        else:
            raise ValueError(f"Нет морзе-кода для символа: {ch}")

    return " ".join(result)


def binary_to_audio(binary_string, zero_file="zero.mp3", one_file="one.mp3",
                    pause_ms=150, output_file="output.mp3"):

    audio_zero = AudioSegment.from_file(zero_file)
    audio_one = AudioSegment.from_file(one_file)
    pause = AudioSegment.silent(duration=pause_ms)

    result = AudioSegment.silent(duration=0)

    for char in binary_string:
        if char == '0':
            result += audio_zero + pause
        elif char == '1':
            result += audio_one + pause
        elif char == ' ':
            result += pause * 4
        else:
            print(f"Пропускаю неизвестный символ: {char}")

    result.export(output_file, format="mp3")
    print(f"Audio saved to {output_file}")


if __name__ == "__main__":
    flag = os.getenv("FLAG")

    if not flag:
        raise RuntimeError("Переменная окружения FLAG не установлена!")

    assert flag.startswith("ctf{"), "FLAG must start with 'ctf{'"
    assert flag.endswith("}"), "FLAG must end with '}'"
    flag = flag.removesuffix("}").removeprefix("ctf{")
    assert flag.isupper(), "FLAG must be uppercase"

    binary_flag = text_to_morse_binary(flag)
    print("Морзе → бинарно:")
    print(binary_flag)

    binary_to_audio(binary_flag, output_file="output/flag.mp3")
