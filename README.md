# FishBackground

Work in progress! Project has just started!

Test project to recreate backgrounds of fishermen. This way they can safely share a picture without fear of revealing where the fish was caught. The model will create a new background based on the one provided.

Happy fishing!


---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Overview

FishBackground is designed to help fishermen share images safely. By using machine learning, the application removes the original background from a photo and replaces it with a generated one, preserving privacy while still looking natural.

---

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/MikaSie/FishBackground.git
   cd FishBackground
   ```

2. **Create a virtual environment:**
    ```bash
    python3 -m venv env 
    source env/bin/activate
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Run the FastAPI application:**
    ```bash
    uvicorn app.main:app --reload
    ```

2. **Access the API:**
Once the server is running, open your browser and navigate to http://localhost:8000/docs to see the interactive API documentation and test endpoints.

3. **Uploading and processing images:**
- Use the /upload endpoint to submit your image
- The backend will process the image, remove the original background, and return the modified image with a generated background.


## Project Structure
```
FishBackground/
├── app/                   
│   ├── __init__.py       
│   ├── main.py           # FastAPI app entry point
│   └── api.py            # API endpoints for image processing
│
├── data/                
│   ├── examples          # Examples for GitHub    
│   ├── output            # Placeholder folder for all outputs
│   └── stock_backgrounds # All stock backgrounds for copy+paste segmentations
|
├── models/                
│   ├── __init__.py       
│   ├── segmentation.py   # Functions for background segmentation
│   └── background.py     # Logic for background generation/replacement
|
|── tests/                 
│   ├── __init__.py       
│   ├── test_api.py       # Tests for API endpoints
│   └── test_models.py    # Tests for ML models and functions
|
├── utils/                 
│   ├── __init__.py       
│   ├── image_processing.py  # Image pre/post-processing functions
│   └── config.py            # Configuration and environment management
│
│
├── Dockerfile            # For containerizing the app
├── LICENSE               # MIT License
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Contributing

Contributions are welcome! If you’d like to contribute:
1.	Fork the repository.
2.	Create a new branch (git checkout -b feature/your-feature).
3.	Make your changes and commit them (git commit -am 'Add new feature').
4.	Push to the branch (git push origin feature/your-feature).
5.	Open a Pull Request.

Please ensure your code adheres to the project’s coding standards and includes tests when appropriate.


## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
If you have any questions or suggestions, please open an issue or contact the maintainer at my GitHub!
