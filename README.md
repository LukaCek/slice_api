# Print Price Calculator

> **Note:** This project is in the early stages of development. Features may change, and occasional instability is expected.

This project is a web application built with Python and the Flask framework, which functions as a price calculator for 3D printing. It allows users to upload 3D models in `.stl` format, and the application uses OrcaSlicer to calculate the estimated printing time, material consumption, and based on this data, estimates the final printing price.

The application is available at: **printprice.cekluka.com** [view](https://printprice.cekluka.com)

Current settings on this website are from the files dir. Because I couldn't figure out how to use custom parameters.


## Features

*   **STL File Upload:** Users can upload their 3D models through the web interface.
*   **Print Quality Selection:** Option to choose between different print quality profiles, which affect time and price.
*   **Automatic Slicing:** OrcaSlicer runs in the background to prepare the model for printing.
*   **Detailed Price Calculation:** The price is composed of several components:
    *   Material cost (PLA, PETG)
    *   Cost of consumed electricity
    *   Printer maintenance cost
    *   Printer amortization
    *   Minimum service fee
*   **Various Output Formats:** After calculation, the user can receive:
    *   A detailed analysis of the price and printing time (web page).
    *   A prepared `.3mf` file.
    *   A generated `G-code` file.
    *   Data in `JSON` format.

## Technologies

*   **Backend:** Python, Flask
*   **Slicer:** OrcaSlicer
*   **Frontend:** HTML, Jinja2
*   **Hosting:** Docker, Google Cloud Run

## Installation:

### Installation with Docker (reconanded)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/LukaCek/slice_api.git
    cd slice_api
    ```
    or

    Download the repository as a ZIP file and extract it.
    
2.  **Install docker:**

    Go to [docker.com](https://www.docker.com/products/docker-desktop/) and install Docker Desktop.

3.  **Build and start the app:**

    For this to work, Docker needs to be running.

    **Linux/macOS:**
    ```bash
    ./start.sh
    ```
    **Windows:** I haven't tested this, because I don't have Windows, but you can try either of these methods:
    *   Using Git Bash or WSL terminal:
        ```bash
        ./start.sh
        ```
    *   Using PowerShell:
        ```powershell
        .\start.ps1
        or
        # this can be run by right clicking the file and selecting "Run with PowerShell"

    This script will install orcaslocer inside the container and all dependencies automatically.

    This script can also be used to start the app after the first time.

### Local Installation and Setup

To run the project in a local environment, you need Python, Flask, and OrcaSlicer installed.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/LukaCek/slice_api.git
    cd slice_api
    ```

2.  **Install dependencies:**
    ```bash
    pip install Flask
    ```

3.  **Install OrcaSlicer:**
    Follow the installation instructions on the official OrcaSlicer website. Make sure the `orcaslicer` command is available in your system's PATH.

4.  **Run the application:**
    ```bash
    python app.py
    ```
    The application will be accessible at `http://localhost:8080`.


## TODO

Here are some planned features and improvements:

*   **Material Selection:** Implement a feature to allow users to select the printing material settings.
*   **Advanced Slicing Parameters:** Expose more slicing parameters to the user, such as layer height, infill percentage, support settings, etc., for more granular control over the print.