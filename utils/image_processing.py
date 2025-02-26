from PIL import Image

def center_background(background: Image, foreground: Image):

    # Ensure background is the size you want; optionally, you can resize if needed
    bg_width, bg_height = background.size
    fg_width, fg_height = foreground.size

    # Calculate offsets to center the foreground at the bottom
    x_offset = (bg_width - fg_width) // 2
    y_offset = bg_height - fg_height

    return (x_offset, y_offset)
    # Paste the foreground onto the background using the alpha channel as mask
    background.paste(foreground, (x_offset, y_offset), foreground)

    # Save or display the result
    background.show()  # For quick visual check

    return background