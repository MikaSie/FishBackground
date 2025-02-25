import rembg
import matplotlib.pyplot as plt
import argparse
import os
from PIL import Image

#TODO: Add relative paths


class Segmenter:
    def __init__(self, model_name: str = 'u2net_human_seg'):
        self.model = self._load_model(model_name)

    # _load_model is a private method, that's why it starts with an underscore
    def _load_model(self, model_name: str):
        print(f'Loading model {model_name}')
        session = rembg.new_session(model_name= model_name)
        return session
    

    def create_background(self, background_path:str, foreground_path: str = 'tests/output.png'):
        """
        Creates a background for the given image using the model and saves the output.

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
        background = Image.open(background_path)
        background.paste(foreground, (0, 0), foreground)
        #TODO: Add relative paths
        background.save('tests/complete_image.png')
        return background


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

        with open(image_path, 'rb') as img_file:
            #TODO: Add relative paths
            with open(f'tests/output.png', 'wb') as output_file:
                input = img_file.read()
                output = rembg.remove(input, session= self.model, alpha_matting= True)
                output_file.write(output)


        """plt.imshow(Image.open('tests/output.png'))
        plt.axis('off')
        plt.show()"""
        
        return output_file
    

if __name__ == '__main__':
    # Test the Segmenter class
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, default='u2net_human_seg')
    parser.add_argument('--image', type=str, default='tests/mika.jpeg')
    
    args = parser.parse_args()

    
    segmenter = Segmenter()
    test_path = 'tests/mika.jpeg'
    segmenter.segment(test_path)
    segmenter.create_background(background_path='tests/background.jpeg', foreground_path='tests/output.png')

    plt.imshow(Image.open('tests/complete_image.png'))
    plt.axis('off')
    plt.show()
