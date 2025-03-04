import rembg
import matplotlib.pyplot as plt
import argparse
import os
import random
import io
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


    def segment(self, image_path: str) -> Image.Image:
        """
        Segments the given image using the model and returns the segmented image as a PIL Image.
        
        Args:
            image_path (str): The path to the image file to be segmented.
        
        Returns:
            Image.Image: The segmented image with transparency.
        """
        print(f'Segmenting image {image_path}')
        with open(image_path, 'rb') as img_file:
            input_bytes = img_file.read()
            output_bytes = rembg.remove(input_bytes, session=self.model, alpha_matting=True)
        
        # Convert the output bytes to a PIL Image using an in-memory buffer
        segmented_image = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

        return segmented_image
    
    
    def combine_foreground_and_background(self, background_image: Image.Image, foreground_image: Image.Image, random_background: bool = False) -> Image.Image:
        """
        Pastes the segmented foreground image onto the background image and returns the combined image.
        The final image is saved in the data/output folder.
        
        Args:
            background_image (Image.Image): The background image as a PIL Image.
            foreground_image (Image.Image): The segmented foreground image as a PIL Image.
            random_background (bool): If True, a random background from the stock backgrounds is used.
        
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
    print(f"Segmented foreground type: {type(segmented_foreground)}")
    
    # Load the background image as a PIL image
    background_image = Image.open(background_path)
    
    # Combine the foreground and background images
    combined_image = segmenter.combine_foreground_and_background(
        background_image=background_image, 
        foreground_image=segmented_foreground, 
        random_background=args.random_background
    )

    print('Combined image saved to data/output/complete_image.png')
    
    # Display the final image
    plt.imshow(combined_image)
    plt.axis('off')
    plt.show()
