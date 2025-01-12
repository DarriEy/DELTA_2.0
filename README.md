# DELTA: An AI-Assisted Hydrological Research Assistant

[![Project Status](https://img.shields.io/badge/Status-In%20Development-yellow.svg)](https://github.com/DarriEy/Delta_2.0)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Overview

DELTA (Descriptive এখানকার নাম দিন) is an innovative AI-powered research assistant designed to facilitate hydrological modeling, data analysis, and education. It leverages state-of-the-art technologies, including a conversational AI avatar, large language models (LLMs), and a comprehensive hydrological modeling framework to provide a user-friendly and interactive experience for researchers, students, and professionals in the field of hydrology.

DELTA offers a multi-modal interface, allowing users to interact with the system through text and voice commands. It features an animated avatar that provides visual feedback and enhances user engagement. The system is built upon a robust architecture that integrates a React frontend, a FastAPI backend, and various external APIs for natural language processing, text-to-speech, and image generation.

## Features

*   **Conversational AI Avatar:** Interact with DELTA through natural language using text or voice.
*   **Multiple Modes of Operation:**
    *   **General Mode:** For general hydrological inquiries and conversations with the AI.
    *   **Educational Mode:** Access interactive educational content on hydrology, including an introductory course (Hydrology 101) with various topics.
    *   **Modeling Mode:** Run hydrological simulations using the CONFLUENCE modeling framework. Select from various models (SUMMA, FUSE, MESH, HYPE, GR4J, FLASH) or run all of them simultaneously.
    *   **Data Analysis Mode:** Analyze hydrological data, such as estimating average daily temperature and precipitation for specific locations (e.g., Bow River at Banff).
*   **Background Image Generation:** Dynamically generates background images based on the active mode using the Vertex AI API.
*   **Speech Recognition and Text-to-Speech:** Supports voice interaction through the browser's Speech Recognition API and the Google Cloud Text-to-Speech API.
*   **Integration with External APIs:**
    *   **Anthropic Claude API:** For natural language understanding and response generation.
    *   **Google Cloud Text-to-Speech API:** To give DELTA a voice.
    *   **Vertex AI API:** For dynamic background image generation.
*   **CONFLUENCE Integration:** Seamlessly integrates with the CONFLUENCE hydrological modeling framework for running simulations.
*   **Modular and Extensible:** Designed with a modular architecture that allows for easy expansion and customization.

## Architecture

DELTA's architecture consists of the following key components:

*   **Frontend:** Built with React, JavaScript, and Tailwind CSS, providing the user interface and avatar interaction.
*   **API Gateway:** Acts as a single entry point for requests, handling routing and potentially authentication.
*   **Backend (DELTA Orchestrator):** A FastAPI-based backend that orchestrates the different services, manages state, and integrates with external APIs.
*   **Tooling Layer:** Includes various tools for hydrological modeling (CONFLUENCE), data analysis, and external data access (MAF, CUAHSI).
*   **External Data Sources:** Integrates with external APIs and databases for hydrological data.
*   **Knowledge Base:** Stores user data, conversation history, and potentially other relevant information.



## Getting Started

### Prerequisites

*   Node.js (v16 or higher recommended)
*   npm (or Yarn)
*   Python 3.9+
*   Virtual environment (recommended, e.g., `venv` or `conda`)
*   Anthropic API key
*   Google Cloud Text-to-Speech API credentials
*   Vertex AI API credentials

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/DarriEy/DELTA_2.0
    cd your-repo-name
    ```

2.  **Frontend Setup:**

    ```bash
    cd my-avatar-app
    npm install
    ```

3.  **Backend Setup:**

    ```bash
    cd ../backend
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    *   Create a `.env` file in the `backend` directory.
    *   Add the following environment variables, replacing the placeholders with your actual API keys and credentials:

        ```
        ANTHROPIC_API_KEY=your_anthropic_api_key
        GOOGLE_APPLICATION_CREDENTIALS=path/to/your/google_cloud_credentials.json
        PROJECT_ID=your-gcp-project-id
        LOCATION=your-gcp-region
        # Add other environment variables as needed
        ```

### Running the Application

1.  **Start the Backend Server:**

    ```bash
    cd backend
    source .venv/bin/activate
    uvicorn main:app --reload
    ```

2.  **Start the Frontend Development Server:**

    ```bash
    cd my-avatar-app
    npm start
    ```

3.  **Access the Application:**
    Open your web browser and go to `http://localhost:5173`.

## Usage

1.  **Interact with DELTA:**
    *   Click on the DELTA avatar to start the interaction.
    *   DELTA will greet you with an introduction and start listening.
    *   Speak your requests or questions clearly.
    *   You can also type your input if you prefer.

2.  **Switch Modes:**
    *   Use the buttons in the top-left corner to switch between "General Mode," "Educational Mode," "Modeling Mode," and "Data Analysis Mode."

3.  **Educational Mode:**
    *   Explore the provided educational content.
    *   Click "Open Content" to view the content frame, and "Close Content" to hide it.

4.  **Modeling Mode:**
    *   Select a hydrological model from the dropdown menu.
    *   Click "Run Model(s)" to start a simulation (currently a simulated run).

5.  **Data Analysis Mode:**
    *   Select a variable (Temperature or Precipitation) from the dropdown menu.
    *   Click "Run Analysis" to perform a sample analysis (currently a simulated analysis).

## Configuration

*   **`config.yaml`:** This file in the `backend` directory is used to configure the CONFLUENCE modeling framework. You can modify it to change model settings, data paths, and other parameters.
*   **Environment Variables:** The `.env` file in the `backend` directory is used to store API keys and other sensitive information.

## Contributing

We welcome contributions to DELTA! If you'd like to contribute, please follow these guidelines:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them with clear and descriptive commit messages.
4.  Submit a pull request to the `main` branch.
5.  Be sure to follow the existing code style and conventions.
6.  Write tests for your changes whenever possible.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

*   This project was funded in part by [Funding Source/Grant].
*   We acknowledge the contributions of [Contributors/Collaborators].
*   We thank the developers of the following open-source projects:
    *   React
    *   FastAPI
    *   Tailwind CSS
    *   Anthropic Claude
    *   Google Cloud Text-to-Speech
    *   Vertex AI
    *   CONFLUENCE
    *   MAF
    *   [Add other dependencies here]

## Contact

For questions or inquiries, please reach out

## Further Development

We plan to continue developing DELTA by adding more features, including:

*   **More Hydrological Models:** Integrate more models into the Modeling Mode.
*   **Advanced Data Analysis:** Implement more sophisticated data analysis techniques and visualizations.
*   **Improved LLM Integration:** Enhance the conversational capabilities and contextual awareness of the AI.
*   **User Authentication:** Add user accounts and authentication for personalized experiences.
*   **Enhanced UI/UX:** Continuously improve the user interface and user experience.

---
