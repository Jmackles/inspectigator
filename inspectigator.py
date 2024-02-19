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

# set a directory to save DALL·E images to
image_dir_name = "images"
image_dir = os.path.join(os.curdir, image_dir_name)

# create the directory if it doesn't yet exist
if not os.path.isdir(image_dir):
    os.mkdir(image_dir)

# print the directory to save to
print(f"{image_dir=}")


# Instantiate OpenAI client with API key
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def validate_input(user_input):
    """Validate user input for color and shape."""
    colors = {"red", "blue", "green", "yellow", "black", "white"}
    shapes = {"circle", "square", "triangle", "rectangle"}
    color, shape = user_input.lower().split()
    return (color in colors) and (shape in shapes), color, shape

def generate_description(color, shape):
    """Generate a description using OpenAI based on color and shape."""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are interpreting choices made by human input. Using the provided color/shape, return a prompt describing a shape of that color for DallE3 to make. It should be a plain description of the shape, it should not include unenessary details. Do not reply to the user or to the system message. Your reply is interpreted by the program automatically therefore it is crucial that you adhere to a succinct description of the shape of that color on an otherwise plain backdrop."},
                {"role": "user", "content": f"{color} {shape}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(colored(f"Error generating description: {e}", "red"))
        return None




def generate_image(description):
    """Generate an image using OpenAI based on the description."""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=description,
            n=1,
            size="1024x1024",
            quality="standard",
            response_format="url"
        )
        # Assuming the response contains a URL to the generated image
        image_url = response.data[0].url
        
        # Generate a unique filename using UUID
        generated_image_name = f"generated_image_{uuid.uuid4()}.png"
        generated_image_filepath = os.path.join(image_dir, generated_image_name)
        
        # Download the image
        generated_image = requests.get(image_url).content

        with open(generated_image_filepath, "wb") as image_file:
            image_file.write(generated_image)  # write the image to the file

        # Print the path of the saved image
        print(colored(f"Image saved to: {generated_image_filepath}", "cyan"))

        return image_url
    except Exception as e:
        print(colored(f"Error generating image: {e}", "red"))
        return None

# Define a function to submit the image to `gpt-4-vision-preview` to describe the image
def image_inspector(image_url):
    try:
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
        
        
        
        # Assuming the response contains the description of the image
        inspected_description = response.choices[0].message.content.strip()
        
        # Print the response in cyan
        print(colored(inspected_description, "cyan"))
        return inspected_description
    except Exception as e:
        print(colored(f"Error inspecting image: {e}", "red"))
        return None


# Define a function to validate the inspected image against the user input.
def validate_inspected_image(inspected_description, color, shape):
    """Validate the inspected image description against the user input."""
    # Normalize the description by converting it to lowercase
    inspected_description_lower = inspected_description.lower()
    
    # Check if both color and shape are present in the inspected description
    return color in inspected_description_lower and shape in inspected_description_lower

def main():
    """Main function to process user input and generate images."""
    attempts = 0
    while attempts < 3:
        user_input = input("Enter the color followed by shape: ")
        try:
            valid, color, shape = validate_input(user_input)
        except ValueError:
            print(colored("Please enter exactly two words: a color and a shape.", "red"))
            attempts += 1
            continue

        if not valid:
            print(colored("Invalid input. Please enter a valid color and a shape.", "red"))
            attempts += 1
            continue

        description = generate_description(color, shape)
        if description:
            print(colored(description, "cyan"))
            image_url = generate_image(description)
            if image_url:
                print(colored(f"Generated Image URL: {image_url}", "cyan"))
                webbrowser.open(image_url)
                inspected_description = image_inspector(image_url)
                if validate_inspected_image(inspected_description, color, shape):
                    print(colored("Image validated successfully.", "green"))
                    return  # Exit the loop after successful validation
                else:
                    print(colored("Image validation failed.", "red"))
            else:
                print(colored("Failed to generate image.", "red"))
        else:
            print(colored("Failed to generate description.", "red"))
        attempts += 1

    if attempts >= 3:
        print(colored("Maximum attempts reached. Exiting program.", "yellow"))

if __name__ == "__main__":
    main()
