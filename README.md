# Simple To-Do App with FastAPI, Streamlit, and Gemini AI

## Overview

This project presents a full-stack To-Do list application designed for simplicity and persistence, enhanced with AI capabilities. It allows users to manage their daily tasks, set priorities, assign due dates, and even translate task details using the Google Gemini AI model. The application features a robust backend built with FastAPI, a user-friendly frontend powered by Streamlit, and persistent data storage using SQLite.

## Features

* **CRUD Operations:** Easily Create, Read, Update (mark as completed), and Delete To-Do items.
* **Task Prioritization:** Assign `Low`, `Medium`, or `High` priority levels to tasks for better organization.
* **Due Date Tracking:** Set specific due dates for your tasks.
* **Persistent Storage:** All your To-Do items, including their details, priority, and due dates, are saved to a local SQLite database (`sql_app.db`), ensuring your data is not lost when the application restarts.
* **Visual Priority Indicators:** Task containers are dynamically colored based on their priority level (e.g., green for Low, yellow for Medium, red for High), providing an immediate visual cue.
* **AI-Powered Translation:** Translate To-Do item titles and descriptions into various languages using the Google Gemini AI model.
* **Modern User Interface:** An intuitive and responsive UI built with Streamlit.
* **Robust Backend:** A high-performance and scalable API built with FastAPI.

## Technologies Used

### Backend
* **FastAPI:** A modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints.
* **SQLModel:** A library for interacting with SQL databases, designed to be simple, consistent, and robust. It's built on top of Pydantic and SQLAlchemy.
* **Uvicorn:** An ASGI server for running FastAPI applications.
* **Python-Dotenv:** For loading environment variables from a `.env` file.
* **Google Generative AI:** Python client library for interacting with Google's Gemini AI models for translation services.
* **SQLite:** A lightweight, file-based SQL database used for persistent data storage.

### Frontend
* **Streamlit:** An open-source app framework for Machine Learning and Data Science teams to create beautiful, custom web apps in minutes.
* **Requests:** A simple, yet elegant HTTP library for Python, used to communicate with the FastAPI backend.

### Development Tools
* **Poetry:** A dependency management and packaging tool for Python. (Recommended)

## Prerequisites

Before you begin, ensure you have the following installed:

* **Python 3.9+**: You can download it from [python.org](https://www.python.org/downloads/).
* **Poetry (Recommended)**: Follow the installation instructions on the [Poetry documentation](https://python-poetry.org/docs/#installation).
* **Google Gemini API Key**:
    * Go to the [Google AI Studio](https://aistudio.google.com/app/apikey).
    * Create a new API key.
    * You will need to set this key in your environment variables.

## Setup and Installation

Follow these steps to get the application up and running on your local machine:

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url> # Replace with your repository URL if hosted
    cd todo_app
    ```

2.  **Install Dependencies:**
    Using Poetry (recommended):
    ```bash
    poetry install
    ```
    This command will create a virtual environment and install all the necessary packages listed in `pyproject.toml`.

3.  **Set up Environment Variables:**
    Create a file named `.env` in the root of your `todo_app` directory (the same level as `pyproject.toml`).
    Add your Google Gemini API key to this file:
    ```
    GOOGLE_API_KEY="your_google_gemini_api_key_here"
    ```
    **Important:** Replace `"your_google_gemini_api_key_here"` with your actual API key.

4.  **Database Initialization:**
    The SQLite database file (`sql_app.db`) will be automatically created in the `todo_app` directory the first time you run the backend server. If you previously had an in-memory or older database file, it's recommended to delete any existing `sql_app.db` file to ensure a clean start with the correct schema.

## Running the Application

The application consists of two parts: a FastAPI backend and a Streamlit frontend. Both need to be running simultaneously.

1.  **Start the Backend Server:**
    Open your first terminal, navigate to the `todo_app` directory, and run:
    ```bash
    uvicorn src.backend.main:app --reload
    ```
    You should see output indicating that the server is running on `http://127.0.0.1:8000`. The `--- Database tables created (if they didn't exist) ---` message confirms your database is set up.

2.  **Start the Frontend Application:**
    Open a *second* terminal, navigate to the `todo_app` directory, and run:
    ```bash
    streamlit run src/frontend/app.py
    ```
    This will open the Streamlit application in your web browser, typically at `http://localhost:8501`.

## Usage

* **Add New To-Do:** Use the "Add New To-Do" form at the top. Enter a title, optional description, select a priority, and choose a due date. Click "Add To-Do".
* **View Tasks:** Your tasks will appear in the "Pending Tasks" or "Completed Tasks" sections. Each task will have a background color reflecting its priority.
* **Mark Completed:** Click the "Mark Completed" button next to a pending task to move it to the completed list.
* **Translate Task:** Use the "Translate to <language>" button to get a real-time translation of the task's title, description, priority, and due date.
* **Delete Task:** Click the "Delete" button to remove a task permanently from the database.

## Project Structure