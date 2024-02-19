# Inspectigator

Inspectigator is a proof of concept Python application that leverages multiple OpenAI API calls to validate expected results or reject them. It allows users to input a color and shape, which then generates a corresponding image using DALL·E 3. The generated image is further inspected by GPT-4's vision capabilities to ensure the image contains the specified color and shape.

## Features

- User input validation for color and shape.
- Image description generation using OpenAI's GPT-4 model.
- Image creation with DALL·E 3 based on the generated description.
- Image inspection using GPT-4's vision capabilities to validate the content.
- Local storage of generated images.
- Direct opening of generated image URLs in a web browser.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have installed Python 3.9 or higher.
- You have an OpenAI API key with access to GPT-4 and DALL·E 3 models.
- You have installed the required Python packages listed in `requirements.txt`.

## Installation

To install Inspectigator, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/jmackles/inspectigator.git
   ```
2. Navigate to the project directory:
   ```bash
   cd inspectigator
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To use Inspectigator, run the following command in your terminal:

```bash
python inspectigator.py
```

Follow the prompts to enter a color followed by a shape (e.g., "red circle"). The program will attempt to generate and validate an image up to three times before exiting.

## Configuration

Create a `.env` file in the root directory of the project with the following content:

```plaintext
OPENAI_API_KEY=your_openai_api_key_here
```

Replace `your_openai_api_key_here` with your actual OpenAI API key.
