import streamlit as st
import requests
from typing import List, Dict, Optional
from datetime import date # Import date for handling due dates

# Configuration for the FastAPI backend
FASTAPI_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Streamlit To-Do App", layout="wide")
st.title("Simple To-Do List")

# --- Initialize session state for translations ---
if 'translations' not in st.session_state:
    st.session_state.translations = {} # {todo_id: {language: translated_text}}


# --- Helper Functions to interact with Backend ---

def get_todos() -> List[Dict]:
    """Fetches all to-do items from the backend."""
    try:
        response = requests.get(f"{FASTAPI_BASE_URL}/todos")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend. Please ensure the FastAPI backend is running.")
        return []
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching todos: {e}")
        return []

def add_todo_to_backend(title: str, description: Optional[str] = None,
                        priority: Optional[str] = None, due_date: Optional[date] = None) -> bool:
    """Adds a new to-do item to the backend. Returns True on success, False on failure."""
    data = {"title": title}
    if description:
        data["description"] = description
    if priority:
        data["priority"] = priority
    if due_date:
        data["due_date"] = str(due_date) # Convert date object to string for JSON
    try:
        response = requests.post(f"{FASTAPI_BASE_URL}/todos", json=data)
        response.raise_for_status()
        st.success("To-Do item added successfully!")
        return True
    except requests.exceptions.RequestException as e:
        st.error(f"Error adding todo: {e}")
        return False

def mark_todo_completed(todo_id: int):
    """Marks a to-do item as completed in the backend."""
    data = {"completed": True}
    try:
        response = requests.put(f"{FASTAPI_BASE_URL}/todos/{todo_id}", json=data)
        response.raise_for_status()
        st.success(f"To-Do item {todo_id} marked as completed!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error marking todo as completed: {e}")

def delete_todo_item(todo_id: int):
    """Deletes a to-do item from the backend."""
    try:
        response = requests.delete(f"{FASTAPI_BASE_URL}/todos/{todo_id}")
        response.raise_for_status()
        st.success(f"To-Do item {todo_id} deleted successfully!")
    except requests.exceptions.RequestException as e:
        st.error(f"Error deleting todo: {e}")

def translate_text_on_backend(text: str, target_language: str) -> Optional[str]:
    """Sends text to backend for translation using Gemini."""
    data = {"text": text, "target_language": target_language}
    try:
        response = requests.post(f"{FASTAPI_BASE_URL}/translate", json=data)
        response.raise_for_status()
        return response.json().get("translated_text")
    except requests.exceptions.RequestException as e:
        st.error(f"Error translating text: {e}. Check backend logs for details.")
        return None

# --- Streamlit UI ---

st.sidebar.header("Translation Settings")
LANGUAGES = {
    "English": "English",
    "Spanish": "Spanish",
    "French": "French",
    "German": "German",
    "Hindi": "Hindi",
    "Marathi": "Marathi",
    "Japanese": "Japanese",
    "Chinese (Simplified)": "Chinese (Simplified)",
    "Korean": "Korean",
    "Portuguese": "Portuguese"
}
selected_language_name = st.sidebar.selectbox(
    "Translate to:",
    list(LANGUAGES.keys()),
    index=0
)
target_language = LANGUAGES[selected_language_name]


# Add New To-Do Item
st.header("Add New To-Do")
with st.form("add_todo_form", clear_on_submit=True):
    new_title = st.text_input(
        "Title",
        key="add_todo_title_input"
    )
    new_description = st.text_area(
        "Description (optional)",
        key="add_todo_description_input"
    )
    new_priority = st.selectbox(
        "Priority",
        ["None", "Low", "Medium", "High"],
        key="add_todo_priority_input"
    )
    new_due_date = st.date_input(
        "Due Date (optional)",
        min_value=date.today(), # ⭐ MODIFIED: Use date.today() for dynamic minimum date
        value=None,
        key="add_todo_due_date_input"
    )

    add_button = st.form_submit_button("Add To-Do")

    if add_button:
        submitted_title = new_title
        submitted_description = new_description
        submitted_priority = new_priority if new_priority != "None" else None
        submitted_due_date = new_due_date

        if submitted_title:
            success = add_todo_to_backend(
                submitted_title,
                submitted_description,
                submitted_priority,
                submitted_due_date
            )
            if success:
                pass
        else:
            st.warning("Please enter a title for the To-Do item.")

st.markdown("---")

# List Existing To-Do Items
st.header("Your To-Do List")
todos = get_todos()

if todos:
    incomplete_todos = [todo for todo in todos if not todo.get("completed")]
    completed_todos = [todo for todo in todos if todo.get("completed")]

    if incomplete_todos:
        st.subheader("Pending Tasks")
        task_number = 1
        for todo in incomplete_todos:
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([0.5, 0.2, 0.2, 0.1])
                with col1:
                    st.markdown(f"**{task_number}. {todo.get('title')}**")
                    if todo.get("description"):
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;_{todo.get('description')}_")
                    if todo.get("priority"):
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**Priority:** {todo['priority']}")
                    if todo.get("due_date"):
                        st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;**Due:** {todo['due_date']}")

                    if todo.get('id') in st.session_state.translations and \
                       target_language in st.session_state.translations[todo.get('id')]:
                        st.markdown(f"**Translated ({selected_language_name}):** *{st.session_state.translations[todo.get('id')][target_language]}*")

                with col2:
                    if st.button("Mark Completed", key=f"complete_{todo.get('id')}"):
                        mark_todo_completed(todo.get("id"))
                        st.rerun()
                with col3:
                    if st.button(f"Translate to {selected_language_name}", key=f"translate_{todo.get('id')}"):
                        text_to_translate = todo.get("title")
                        if todo.get("description"):
                            text_to_translate += f" (Description: {todo.get('description')})"
                        if todo.get("priority"):
                            text_to_translate += f" (Priority: {todo['priority']})"
                        if todo.get("due_date"):
                            text_to_translate += f" (Due Date: {todo['due_date']})"


                        translated_text = translate_text_on_backend(text_to_translate, target_language)
                        if translated_text:
                            if todo.get('id') not in st.session_state.translations:
                                st.session_state.translations[todo.get('id')] = {}
                            st.session_state.translations[todo.get('id')][target_language] = translated_text
                            st.rerun()
                with col4:
                    if st.button("Delete", key=f"delete_incomplete_{todo.get('id')}"):
                        delete_todo_item(todo.get("id"))
                        if todo.get('id') in st.session_state.translations:
                            del st.session_state.translations[todo.get('id')]
                        st.rerun()
            st.divider()
            task_number += 1

    if completed_todos:
        st.subheader("Completed Tasks")
        completed_task_number = 1
        for todo in completed_todos:
            with st.container(border=True):
                col1, col2, col3 = st.columns([0.7, 0.2, 0.1])
                with col1:
                    st.markdown(f"<del>**{completed_task_number}. {todo.get('title')}**</del>", unsafe_allow_html=True)
                    if todo.get("description"):
                        st.markdown(f"<del>&nbsp;&nbsp;&nbsp;&nbsp;_{todo.get('description')}_</del>", unsafe_allow_html=True)
                    if todo.get("priority"):
                        st.markdown(f"<del>&nbsp;&nbsp;&nbsp;&nbsp;**Priority:** {todo['priority']}</del>", unsafe_allow_html=True)
                    if todo.get("due_date"):
                        st.markdown(f"<del>&nbsp;&nbsp;&nbsp;&nbsp;**Due:** {todo['due_date']}</del>", unsafe_allow_html=True)

                    if todo.get('id') in st.session_state.translations and \
                       target_language in st.session_state.translations[todo.get('id')]:
                        st.markdown(f"<del>**Translated ({selected_language_name}):** *{st.session_state.translations[todo.get('id')][target_language]}*</del>", unsafe_allow_html=True)
                with col2:
                    pass
                with col3:
                    if st.button("Delete", key=f"delete_completed_{todo.get('id')}"):
                        delete_todo_item(todo.get("id"))
                        if todo.get('id') in st.session_state.translations:
                            del st.session_state.translations[todo.get('id')]
                        st.rerun()
            st.divider()
            completed_task_number += 1
else:
    st.info("No To-Do items yet! Add one above.")