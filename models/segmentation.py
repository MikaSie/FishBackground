import rembg
import matplotlib.pyplot as plt
import argparse
import os
import random
import io
import torch
from diffusers import StableDiffusionInpaintPipeline #TODO: Check later if this is the correct import, ControlNet version also possible, but also StableDiffusion3InpaintPipeline
from typing import Union
from utils.image_processing import center_background
from PIL import Image


class Segmenter:
    
    def __init__(self, model_name: str = 'u2net_human_seg'):
        self.model = self._load_model(model_name)
        self.inpaint_pipe = self._load_inpainting_pipeline()

    # _load_model is a private method, that's why it starts with an underscore
    def _load_model(self, model_name: str):
        """
        Loads a machine learning model session for image segmentation based on the given model name.

        Parameters:
            model_name (str): The identifier or name of the model to be loaded.

        Returns:
            session: An active session or context object created by the rembg library,
                     configured to use the specified model for segmentation tasks.

        Side Effects:
            Prints progress messages to the standard output indicating the start and completion
            of the model loading process.
        """
        print(f'Loading model {model_name}')
        session = rembg.new_session(model_name = model_name)
        print(f'Model {model_name} loaded')
        return session
    

    def _load_inpainting_pipeline(self):
        """
        Initializes the Stable Diffusion inpainting pipeline.
        Note: Requires a CUDA-enabled GPU for best performance.
        """
        print("Loading Stable Diffusion Inpainting Pipeline...")
        pipe = StableDiffusionInpaintPipeline.from_pretrained(
            "runwayml/stable-diffusion-inpainting", 
            torch_dtype=torch.float16
        )

        #TODO: Check if this can be done to use GPU with mac silicon
        #pipe = pipe.to("cuda")
        print("Inpainting Pipeline loaded.")
        return pipe


    def segment(self, image_input: Union[str, Image.Image]) -> Image.Image:
        """
        Segments the input image by removing its background using the rembg library with alpha matting.
        Parameters:
            image_input (str | PIL.Image.Image): 
                The image to segment. This can either be a file path to the image (str) or an in-memory PIL Image.
        Returns:
            PIL.Image.Image: 
                A PIL Image object representing the segmented image with an RGBA mode, where the background has been removed.
        Raises:
            TypeError: 
                If the provided image_input is neither a file path (str) nor a PIL Image.
        """
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

    def inpaint_background(self, segmented_image: Image.Image, prompt: str, guidance_scale: float = 7.5) -> Image.Image:
        """
        Uses Stable Diffusion inpainting to generate a new background based on a text prompt.
        The method derives a mask from the alpha channel of the segmented image, where the transparent
        areas (background) will be inpainted.

        Parameters:
            segmented_image (PIL.Image.Image): The image with the foreground (e.g., fisherman) and a transparent background.
            prompt (str): The text prompt to guide the generation of the new background.
            guidance_scale (float): How strongly the prompt is followed (default 7.5).

        Returns:
            PIL.Image.Image: The final image with the inpainted background.
        """
        # Create a mask from the alpha channel: 
        # White (255) where the alpha is low (background to fill), black (0) where the foreground is.
        alpha_channel = segmented_image.split()[-1]
        mask = alpha_channel.point(lambda p: 255 if p < 128 else 0).convert("L")
        
        # Create a base image (RGB) that uses a solid color (e.g., white) where the background is missing.
        base_image = Image.new("RGB", segmented_image.size, (255, 255, 255))
        base_image.paste(segmented_image, mask=alpha_channel)
        base_image = Image.new("RGB", segmented_image.size, (255, 255, 255))
        # Paste the segmented image onto the white base using its alpha channel as the mask.
        base_image.paste(segmented_image, mask=alpha_channel)

        # --- Display Images Side by Side ---
        """fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        # Original Segmented Image
        axes[0].imshow(segmented_image)
        axes[0].set_title("Segmented Image")
        axes[0].axis("off")

        # Mask Image
        axes[1].imshow(mask, cmap="gray")
        axes[1].set_title("Mask Image")
        axes[1].axis("off")

        # Base Image
        axes[2].imshow(base_image)
        axes[2].set_title("Base Image")
        axes[2].axis("off")

        plt.tight_layout()
        plt.show()"""
        # Run the inpainting pipeline.
        result = self.inpaint_pipe(
            prompt=prompt,
            image=base_image,
            mask_image=mask,
            guidance_scale=guidance_scale
        )
        inpainted_image = result.images[0]
        return inpainted_image
    

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

    inpainted_image = segmenter.inpaint_background(segmented_foreground, "a serene fishing boat on a misty lake with a lush forest in the background")
    
    # Display the final image
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    axes[0].imshow(combined_image)
    axes[0].set_title("Combined Image")
    axes[0].axis('off')

    axes[1].imshow(inpainted_image)
    axes[1].set_title("Inpainted Image")
    axes[1].axis('off')

    plt.tight_layout()
    plt.show()
