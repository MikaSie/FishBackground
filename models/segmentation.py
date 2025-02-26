import rembg
import matplotlib.pyplot as plt
import argparse
import os
import random
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


    def segment(self, image_path: str):
        """
        Segments the given image using the model and saves the output.

        Args:
            image_path (str): The path to the image file to be segmented.

        Returns:
            file object: The file object of the output image.

        Raises:
            FileNotFoundError: If the image file does not exist.
            IOError: If there is an error reading or writing the files.
        """
        print(f'Segmenting image {image_path}')
        #TODO: Add functionality for multiple images

        #TODO: Consider not saving output, but returning the file object for later. Otherwise we will have to delete the file after using it.
        with open(image_path, 'rb') as img_file:
            with open(os.path.join('data', 'output.png'), 'wb') as output_file:
                input = img_file.read()
                output = rembg.remove(input, session= self.model, alpha_matting= True)
                output_file.write(output)


        """plt.imshow(Image.open('tests/output.png'))
        plt.axis('off')
        plt.show()"""
        
        return output_file
    
    
    def create_background(self, background_path:str, foreground_path: str = 'tests/output.png', random_background: bool = False):
        """
        Creates a background for the given image using the model and saves the output.
        For now this function can only handle the first type of segmentation, where the foreground is just pasted on a different
        background. This function will be updated to handle more complex segmentations in the future.

        Args:
            background (str): The path to the background image file.
            foreground_path (str): The path to the segmented image file.

        Returns:
            file object: The file object of the output image.

        Raises:
            FileNotFoundError: If the image file does not exist.
            IOError: If there is an error reading or writing the files.
        """
        foreground = Image.open(foreground_path)
        if random_background:
            random_choice = random.choice(os.listdir(os.path.join('data', 'stock_backgrounds')))
            background_path = os.path.join(os.path.join('data', 'stock_backgrounds', random_choice))
            print(f'Using random background {random_choice}, out of choices of {os.listdir(os.path.join("data", "stock_backgrounds"))}')

        background = Image.open(background_path)
        background.paste(foreground, center_background(background, foreground), foreground)
        background.save(os.path.join('data', 'output', 'complete_image.png'))

        return background


if __name__ == '__main__':
    # Test the Segmenter class
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default= 'u2net_human_seg')
    parser.add_argument('--image', type=str, default= 'before.jpeg') 
    parser.add_argument('--background', type=str, default= 'blue_morning.jpeg')
    parser.add_argument('--random_background', action= "store_true", default= False)

    args = parser.parse_args()
    args.image = os.path.join('data', 'examples', args.image)
    args.background = os.path.join('data', 'stock_backgrounds', args.background)

    segmenter = Segmenter(model_name= args.model)
    segmenter.segment(args.image)

    segmenter.create_background(background_path= args.background, 
                                foreground_path= os.path.join('data', 'output.png'), 
                                random_background= args.random_background)

    #Check path
    plt.imshow(Image.open(os.path.join('data', 'output', 'complete_image.png')))
    plt.axis('off')
    plt.show()
