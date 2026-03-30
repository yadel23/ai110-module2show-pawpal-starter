import streamlit as st
from datetime import date, time
from models import Owner, Pet, PetTask, TaskType, TimeWindow, OwnerPreferences, SchedulingRules
from taskScheduler import TaskScheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.error("Please add at least one task.")
    else:
        # Create owner with default availability
        owner_preferences = OwnerPreferences(
            preferred_times=[TimeWindow(time(9, 0), time(12, 0))],
            quiet_hrs=[TimeWindow(time(23, 0), time(7, 0))]
        )
        owner = Owner(
            name=owner_name,
            availability=[TimeWindow(time(8, 0), time(12, 0)), TimeWindow(time(14, 0), time(18, 0))],
            preferences=owner_preferences
        )

        # Create pet
        pet = Pet(name=pet_name, species=species, age=2)

        # Convert tasks to PetTask
        pet_tasks = []
        priority_map = {"low": 1, "medium": 3, "high": 5}
        for i, task_dict in enumerate(st.session_state.tasks):
            task_type = TaskType.WALK  # Default, could be smarter
            if "feed" in task_dict["title"].lower():
                task_type = TaskType.FEED
            elif "med" in task_dict["title"].lower():
                task_type = TaskType.MEDS
            pet_task = PetTask(
                task_id=f"task_{i}",
                title=task_dict["title"],
                task_type=task_type,
                duration_min=task_dict["duration_minutes"],
                priority=priority_map[task_dict["priority"]],
                mandatory=task_dict["priority"] == "high"
            )
            pet_tasks.append(pet_task)

        # Create scheduler
        rules = SchedulingRules()
        scheduler = TaskScheduler(rules)

        # Generate schedule
        today = date.today()
        schedule = scheduler.generate(owner, pet, pet_tasks, today)

        # Display results
        st.success(f"Schedule generated for {schedule.date.strftime('%Y-%m-%d')}")

        if schedule.items:
            st.subheader("Scheduled Tasks")
            schedule_data = []
            for item in schedule.items:
                schedule_data.append({
                    "Time": f"{item.start.strftime('%H:%M')} - {item.end.strftime('%H:%M')}",
                    "Task": item.task.title,
                    "Duration": f"{item.duration_minutes()} min",
                    "Priority": item.task.priority,
                    "Reason": item.reason
                })
            st.table(schedule_data)
        else:
            st.warning("No tasks could be scheduled.")

        if schedule.notes:
            st.subheader("Notes")
            for note in schedule.notes:
                st.write(f"- {note}")

        st.subheader("Summary")
        st.write(f"Total scheduled time: {schedule.total_minutes_scheduled()} minutes")
        st.write(f"Mandatory tasks: {len(schedule.get_mandatory_tasks())}")
        st.write(f"Optional tasks: {len(schedule.get_optional_tasks())}")
