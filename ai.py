import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def get_ai_advice(tasks, deadline, hours):

    

    prompt = f"""

You are Zenflow, an AI productivity coach.

Analyze the user's tasks:

Tasks:
{tasks}

Deadline:
{deadline}

Available time:
{hours}


Your job:
Create a short, clean productivity plan.

Rules:
- Use short sentences only.
- Maximum 1-2 lines per point.
- Add blank lines between every section.
- Never write long paragraphs.
- Keep it visually clean.
- Do not repeat information.
- make important keywords bold like why and the reason etc


Return exactly in this format:


## 🎯 Today's Focus


🔥 Priority 1

Task:
(task name)

Why:
(short reason)



🟡 Priority 2

Task:
(task name)

Why:
(short reason)



🟢 Priority 3

Task:
(task name)

Why:
(short reason)




## ⏰ Suggested Schedule


🕘 8:00 AM
(task)


🕙 10:00 AM
(task)




## ⚠️ Deadline Risk


Risk:
Low / Medium / High


Reason:
(one short sentence)




## 💡 Coach Tip


(one motivational sentence)


"""


    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )
    formatted = f"""
## 🧠 Your AI Plan

{response.choices[0].message.content}

---

### 🚀 Action Tip

Start with the highest priority task first.
"""

    return formatted





def get_schedule_suggestion(tasks, deadline, hours):


    prompt = f"""

Create a simple study/work schedule.

Tasks:
{tasks}

Deadline:
{deadline}

Available hours:
{hours}


Give:

📅 Smart Schedule

with time blocks.

"""


    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]

    )


    return response.choices[0].message.content


def get_deadline_risk(tasks, deadline, hours):


    task_list = tasks.splitlines()


    total_tasks = len(
        [t for t in task_list if t.strip()]
    )


    available_hours = int(hours) if hours.isdigit() else 0


    if total_tasks == 0:

        return """
⏰ Deadline Risk Analysis

No tasks added yet.
"""


    if available_hours < total_tasks:

        risk = "🔴 HIGH"

        advice = (
            "You have more tasks than available time. "
            "Complete urgent tasks first."
        )


    elif available_hours == total_tasks:

        risk = "🟡 MEDIUM"

        advice = (
            "Your schedule is tight. "
            "Avoid distractions."
        )


    else:

        risk = "🟢 LOW"

        advice = (
            "Your workload looks manageable."
        )



    return f"""

⏰ Deadline Risk Analysis


Risk Level:

{risk}


Tasks:

{total_tasks}


Available Hours:

{available_hours}


💡 Advice:

{advice}

"""
def get_task_priority(tasks):

    prompt = f"""
Analyze these tasks:

{tasks}

Return ONLY:

High:
task1, task2

Medium:
task1, task2

Low:
task1, task2
"""


    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )


    return response.choices[0].message.content