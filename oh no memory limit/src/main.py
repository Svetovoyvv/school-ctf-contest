import os
from PIL import Image, ImageDraw, ImageFont
import sys

def generate_image(output_path: str):
    flag = os.getenv('FLAG', 'TEST_FLAG')
    text = f"Да, конечно я скажу тебе свой секрет\n\nТолько не рассказывай никому! Вот:\n\n{flag}"

    width, height = 800, 400
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("/usr/share/fonts/ttf-dejavu/DejaVuSans.ttf", 24)
    except OSError:
        print("Warning: DejaVuSans.ttf not found. Text might not render correctly.")
        font = ImageFont.load_default()

    draw.text((50, 50), text, fill='black', font=font)

    image.save(output_path)
    print(f"Saved {output_path}")

if __name__ == "__main__":
    generate_image(sys.argv[1])


