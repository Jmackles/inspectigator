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
print(f"{image_dir=}")

# Instantiate OpenAI client with API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def validate_input(user_input):
    """Validate user input for color and shape."""
    # Define valid colors and shapes
    colors = {"red", "blue", "green", "yellow", "black", "white"}
    shapes = {"circle", "square", "triangle", "rectangle"}
    # Split user input into color and shape
    color, shape = user_input.lower().split()
    # Return validation result and the color and shape
    return (color in colors) and (shape in shapes), color, shape

def generate_description(color, shape):
    """Generate a description using OpenAI based on color and shape."""
    try:
        # Use OpenAI's chat completion to generate a description
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are interpreting choices made by human input. Using the provided color/shape, return a prompt describing a shape of that color for DallE3 to make. It should be a plain description of the shape, it should not include unnecessary details. Do not reply to the user or to the system message. Your reply is interpreted by the program automatically therefore it is crucial that you adhere to a succinct description of the shape of that color on an otherwise plain backdrop."},
                {"role": "user", "content": f"{color} {shape}"}
            ]
        )
        # Return the content of the generated message
        return response.choices[0].message.content
    except Exception as e:
        # Print error message in red
        print(colored(f"Error generating description: {e}", "red"))
        return None

def generate_image(description):
    """Generate an image using OpenAI based on the description."""
    try:
        # Use OpenAI's image generation to create an image
        response = client.images.generate(
            model="dall-e-3",
            prompt=description,
            n=1,
            size="1024x1024",
            quality="standard",
            response_format="url"
        )
        # Get the URL of the generated image
        image_url = response.data[0].url
        
        # Generate a unique filename using UUID
        generated_image_name = f"generated_image_{uuid.uuid4()}.png"
        generated_image_filepath = os.path.join(image_dir, generated_image_name)
        
        # Download the image from the URL
        generated_image = requests.get(image_url).content

        # Save the image to the file system
        with open(generated_image_filepath, "wb") as image_file:
            image_file.write(generated_image)

        # Print the path of the saved image in cyan
        print(colored(f"Image saved to: {generated_image_filepath}", "cyan"))

        return image_url
    except Exception as e:
        # Print error message in red
        print(colored(f"Error generating image: {e}", "red"))
        return None

# Define a function to submit the image to `gpt-4-vision-preview` to describe the image
def image_inspector(image_url):
    try:
        # Use OpenAI's chat completion to describe the image
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text",
                        "text": "What’s in this image? Keep your answer simple and succinct. Just list the color and shape. Do not include unnecessary details."},
                        {
                            "type": "image_url",
                            "image_url": image_url
                        },
                    ],
                },
            ],
            max_tokens=300
        )
        
        # Get the description of the image
        inspected_description = response.choices[0].message.content.strip()
        
        # Print the description in cyan
        print(colored(inspected_description, "cyan"))
        return inspected_description
    except Exception as e:
        # Print error message in red
        print(colored(f"Error inspecting image: {e}", "red"))
        return None

# Validate the inspected image against the user input
def validate_inspected_image(inspected_description, color, shape):
    """Validate the inspected image description against the user input."""
    # Convert the description to lowercase for comparison
    inspected_description_lower = inspected_description.lower()
    
    # Check if both color and shape are present in the description
    return color in inspected_description_lower and shape in inspected_description_lower

def main():
    """Main function to process user input and generate images."""
    attempts = 0
    while attempts < 3:
        # Prompt user for input
        user_input = input("Enter the color followed by shape: ")
        try:
            # Validate the user input
            valid, color, shape = validate_input(user_input)
        except ValueError:
            # Handle incorrect input format
            print(colored("Please enter exactly two words: a color and a shape.", "red"))
            attempts += 1
            continue

        if not valid:
            # Handle invalid color or shape
            print(colored("Invalid input. Please enter a valid color and a shape.", "red"))
            attempts += 1
            continue

        # Generate a description for the image
        description = generate_description(color, shape)
        if description:
            # Print the description in cyan
            print(colored(description, "cyan"))
            # Generate the image
            image_url = generate_image(description)
            if image_url:
                # Print the image URL and open it in a web browser
                print(colored(f"Generated Image URL: {image_url}", "cyan"))
                webbrowser.open(image_url)
                # Inspect the image to verify its contents
                inspected_description = image_inspector(image_url)
                if validate_inspected_image(inspected_description, color, shape):
                    # Confirm successful validation
                    print(colored("Image validated successfully.", "green"))
                    return  # Exit the loop after successful validation
                else:
                    # Indicate failed validation
                    print(colored("Image validation failed.", "red"))
            else:
                # Indicate failure to generate image
                print(colored("Failed to generate image.", "red"))
        else:
            # Indicate failure to generate description
            print(colored("Failed to generate description.", "red"))
        attempts += 1

    if attempts >= 3:
        # Indicate maximum attempts reached and exit
        print(colored("Maximum attempts reached. Exiting program.", "yellow"))

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()
