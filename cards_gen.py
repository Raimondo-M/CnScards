import pandas as pd
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageColor

from collections import defaultdict

# Define a default color
default_color = (0, 0, 0)

# Create a defaultdict for colors
COLORS = defaultdict(lambda: default_color, {
    'Might': (163, 34, 11), 'Red': (163, 34, 11),
    'Agility': (36, 150, 141), 'Green': (36, 150, 141),
    'Instinct': (83, 20, 122), 'Purple': (83, 20, 122),
    'Fate': (227, 179, 23), 'Yellow': (227, 179, 23),
    'Blue': (15, 82, 186),
    'Loot': (102, 37, 11), '': (174, 16, 6), '-': (0, 0, 0)
})

# Fonts
FONT_REGULAR =      'fonts/Montserrat-Regular.ttf'
FONT_BOLD =         'fonts/Montserrat-Bold.ttf'
FONT_ITALIC =       'fonts/Montserrat-Italic.ttf'
FONT_NUSALIVER =    'fonts/nusaliver.ttf'

# Define fonts
fonts = {
    "regular":      ImageFont.truetype(FONT_REGULAR, 15),
    "req":          ImageFont.truetype(FONT_BOLD, 11),
    "tag":          ImageFont.truetype(FONT_ITALIC, 11),
    "italic":       ImageFont.truetype(FONT_ITALIC, 14),
    "title":        ImageFont.truetype(FONT_NUSALIVER, 20),
    "pts":          ImageFont.truetype(FONT_NUSALIVER, 32),
    "icon":         ImageFont.truetype(FONT_NUSALIVER, 40),
    "icon_small":   ImageFont.truetype(FONT_NUSALIVER, 20),
    "icon_sub":     ImageFont.truetype(FONT_NUSALIVER, 10)
}

# Load icons
icons = {
    "d6":   Image.open("icons/dice-d6-stroke44.png"),
    "d20":  Image.open("icons/dice-d20-stroke44.png"),
    "null": Image.new("RGBA", (32,32), (255, 255, 255, 0))
}

# Paths
CARDS_CSV = 'CnS_cards.csv'
PICS_FOLDER = 'pics'
CARDS_FOLDER = 'cards'
TEMPLATE_IMAGE = Image.open("templates/template_inca.png")
TEMPLATE_IMAGE_DAMAGE = Image.open("templates/CardTemplate_Damage.jpg")

def read_cards_data(file_path):
    """
    Reads card data from a CSV file.

    Args:
    file_path (str): Path to the CSV file.

    Returns:
    DataFrame: Pandas DataFrame containing card data.
    """
    try:
        return pd.read_csv(file_path, delimiter=',')
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        exit(1)

def wrap_text(text, font, max_width):
    """
    Wraps text to fit within a specified width, taking into account explicit new lines.

    Args:
    text (str): Text to wrap.
    font (ImageFont): Font of the text.
    max_width (int): Maximum width in pixels.

    Returns:
    str: Wrapped text.
    """
    def wrap_single_line(line, font, max_width):
        words = line.split()
        lines = []
        current_line = ''
        current_width = 0

        for word in words:
            # Create a dummy image to get the bounding box
            dummy_image = Image.new('RGB', (1, 1))
            draw = ImageDraw.Draw(dummy_image)
            word_bbox = draw.textbbox((0, 0), word, font=font)
            word_width = word_bbox[2] - word_bbox[0]

            if current_width + word_width > max_width:
                lines.append(current_line.rstrip())
                current_line = ''
                current_width = 0

            current_line += word + ' '
            current_width += word_width + draw.textbbox((0, 0), ' ', font=font)[2]

        lines.append(current_line.rstrip())
        return lines

    # Split the text into lines based on explicit new lines
    original_lines = text.split('\\n')
    wrapped_lines = []

    for line in original_lines:
        wrapped_lines.extend(wrap_single_line(line, font, max_width))

    return '\n'.join(wrapped_lines)

def colorise_icon(icon, color):
    """
    Colorises an icon by blending the specified color with the grayscale value of each pixel.

    Args:
    icon (Image): Icon image to colorise.
    color (tuple): RGB color tuple to blend with.

    Returns:
    Image: Colorised icon.
    """
    # Convert the icon to RGBA format
    icon = icon.convert("RGBA")

    # Loop through all the pixels in the image
    for x in range(icon.width):
        for y in range(icon.height):
            # Get the RGBA value of the current pixel
            r, g, b, a = icon.getpixel((x, y))

            # Calculate the grayscale intensity
            grayscale = int(0.299 * r + 0.587 * g + 0.114 * b)

            # Calculate blending percentage based on the grayscale intensity
            blending_percentage = 1 - grayscale / 255

            # Blend the color with the grayscale value
            new_color = (
                int(color[0] * blending_percentage + r * (1 - blending_percentage)),
                int(color[1] * blending_percentage + g * (1 - blending_percentage)),
                int(color[2] * blending_percentage + b * (1 - blending_percentage)),
                a
            )

            # Set the new color to the pixel
            icon.putpixel((x, y), new_color)

    return icon




def add_text(image, text, font, color, pos='center'):
    # Create a draw object to draw on the image
    draw = ImageDraw.Draw(image)
    font_size = 24
    width, height = draw._image.size

    # Calculate text width and height using getbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    while text_width > width or text_height > height:
        font_size -= 1
        font = font.font_variant(size=font_size)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
    # Calculate the position to center the text
    if pos == 'bottom':
        text_y = (height - text_height) - 2
    else:  # center by default
        text_y = (height - text_height) / 2 - 1
    text_x = (width - text_width) / 2

    # Draw the text in the specified position
    for offset_x, offset_y in [(0, 2), (2, 0), (0, -2), (-2, 0)]:
        draw.text((text_x + offset_x, text_y + offset_y), text, font=font, fill=(255, 255, 255, 255))

    draw.text((text_x, text_y), text, color, font=font)


def add_text_with_shadow(draw, text, font, position, fill_color, shadow_color):
    # Add shadow
    for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
        shadow_position = (position[0] + offset[0], position[1] + offset[1])
        draw.text(shadow_position, text, font=font, fill=shadow_color)
    # Add text
    draw.text(position, text, font=font, fill=fill_color)

def custom_dice(stat, val, fonts, dice_icon, color, size=40, is_small=False):
    """
    Creates a custom dice image with specified parameters.

    Args:
    stat (str): The stat type.
    val (str): The value to display on the dice.
    fonts (dict): Dictionary of fonts.
    icons (dict): Dictionary of icons.
    color (tuple): RGB color tuple.
    size (int): Size of the dice icon.
    is_small (bool): Whether to use the small font.

    Returns:
    Image: Custom dice image.
    """
    # Convert the color tuple to a hex color string
    #color_hex = '#{:02x}{:02x}{:02x}'.format(*color)
    
    dice_c = colorise_icon(dice_icon, color)
    #dice_w = colorise_icon(dice_icon.resize((size-4, size-4), Image.Resampling.BILINEAR), (255, 255, 255))

    out = Image.new("RGBA", dice_c.size, (255, 255, 255, 0))

    #for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
    #    out.paste(dice_w, (offset[0], offset[1]), dice_w)

    out.paste(dice_c, (0, 0), dice_c)

    font_key = 'icon_small' if is_small else 'icon'
    add_text(out, val, fonts[font_key], color)

    return out



def load_card_template(card_type, icons, colors):
    """
    Loads and colors the card template based on the card type.

    Args:
    card_type (str): The type of the card.
    icons (dict): Dictionary of icons.
    colors (dict): Dictionary of colors.

    Returns:
    Image: Colored card template.
    """
    if card_type == 'Loot':
        return ImageOps.colorize(TEMPLATE_IMAGE.convert("L"), black=colors['Loot'], white="white")
    elif card_type == 'Damage':
        return ImageOps.colorize(TEMPLATE_IMAGE_DAMAGE.convert("L"), black=colors['Red'], white="white")
    else:
        return TEMPLATE_IMAGE.copy()

def add_card_picture(card, template, max_width_pic):
    """
    Loads and resizes the picture for the card.

    Args:
    card (Series): Data for the card.
    template (Image): The card template.
    max_width_pic (int): Maximum width for the picture.
    """
    try:
        pic = Image.open(f"{PICS_FOLDER}/{card['Title']}.png")
        pic = pic.resize((max_width_pic, int(max_width_pic / pic.size[0] * pic.size[1])))
        template.paste(pic, (35, 90))
    except FileNotFoundError:
        print(f"Image for '{card['Title']}' not found. Skipping picture.")

def add_title_elements(pos, card, draw, fonts, card_height, colors):
    # Add the title
    title = card['Title'].upper().split('_')[0]
    draw.text(pos, title, font=fonts['title'],  fill=colors['Red'])

def add_tags_elements(pos, card, draw, fonts, card_height, colors):
    # Add requirement, if any
    tag_x = 0
    if card['Requirement'] != '-':
        requirement_text = card['Requirement'].upper() + ' - '
        draw.text(pos,  requirement_text, font=fonts['req'], fill=colors['Red'])
        requirement_box = draw.textbbox((0, 0), text=requirement_text, font=fonts['req'])
        tag_x = requirement_box[2]

    # Add tags, if any
    if card['Tags'] != '-':
        draw.text((pos[0] + tag_x, pos[1]), card['Tags'], font=fonts['tag'],  fill=colors['Red'])

    # Add card type
    draw.text((40, card_height * 0.575),  card['Type'], font=fonts['italic'], fill=colors['Red'])
    
def add_effect_fail_flavor_texts(card, draw, fonts, template, card_height, max_width, max_width_effect):
    # Add effect text
    effect_text = wrap_text(card['Effect'], fonts['regular'], max_width_effect if card['Target'] != '-' else max_width)
    effect_box = draw.textbbox((0, 0), text=effect_text, font=fonts['regular'])
    draw.text((70 if card['Target'] != '-' else 40, card_height * 0.64), effect_text, font=fonts['regular'], fill=(0, 0, 0))
    if card['Target'] != '-':
        deff = custom_dice('', '≤'+card['Target'], fonts, icons['null'],  COLORS[card['Colour']], size = 32)   
        template.paste(deff, (32, int(card_height*0.64 + effect_box[3]/2 -14)), deff)
    
    # Add fail text, if any
    fail_box = (0, 0, 0, 0)
    if card['Fail'] != '-':
        fail_text = wrap_text(card['Fail'], fonts['regular'], max_width_effect)
        fail_box = draw.textbbox((0, 0), text=fail_text, font=fonts['regular'])
        draw.text((70, card_height * 0.66 + effect_box[3]), fail_text, font=fonts['regular'], fill=(0, 0, 0))
        
        dfail = custom_dice('', 'Fail', fonts, icons['null'],  COLORS[card['Colour']], size = 32)    
        template.paste(dfail, (32, int(card_height*0.66+ effect_box[3] + fail_box[3]/2 -14)), dfail)

    # Add flavor text, if any
    if card['Flavor'] != '-':
        try:
        # add the flavor text to the left side of the card
            fl_cax_h = -int(card_height*0.66 + effect_box[3]+ fail_box[3] - card_height*0.95)

            # print(card['Flavor'])
            flavor_text = wrap_text(card['Flavor'], fonts['italic'], max_width)
            flavor_box = draw.textbbox((0, 0), text=flavor_text, font=fonts['italic'])

            while (flavor_box[2] >= max_width or flavor_box[3] > fl_cax_h) and flavour_size > 9:
                flavour_size -= 1
                flavor_text = wrap_text(card['Flavor'], fonts['italic'], max_width)
                flavor_box = draw.textbbox((0, 0), text=flavor_text, font=fonts['italic'])

            draw.text((44, card_height*0.66 + effect_box[3]+ fail_box[3]+14), flavor_text, font=fonts['italic'], fill=COLORS['Black'])
        except:
            pass

def add_points(card, draw, fonts, card_height, colors):
    if card['PTS'] != '-':
        pts_text = str(card['PTS'])
        pts_box = draw.textbbox((0, 0), text=pts_text, font=fonts['pts'])
        add_text_with_shadow(draw, pts_text, fonts['pts'], (10, card_height - 14 - pts_box[3]), COLORS[card['Colour']], (255, 255, 255))


# iterate through the dataframe and create an image for each card
def create_card_image(card, fonts, icons):
    """
    Creates an image for a card.

    Args:
    card (Series): Data for the card.
    fonts (dict): Dictionary of fonts.
    icons (dict): Dictionary of icons.

    Returns:
    Image: Generated card image.
    """
    # Open the template image
    print(card['Title'].upper())
    
    # Load template and set up drawing context
    template = load_card_template(card['Type'], icons, COLORS)
    draw = ImageDraw.Draw(template)
    
    if card['Target'] != '-':
        d20 = custom_dice(card['Colour'], card['Target'], fonts, icons['d20'], COLORS[card['Colour']], is_small=True)
        template.paste(d20, (3, 14), d20)

    #if card['Colour'] != '-':
        #template = ImageOps.colorize(template.convert("L"), black=color[card['Colour']], white="white")

    card_width, card_height = template.size
    max_width_pic = card_width - 70
    max_width = card_width - 74
    max_width_effect = card_width - 74 - 32
    
    # Load and resize card picture
    add_card_picture(card, template, max_width_pic)

    add_title_elements((58, 36), card, draw, fonts, card_height, COLORS)
    add_tags_elements((40, 72), card, draw, fonts, card_height, COLORS)
    add_effect_fail_flavor_texts(card, draw, fonts, template, card_height, max_width, max_width_effect)
    add_points(card, draw, fonts, template.size[1], COLORS)
    
    # save the card as a JPEG file
    filename = f"{CARDS_FOLDER}/{card['Title']}.png"
    template.save(filename, "PNG", quality=200)

def main():
    if not os.path.exists(CARDS_FOLDER):
        os.makedirs(CARDS_FOLDER)

    cards_df = read_cards_data(CARDS_CSV)

    for _, card in cards_df.iterrows():
        card_image = create_card_image(card, fonts, icons)

if __name__ == "__main__":
    main()
