import streamlit as st
import time
import pandas as pd
import requests
from datetime import datetime

st.markdown(
"""
<style>

body {
    background-color: #f8faff;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #eef2ff, #fdf2f8, #ecfeff);
}

.card {
    background: rgba(255,255,255,0.85);
    padding: 14px;
    border-radius: 22px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

h1 { color: #1e293b; }
h2 { color: #334155; }

.stButton button {
    border-radius: 15px;
    height: 45px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    font-weight: 600;
}

.stButton button:hover {
    transform: scale(1.02);
}

[data-testid="metric-container"] {
    background: white;
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #eef2ff, #ffffff);
}

</style>
""",
unsafe_allow_html=True
)

from ai import (
    get_ai_advice,
    get_schedule_suggestion,
    get_deadline_risk,
    get_task_priority
)
from database import (
    create_table,
    add_task,
    get_tasks,
    get_priority_count,
    complete_task,
    get_progress,
    get_priority_tasks,
    clear_completed_tasks,
    create_calendar_table,
    add_calendar_event,
    get_calendar_events,
    get_productivity_stats,
    get_streak
)
create_table()
create_calendar_table()

# ── Sidebar ──────────────────────────────────────────────
high_count = len(get_priority_tasks("High"))
title = f"🚀 Planner Menu 🔔 {high_count}" if high_count > 0 else "🚀 Planner Menu"
st.sidebar.title(title)
page = st.sidebar.radio(
    "Go to",
    ["🏠 Dashboard", "📝 Tasks", "📅 Calendar", "📊 Progress"]
)

# ── Reminders in Sidebar ──
st.sidebar.divider()
st.sidebar.markdown("### 🔔 Reminders")

from database import get_priority_tasks
high_reminders = get_priority_tasks("High")
medium_reminders = get_priority_tasks("Medium")

if high_reminders:
    st.sidebar.error("🔥 Urgent Tasks Pending!")
    for t in high_reminders:
        st.sidebar.warning(f"⚡ {t[0]}")
elif medium_reminders:
    st.sidebar.info("🟡 You have pending tasks")
    for t in medium_reminders[:3]:
        st.sidebar.info(f"📌 {t[0]}")
else:
    st.sidebar.success("✅ All caught up!")

show_dashboard = page == "🏠 Dashboard"
show_tasks     = page == "📝 Tasks"
show_calendar  = page == "📅 Calendar"
show_progress  = page == "📊 Progress"

# Default values to avoid NameError on other pages
tasks          = ""
deadline       = ""
available_time = ""

@st.cache_data(ttl=600)
def get_cached_advice(tasks, deadline, hours):
    return get_ai_advice(tasks, deadline, hours)


# ══════════════════════════════════════════════════════════
# 🏠 DASHBOARD
# ══════════════════════════════════════════════════════════
if show_dashboard:

    

    # Hero card
    st.markdown(
        """
        <div class="card">
        <h1>🌿 Zenflow</h1>
        <h3>Your AI Productivity Coach 🚀</h3>
        <p>Focus deeply • Achieve calmly • Finish faster</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Greeting
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good Morning ☀️"
    elif hour < 18:
        greeting = "Good Afternoon 🌤️"
    else:
        greeting = "Good Evening 🌙"
    st.info(greeting)

    # ── Reminder Banner ──
    high_pending = get_priority_tasks("High")
    if high_pending:
        task_names = ", ".join([t[0] for t in high_pending[:3]])
        st.error(
            f"🔔 **Reminder:** You have {len(high_pending)} urgent task(s) pending → {task_names}"
        )
    # Motivational quote
    try:
        quote = requests.get("https://zenquotes.io/api/random", timeout=3).json()
        st.success(f'💭 "{quote[0]["q"]}" — {quote[0]["a"]}')
    except Exception:
        st.success('💭 "Focus on being productive instead of busy." — Tim Ferriss')

    # Task input
    tasks = st.text_area(
        "Enter your tasks (one per line)",
        placeholder="Example:\nFinish assignment\nPay bills\nStudy Python"
    )

    col1, col2 = st.columns(2)
    with col1:
        deadline = st.text_input("📅 Deadline")
    with col2:
        available_time = st.text_input("⏳ Available hours")

    st.divider()

    # ── AI Plan button ────────────────────────────────────
    if st.button("🚀 Create My AI Plan", use_container_width=True):

     with st.spinner("🧠 AI is building your plan..."):
        try:
            answer = get_cached_advice(tasks, deadline, available_time)
            st.success("✨ Your AI plan is ready!")
            st.markdown(answer)
        except Exception as e:
            st.error(f"AI Error: {e}")

    # ✅ INSIDE button — Get AI priority
    if tasks.strip():
        priority_result = get_task_priority(tasks)
        priority_map = {}
        current_priority = ""

        for line in priority_result.split("\n"):
            line = line.strip()
            if line.startswith("High:"):
                current_priority = "High"
            elif line.startswith("Medium:"):
                current_priority = "Medium"
            elif line.startswith("Low:"):
                current_priority = "Low"
            else:
                if current_priority and line:
                    for item in line.split(","):
                        priority_map[item.strip()] = current_priority

        # ✅ INSIDE button — Save tasks
        for t in tasks.split("\n"):
            t = t.strip()
            if t:
                priority = priority_map.get(t, "Medium")
                add_task(t, priority)

    st.divider()

    # ── Today's Focus ─────────────────────────────────────
    st.markdown(
        "<div class='card'><h2>🎯 Today's Focus</h2></div>",
        unsafe_allow_html=True
    )

    high_tasks = get_priority_tasks("High")
    if high_tasks:
        st.subheader("🔥 Start Here")
        for t in high_tasks:
            st.success(f"🎯 {t[0]}\n\n🔥 Important — finish this before easier work.")
    else:
        medium_tasks = get_priority_tasks("Medium")
        if medium_tasks:
            st.write("🟡 Next Best Tasks")
            for t in medium_tasks:
                st.warning(t[0])
        else:
            st.success("🎉 No urgent tasks left!")

    st.divider()

    

    # ── ⏱️ POMODORO TIMER ─────────────────────────────────
    st.markdown(
        "<div class='card'><h2>⏱️ Pomodoro Focus Timer</h2></div>",
        unsafe_allow_html=True
    )
    st.caption("Stay focused. Work in sprints. Achieve more. 🎯")

    col1, col2 = st.columns(2)
    with col1:
        focus_mins = st.selectbox(
            "Focus Duration (mins)",
            [25, 30, 45, 60],
            key="focus_duration"
        )
    with col2:
        break_mins = st.selectbox(
            "Break Duration (mins)",
            [5, 10, 15],
            key="break_duration"
        )

    if st.button("▶️ Start Focus Session", key="pomodoro_btn"):
        total_seconds = focus_mins * 60
        placeholder = st.empty()
        progress_bar = st.progress(0)

        for remaining in range(total_seconds, 0, -1):
            mins = remaining // 60
            secs = remaining % 60
            elapsed = total_seconds - remaining
            progress = elapsed / total_seconds

            placeholder.markdown(
                f"### ⏱️ {mins:02d}:{secs:02d} — Stay focused! 🎯"
            )
            progress_bar.progress(progress)
            time.sleep(1)

        placeholder.markdown("## ✅ Session Complete! Take a break 🌿")
        progress_bar.progress(1.0)
        st.balloons()
        st.success(f"🎉 Great work! Take a {break_mins}-minute break now.")

    st.divider()

    # ── 💬 AI CHAT ASSISTANT ──────────────────────────────
    st.markdown(
        "<div class='card'><h2>💬 Ask Your AI Coach</h2></div>",
        unsafe_allow_html=True
    )
    st.caption("Ask anything about your tasks, focus, or productivity 🤖")

    user_question = st.text_input(
        "Your question",
        placeholder="e.g. What should I focus on first? Am I on track?",
        key="ai_chat_input"
    )

    if st.button("Ask AI 🤖", key="ask_ai_btn"):
        if user_question.strip():
            with st.spinner("🧠 Thinking..."):
                try:
                    from groq import Groq
                    from ai import client as groq_client

                    response = groq_client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {
                                "role": "user",
                                "content": (
                                    f"My current tasks are:\n{tasks}\n\n"
                                    f"My deadline is: {deadline}\n"
                                    f"Available hours: {available_time}\n\n"
                                    f"My question: {user_question}\n\n"
                                    f"Give a short, direct, friendly answer in 2-3 lines only."
                                )
                            }
                        ]
                    )
                    st.success(f"🤖 {response.choices[0].message.content}")
                except Exception as e:
                    st.error(f"AI Error: {e}")
        else:
            st.warning("Please type a question first!")


# ══════════════════════════════════════════════════════════
# 📅 CALENDAR
# ══════════════════════════════════════════════════════════
if show_calendar:

    st.markdown(
        "<div class='card'><h2>📅 Smart Planner</h2></div>",
        unsafe_allow_html=True
    )

    event = st.text_input("Event / Task")
    date  = st.date_input("Select Date")
    calendar_time = st.time_input("Select Time")

    if st.button("➕ Add to Calendar", key="calendar_add_btn"):
        if event.strip():
            add_calendar_event(event, str(date), str(calendar_time))
            st.success("Event added!")
            st.rerun()
        else:
            st.warning("Please enter an event name")

    st.markdown(
        "<div class='card'><h2>📆 Upcoming Events</h2></div>",
        unsafe_allow_html=True
    )

    events = get_calendar_events()
    if events:
        for item in events:
            st.info(f"📌 {item[0]}\n\n📅 {item[1]}\n\n⏰ {item[2]}")
    else:
        st.info("No upcoming events. Add one above!")


# ══════════════════════════════════════════════════════════
# 📊 PROGRESS
# ══════════════════════════════════════════════════════════
if show_progress:

    st.markdown(
        "<div class='card'><h2>📊 Productivity Insights</h2></div>",
        unsafe_allow_html=True
    )

    total, completed, priorities = get_productivity_stats()

    rate  = int((completed / total) * 100) if total > 0 else 0
    score = rate if total > 0 else 0

    if total == 0:
        st.info("🚀 Create your first plan to start tracking productivity")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔥 Productivity Score", f"{score}/100")
        with col2:
            st.metric("✅ Completed", f"{completed} Tasks")
        with col3:
           streak = get_streak()
           st.metric("🔥 Streak", f"Day {streak}", "Keep going!")
    st.markdown(
    f"""
    <div style="background:#e2e8f0; border-radius:10px; height:12px;">
    <div style="background:linear-gradient(90deg,#6366f1,#8b5cf6);
    width:{rate}%; height:12px; border-radius:10px;"></div>
    </div>
    """,
    unsafe_allow_html=True
)

    if total == 0:
        pass
    elif rate >= 80:
        st.success("🔥 Excellent productivity today!")
    elif rate >= 50:
        st.info("💪 Good progress. Keep going!")
    else:
        st.warning("🚀 Start with your highest priority task.")

    st.caption(f"You completed {rate}% of today's tasks 🚀")
    st.caption(f"Completed: {completed}/{total} tasks")

    # Priority Distribution Chart
    st.write("### Priority Distribution")
    import plotly.express as px

    priority_labels = []
    priority_values = []

    for item in priorities:
        if item[0] == "High":
            priority_labels.append("🔥 High")
            priority_values.append(item[1])
        elif item[0] == "Medium":
            priority_labels.append("🟡 Medium")
            priority_values.append(item[1])
        else:
            priority_labels.append("🟢 Low")
            priority_values.append(item[1])

    if priority_values:
        fig = px.pie(
            values=priority_values,
            names=priority_labels,
            color_discrete_sequence=["#fca5a5", "#fcd34d", "#86efac"],
            hole=0.4
        )
        fig.update_layout(
            showlegend=True,
            margin=dict(t=20, b=20, l=20, r=20),
            width=350,
            height=300
        )
        st.plotly_chart(fig, use_container_width=False)
    else:
        st.info("No tasks yet to show chart.")

    st.write(f"{completed} Completed / {total} Total Tasks")



# ══════════════════════════════════════════════════════════
# 📝 TASKS
# ══════════════════════════════════════════════════════════
if show_tasks:

    st.markdown(
        "<div class='card'><h2>📋 Task History</h2></div>",
        unsafe_allow_html=True
    )

    # ── 📥 Export CSV ─────────────────────────────────────
    saved_tasks = get_tasks()

    if saved_tasks:
        df  = pd.DataFrame(saved_tasks, columns=["Task", "Status", "Priority"])
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Tasks as CSV",
            data=csv,
            file_name="zenflow_tasks.csv",
            mime="text/csv",
            key="download_csv_btn"
        )

    if st.button("🗑 Clear Completed Tasks", key="clear_tasks_btn"):
        clear_completed_tasks()
        st.success("Completed tasks removed!")
        st.rerun()

    if saved_tasks:
        for task in saved_tasks:
            task_name = task[0]
            status    = task[1]
            priority  = task[2]

            with st.container():
                st.markdown("---")
                col1, col2 = st.columns([4, 1])

                with col1:
                    icon = "🔥" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
                    st.markdown(f"#### {icon} {task_name}")
                    st.write(f"Status: {status}")
                    st.write(f"Priority: {priority}")

                with col2:
                    if status == "Pending":
                        if st.button(
                            "✅ Complete",
                            key=f"complete_{task_name}_{priority}_{status}"
                        ):
                            complete_task(task_name)
                            st.rerun()
    else:
        st.info("No tasks yet. Go to Dashboard to add tasks!")


# ── Footer ────────────────────────────────────────────────
st.divider()
st.caption("Don't just plan it. Build it. 💫")