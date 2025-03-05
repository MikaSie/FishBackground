import rembg
import matplotlib.pyplot as plt
import argparse
import os
import random
import io
from typing import Union
from utils.image_processing import center_background
from PIL import Image

#TODO: Add relative paths


class Segmenter:
    
    def __init__(self, model_name: str = 'u2net_human_seg'):
        self.model = self._load_model(model_name)

    # _load_model is a private method, that's why it starts with an underscore
    def _load_model(self, model_name: str):
        print(f'Loading model {model_name}')
        session = rembg.new_session(model_name = model_name)
        print(f'Model {model_name} loaded')
        return session



    def segment(self, image_input: Union[str, Image.Image]) -> Image.Image:
        # If image_input is a string, open the file.
        if isinstance(image_input, str):
            with open(image_input, 'rb') as img_file:
                input_bytes = img_file.read()
        # Otherwise, assume it's a PIL Image.
        elif isinstance(image_input, Image.Image):
            # Save the image to an in-memory buffer.
            buf = io.BytesIO()
            image_input.save(buf, format="PNG")
            buf.seek(0)
            input_bytes = buf.getvalue()
        else:
            raise TypeError("Expected a file path (str) or a PIL Image")

        # Process the image bytes.
        output_bytes = rembg.remove(input_bytes, session=self.model, alpha_matting=True)
        
        # Convert the output bytes back to a PIL Image.
        segmented_image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
        return segmented_image
    
    
    def combine_foreground_and_background(self, background_image: Image.Image, foreground_image: Image.Image, 
                                          random_background: bool = False, save_image: bool = False) -> Image.Image:
        """
        Pastes the segmented foreground image onto the background image and returns the combined image.
        
        Args:
            background_image (Image.Image): The background image as a PIL Image.
            foreground_image (Image.Image): The segmented foreground image as a PIL Image.
            random_background (bool): If True, a random background from the stock backgrounds is used.
            save_image (bool): If True, the final image is saved to the data/output folder.
        
        Returns:
            Image.Image: The final combined image.
        """
        if random_background:
            random_choice = random.choice(os.listdir(os.path.join('data', 'stock_backgrounds')))
            random_background_path = os.path.join('data', 'stock_backgrounds', random_choice)
            print(f'Using random background {random_choice}')
            background_image = Image.open(random_background_path).convert("RGBA")
        else:
            background_image = background_image.convert("RGBA")
        
        position = center_background(background_image, foreground_image)
        background_image.paste(foreground_image, position, foreground_image)
        
        output_path = os.path.join('data', 'output', 'complete_image.png')
        
        if save_image:
            background_image.save(output_path)

        return background_image


if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model', type=str, default='u2net_human_seg',
                        help='The segmentation model to use.')
    parser.add_argument('-i', '--image', type=str, default='before.jpeg',
                        help='The image to segment.')
    parser.add_argument('-b', '--background', type=str, default='blue_morning.jpeg',
                        help='The background image to use.')
    parser.add_argument('-rb', '--random_background', action="store_true", default=False,
                        help='Use a random background from the stock backgrounds.')
    
    args = parser.parse_args()
    
    image_path = os.path.join('data', 'examples', args.image)
    background_path = os.path.join('data', 'stock_backgrounds', args.background)
    
    segmenter = Segmenter(model_name=args.model)
    
    # Get the segmented foreground as a PIL image in memory
    segmented_foreground = segmenter.segment(image_path)
    
    # Load the background image as a PIL image
    background_image = Image.open(background_path)
    
    # Combine the foreground and background images
    combined_image = segmenter.combine_foreground_and_background(
        background_image=background_image, 
        foreground_image=segmented_foreground, 
        random_background=args.random_background
    )
    
    # Display the final image
    plt.imshow(combined_image)
    plt.axis('off')
    plt.show()
