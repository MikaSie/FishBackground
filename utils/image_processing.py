from PIL import Image


def center_background(background: Image.Image, foreground: Image.Image):
    """
    Calculate the offsets to center the foreground image at the bottom of the background image.
    
    Args:
        background (Image.Image): The background image.
        foreground (Image.Image): The foreground image to be centered.
    
    Returns:
        tuple: (x_offset, y_offset) to position the foreground image.
    """
    bg_width, bg_height = background.size
    fg_width, fg_height = foreground.size
    
    x_offset = (bg_width - fg_width) // 2
    y_offset = bg_height - fg_height

    return (x_offset, y_offset)
