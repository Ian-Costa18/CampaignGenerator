""" Program to create campaign sign """
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def generate_sign(name, position, district, party, image, output):
    sign_templates = {
        "democrat": "Assets/Demsign.png",
        "republican": "Assets/Repsign.png",
        "independant": "Assets/Indsign.png"
    }
    template = Image.open(sign_templates[party.lower()])
    img = Image.open(image)
    sign = template.copy()
    img = img.resize((2197, 3304))
    sign.paste(img, (2906, 0))

    font = ImageFont.truetype("Assets/font.ttf", 250)
    font_name = ImageFont.truetype("Assets/font.ttf", 350)
    draw = ImageDraw.Draw(sign)
    text = f"""{position}
Of
{district}"""
    name_w, name_h = draw.textsize(text, font=font_name)
    text_w, text_h = draw.multiline_textsize(text, font=font, spacing=20)
    draw.text(((2401-name_w)/2+253,1400), name, (0,0,0), font=font_name, align="center")
    draw.multiline_text(((2401-text_w)/2+253, 1750), text, (0, 0, 0), font=font, align="center", spacing=20)
    """
    # Draw first part line of text (Name)
    draw.text((500, 1400), name, (0,0,0), font=font_name)
    # Draw position
    draw.text((500, 1700), position, (0,0,0), font=font)
    # Draw "of"
    draw.text((750, 1900), "Of", (0,0,0), font=font)
    # Draw district
    draw.text((500, 2100), district, (0,0,0), font=font)"""


    sign.save(output, quality=95)


if __name__ == "__main__":
    generate_sign("Harambe", "President", "The US", "dout.png", "Independant", "doutput.png")