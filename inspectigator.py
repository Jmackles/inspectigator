# main.py
import os
import base64
import webbrowser
from dotenv import load_dotenv
from openai import OpenAI
from termcolor import colored
import requests
import uuid

# Load environment variables from .env file
load_dotenv()

# Set a directory to save DALL·E generated images
image_dir_name = "images"
image_dir = os.path.join(os.curdir, image_dir_name)

# Create the directory if it doesn't exist
if not os.path.isdir(image_dir):
    os.mkdir(image_dir)

# Print the directory where images will be saved
print(f"Images will be saved in: {image_dir}")

# Instantiate OpenAI client with API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def validate_input(user_input):
    """Validate user input for color and shape."""
    # Define valid colors and shapes
    colors = {"red", "blue", "green", "yellow", "black", "white"}
    shapes = {"circle", "square", "triangle", "rectangle"}

    try:
        color, shape = user_input.lower().split()
        return (color in colors and shape in shapes), color, shape
    except ValueError:
        # If user didn't enter exactly two words
        return False, None, None

def generate_description(color, shape):
    """
    Generate a plain shape description using GPT for the DALL·E prompt.
    Ensures minimal, no-embellishment output.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Updated to gpt-4o
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are interpreting color/shape input. "
                        "Return a concise prompt describing the shape of that color. "
                        "Avoid extra details and do not respond directly to the user."
                    ),
                },
                {
                    "role": "user",
                    "content": f"{color} {shape}",
                },
            ],
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(colored(f"Error generating description: {e}", "red"))
        return None

def generate_image(description):
    """Generate an image using DALL·E 3 based on the description."""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=description,
            n=1,
            size="1024x1024",
            quality="standard",
            response_format="url",
        )
        # Extract image URL
        image_url = response.data[0].url
        # Generate a unique filename
        generated_image_name = f"generated_image_{uuid.uuid4()}.png"
        generated_image_filepath = os.path.join(image_dir, generated_image_name)

        # Download the image
        image_data = requests.get(image_url).content
        with open(generated_image_filepath, "wb") as image_file:
            image_file.write(image_data)

        print(colored(f"Image saved to: {generated_image_filepath}", "cyan"))
        return image_url
    except Exception as e:
        print(colored(f"Error generating image: {e}", "red"))
        return None

def image_inspector(image_url):
    """
    Use GPT-4o with vision capabilities to inspect the generated image.
    This call uses the new format: content is an array with text and image_url objects.
    """
    try:
        # The model: gpt-4o, which can handle vision
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a vision-capable model. "
                        "Provide only the color and shape present in the image, "
                        "without extra details or explanation."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What’s in this image?"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                # You can add "detail": "auto" | "low" | "high"
                                # if you want to specify the resolution mode, e.g.:
                                # "detail": "low"
                            },
                        },
                    ],
                },
            ],
            max_tokens=300,
        )
        inspected_description = response.choices[0].message.content.strip()
        print(colored(inspected_description, "cyan"))
        return inspected_description
    except Exception as e:
        print(colored(f"Error inspecting image: {e}", "red"))
        return None

def validate_inspected_image(inspected_description, color, shape):
    """Validate the inspected image description against the user input."""
    desc_lower = inspected_description.lower()
    return color in desc_lower and shape in desc_lower

def main():
    """Main function to process user input and generate images."""
    attempts = 0
    while attempts < 3:
        user_input = input("Enter a color followed by a shape (e.g., 'red circle'): ")
        valid, color, shape = validate_input(user_input)

        if not valid:
            print(colored("Invalid input. Please enter exactly two words: a valid color and shape.", "red"))
            attempts += 1
            continue

        # Generate a short description
        description = generate_description(color, shape)
        if description is None or len(description) == 0:
            print(colored("Failed to generate a valid description.", "red"))
            attempts += 1
            continue

        print(colored(f"Generated Prompt: {description}", "cyan"))

        # Generate an image
        image_url = generate_image(description)
        if not image_url:
            print(colored("Failed to generate image.", "red"))
            attempts += 1
            continue

        print(colored(f"Generated Image URL: {image_url}", "cyan"))
        webbrowser.open(image_url)

        # Inspect the generated image via vision
        inspected_description = image_inspector(image_url)
        if not inspected_description:
            print(colored("Failed to inspect image.", "red"))
            attempts += 1
            continue

        # Validate the inspection result
        if validate_inspected_image(inspected_description, color, shape):
            print(colored("Image validated successfully.", "green"))
            return
        else:
            print(colored("Image validation failed.", "red"))
        attempts += 1

    print(colored("Maximum attempts reached. Exiting program.", "yellow"))

if __name__ == "__main__":
    main()