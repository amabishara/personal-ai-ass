import streamlit as st

from modules.ai_engine import get_ai_response
from modules.auth import decode_token, login_user, register_user
from modules.database import Base, engine
from modules.notes import create_note, get_notes
from modules.personalization import get_user_preferences, update_user_preferences
from modules.reader import create_reader_entry, get_reader_entries
from modules.tasks import complete_task, create_task, get_tasks

Base.metadata.create_all(bind=engine)

st.set_page_config(page_title="Personal AI Assistant", page_icon="🧠", layout="wide")
st.title("🧠 Personalized AI Assistant")


def build_task_context(tasks):
    if not tasks:
        return "No tasks saved."
    return "\n".join(
        f"- {task.title}: {task.description or 'No description'}" for task in tasks
    )


def build_reader_context(reader_entries):
    if not reader_entries:
        return "No Digital Body Language passages saved."

    latest_entry = reader_entries[0]
    preview = latest_entry.content[:1800]
    return (
        f"Latest Digital Body Language passage title: {latest_entry.title}\n"
        f"Book: {latest_entry.book_title}\n"
        f"Passage:\n{preview}"
    )


def run_reader_analysis(entry, analysis_type, preferences):
    prompts = {
        "Summary": "Summarize this passage in a practical, easy-to-review way.",
        "Key lessons": (
            "Extract the key communication lessons from this passage and explain why they matter."
        ),
        "Practical tips": (
            "Turn this passage into practical digital communication tips I can apply in real life."
        ),
    }

    context = (
        f"User preferences: {preferences}\n"
        f"Book: {entry.book_title}\n"
        f"Passage title: {entry.title}\n"
        f"Passage content:\n{entry.content}"
    )
    return get_ai_response(
        prompts[analysis_type],
        user_context=context,
        assistant_role="You are a communication coach helping the user study Digital Body Language.",
    )


def ensure_chat_state():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []


menu = st.sidebar.radio("Navigation", ["Login", "Register", "Dashboard"])

if menu == "Register":
    spacer_left, main_col, spacer_right = st.columns([1, 2, 1])
    with main_col:
        st.markdown(
            '<h2 style="text-align: center; color: #4CAF50;">Create your account</h2>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="text-align: center; color: #666;">Start managing your tasks, notes, and reading insights.</p>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            with st.form("register_form", clear_on_submit=True):
                name = st.text_input("Full Name", placeholder="e.g. Ahmed Mohamed")
                email = st.text_input("Email Address", placeholder="name@example.com")
                password = st.text_input(
                    "Create Password",
                    type="password",
                    placeholder="Choose a strong password",
                )
                submitted = st.form_submit_button(
                    "Create My Account",
                    use_container_width=True,
                    type="primary",
                )

                if submitted:
                    if name and email and password:
                        with st.spinner("Setting up your profile..."):
                            try:
                                register_user(name, email, password)
                                st.success("Account created successfully.")
                                st.info("Switch to the Login page from the sidebar.")
                            except Exception:
                                st.error("Registration failed. This email may already be in use.")
                    else:
                        st.warning("Please fill out all fields.")

elif menu == "Login":
    spacer_left, main_col, spacer_right = st.columns([1, 2, 1])
    with main_col:
        st.markdown(
            '<h2 style="text-align: center; color: #4CAF50;">Welcome back</h2>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="text-align: center; color: #666;">Sign in to open your workspace.</p>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email Address", placeholder="name@example.com")
                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                )
                submitted = st.form_submit_button(
                    "Login to Dashboard",
                    use_container_width=True,
                    type="primary",
                )

                if submitted:
                    if not email or not password:
                        st.warning("Please fill in all fields.")
                    else:
                        with st.spinner("Authenticating..."):
                            token = login_user(email, password)
                            if token:
                                st.session_state["token"] = token
                                st.success("Login successful.")
                                st.info("Open Dashboard from the sidebar.")
                            else:
                                st.error("Invalid email or password.")

elif menu == "Dashboard":
    if "token" not in st.session_state:
        st.warning("Please log in first to access your personal workspace.")
        st.stop()

    payload = decode_token(st.session_state["token"])
    if not payload:
        st.error("Your session has expired. Please log in again.")
        if st.button("Clear session and go back"):
            st.session_state.clear()
            st.rerun()
        st.stop()

    user_id = payload["user_id"]
    ensure_chat_state()

    tasks = get_tasks(user_id)
    notes = get_notes(user_id)
    reader_entries = get_reader_entries(user_id)
    current_preferences = get_user_preferences(user_id)

    if "reader_analysis" not in st.session_state:
        st.session_state["reader_analysis"] = ""

    left_col, right_col = st.columns([1, 1.35], gap="large")

    with left_col:
        st.subheader("Your Tasks")
        with st.container(border=True):
            with st.form("task_form", clear_on_submit=True):
                task_title = st.text_input("New Task Title")
                task_description = st.text_area("Task Description")
                submit_task = st.form_submit_button(
                    "Add Task",
                    use_container_width=True,
                    type="primary",
                )

                if submit_task:
                    if task_title.strip():
                        create_task(task_title.strip(), task_description.strip(), user_id)
                        st.success("Task added successfully.")
                        st.rerun()
                    else:
                        st.warning("Task title is required.")

        pending_tasks = [task for task in tasks if task.status == "pending"]
        if pending_tasks:
            for task in pending_tasks:
                task_col, button_col = st.columns([3, 1])
                task_col.write(f"**{task.title}**")
                if task.description:
                    task_col.caption(task.description)
                if button_col.button("Done", key=f"task_{task.id}"):
                    complete_task(task.id)
                    st.rerun()
        else:
            st.caption("No pending tasks yet.")

        st.markdown("---")
        st.subheader("Your Notes")
        with st.form("note_form", clear_on_submit=True):
            note_content = st.text_area("New Note", height=120)
            submit_note = st.form_submit_button(
                "Save Note",
                use_container_width=True,
                type="primary",
            )
            if submit_note:
                if note_content.strip():
                    create_note(note_content.strip(), user_id)
                    st.success("Note saved.")
                    st.rerun()
                else:
                    st.warning("Write a note before saving.")

        if notes:
            for note in notes:
                st.info(note.content)
        else:
            st.caption("No notes saved yet.")

        st.markdown("---")
        st.subheader("Digital Body Language Reader")
        with st.container(border=True):
            st.caption(
                "Paste your own notes, excerpts, or examples from Digital Body Language to save them here."
            )
            with st.form("reader_form", clear_on_submit=True):
                reader_title = st.text_input(
                    "Passage title",
                    placeholder="Example: Chapter 2 - Building trust online",
                )
                reader_content = st.text_area(
                    "Passage or notes",
                    height=220,
                    placeholder="Paste the excerpt or your personal notes here...",
                )
                save_reader_entry = st.form_submit_button(
                    "Save to Reader",
                    use_container_width=True,
                    type="primary",
                )

                if save_reader_entry:
                    if reader_content.strip():
                        create_reader_entry(
                            reader_title.strip() or "Untitled passage",
                            reader_content.strip(),
                            user_id,
                        )
                        st.success("Digital Body Language passage saved.")
                        st.rerun()
                    else:
                        st.warning("Paste a passage or your notes before saving.")

        if reader_entries:
            st.caption("Saved passages")
            for entry in reader_entries[:5]:
                created_at = (
                    entry.created_at.strftime("%Y-%m-%d %H:%M")
                    if entry.created_at
                    else "Saved recently"
                )
                with st.expander(f"{entry.title} - {created_at}"):
                    st.write(entry.content)
        else:
            st.caption("No Digital Body Language passages saved yet.")

    with right_col:
        st.subheader("AI Personal Assistant")
        with st.expander("Personalization & Memory Settings", expanded=True):
            updated_preferences = st.text_area(
                "Define AI Behavior",
                value=current_preferences,
                placeholder="Example: Speak to me as a senior software engineer and keep answers concise.",
                height=150,
            )
            if st.button("Update AI Memory", use_container_width=True, type="primary"):
                update_user_preferences(user_id, updated_preferences)
                st.success("Preferences updated.")
                st.rerun()

        st.markdown("---")
        st.subheader("Reader Assistant")
        if reader_entries:
            reader_lookup = {entry.id: entry for entry in reader_entries}
            selected_reader_id = st.selectbox(
                "Choose a saved passage",
                options=list(reader_lookup.keys()),
                format_func=lambda entry_id: (
                    f"{reader_lookup[entry_id].title} - "
                    f"{reader_lookup[entry_id].created_at.strftime('%Y-%m-%d %H:%M') if reader_lookup[entry_id].created_at else 'Saved recently'}"
                ),
            )
            analysis_type = st.radio(
                "What should the reader do?",
                ["Summary", "Key lessons", "Practical tips"],
                horizontal=True,
            )

            selected_entry = reader_lookup[selected_reader_id]
            st.caption(f"Book: {selected_entry.book_title}")
            preview = selected_entry.content[:500]
            if len(selected_entry.content) > 500:
                preview += "..."
            st.write(preview)

            if st.button("Analyze saved passage", use_container_width=True, type="primary"):
                with st.spinner("Reading and analyzing your passage..."):
                    st.session_state["reader_analysis"] = run_reader_analysis(
                        selected_entry,
                        analysis_type,
                        current_preferences,
                    )

            if st.session_state["reader_analysis"]:
                with st.container(border=True):
                    st.markdown(st.session_state["reader_analysis"])
        else:
            st.info("Save a passage in the Digital Body Language Reader to unlock analysis.")

        st.markdown("---")
        st.subheader("Chat with your Assistant")
        with st.container(border=True):
            if st.session_state["chat_history"]:
                for message in st.session_state["chat_history"]:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            else:
                st.caption("Ask about your tasks, notes, or your latest Digital Body Language passage.")

        user_input = st.chat_input("Ask me anything about your work, notes, or reading...")
        if user_input:
            st.session_state["chat_history"].append({"role": "user", "content": user_input})

            with st.spinner("Thinking..."):
                full_context = (
                    f"User Preferences:\n{current_preferences}\n\n"
                    f"Current Tasks:\n{build_task_context(tasks)}\n\n"
                    f"Reading Context:\n{build_reader_context(reader_entries)}"
                )
                response = get_ai_response(user_input, user_context=full_context)

            st.session_state["chat_history"].append({"role": "assistant", "content": response})
            st.rerun()
