import sqlite3


def create_table():

    conn = sqlite3.connect("tasks.db")

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks
    (
        id INTEGER PRIMARY KEY,
        task TEXT,
        status TEXT,
        priority TEXT
    )
    """)

    conn.commit()
    conn.close()

def add_task(task, priority):
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()

    # ✅ Check if task already exists before inserting
    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE task = ? AND status = 'Pending'",
        (task,)
    )
    exists = cursor.fetchone()[0]

    if not exists:
        cursor.execute(
            "INSERT INTO tasks(task,status,priority) VALUES (?, ?, ?)",
            (task, "Pending", priority)
        )
        conn.commit()

    conn.close()



def get_tasks():

    conn = sqlite3.connect("tasks.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT task,status,priority FROM tasks"
    )

    tasks = cursor.fetchall()

    conn.close()

    return tasks



# 👇 ADD FROM HERE

def get_priority_count():

    conn = sqlite3.connect("tasks.db")

    cursor = conn.cursor()

    cursor.execute(
        "SELECT priority, COUNT(*) FROM tasks GROUP BY priority"
    )

    result = cursor.fetchall()

    conn.close()

    return result



def complete_task(task_name):

    conn = sqlite3.connect("tasks.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE tasks
        SET status = ?
        WHERE task = ?
        """,
        ("Completed", task_name)
    )

    conn.commit()

    conn.close()



def get_progress():

    conn = sqlite3.connect("tasks.db")

    cursor = conn.cursor()


    cursor.execute(
        "SELECT COUNT(*) FROM tasks"
    )

    total = cursor.fetchone()[0]


    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
    )

    completed = cursor.fetchone()[0]


    conn.close()


    return completed, total

def get_priority_tasks(priority):

    conn = sqlite3.connect("tasks.db")

    cursor = conn.cursor()


    cursor.execute(
    """
    SELECT task
    FROM tasks
    WHERE priority=?
    AND status='Pending'
    """,
    (priority,)
)


    tasks = cursor.fetchall()


    conn.close()


    return tasks

def clear_completed_tasks():

    conn = sqlite3.connect("tasks.db")

    cursor = conn.cursor()


    cursor.execute(
        """
        DELETE FROM tasks
        WHERE status='Completed'
        """
    )


    conn.commit()

    conn.close()

def create_calendar_table():

    conn = sqlite3.connect("tasks.db")

    cursor = conn.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS calendar
        (
            id INTEGER PRIMARY KEY,
            event TEXT,
            date TEXT,
            time TEXT
        )
        """
    )


    conn.commit()

    conn.close()
def add_calendar_event(event, date, time):

    conn = sqlite3.connect("tasks.db")

    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT INTO calendar(event,date,time)
        VALUES (?,?,?)
        """,
        (
            event,
            date,
            time
        )
    )


    conn.commit()

    conn.close()
def get_calendar_events():

    conn = sqlite3.connect("tasks.db")

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT event,date,time
        FROM calendar
        ORDER BY date
        """
    )


    events = cursor.fetchall()


    conn.close()


    return events
def get_productivity_stats():

    conn = sqlite3.connect("tasks.db")

    cursor = conn.cursor()


    cursor.execute(
        "SELECT COUNT(*) FROM tasks"
    )

    total = cursor.fetchone()[0]


    cursor.execute(
        """
        SELECT COUNT(*) 
        FROM tasks
        WHERE status='Completed'
        """
    )

    completed = cursor.fetchone()[0]


    cursor.execute(
        """
        SELECT priority, COUNT(*)
        FROM tasks
        GROUP BY priority
        """
    )


    priorities = cursor.fetchall()


    conn.close()


    return total, completed, priorities
def get_streak():
    conn = sqlite3.connect("tasks.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM tasks WHERE status='Completed'"
    )
    completed = cursor.fetchone()[0]
    conn.close()
    # Every 3 completed tasks = 1 streak day
    return max(1, completed // 3)
