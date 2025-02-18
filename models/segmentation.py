import rembg
import matplotlib.pyplot as plt
from PIL import Image

class Segmenter:
    def __init__(self, model_name: str = 'u2net_human_seg'):
        self.model = self._load_model(model_name)

    # _load_model is a private method, that's why it starts with an underscore
    def _load_model(self, model_name: str):
        print(f'Loading model {model_name}')
        session = rembg.new_session(model_name= model_name)
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
        with open(image_path, 'rb') as img_file:
            with open('tests/output.png', 'wb') as output_file:
                input = img_file.read()
                output = rembg.remove(input, session= self.model)
                output_file.write(output)
        return output_file
    

if __name__ == '__main__':
    # Test the Segmenter class
    segmenter = Segmenter()
    test_path = 'tests/mika.jpeg'
    segmenter.segment(test_path)
    
    plt.imshow(Image.open('tests/output.png'))
    plt.axis('off')
    plt.show()
