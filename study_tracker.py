"""
Study Session Tracker
A command-line tool that logs study sessions to a real database, so the data
is saved permanently between runs, and shows stats on time spent per subject.
Includes a live timer so you can start and stop a session in real time.
"""

import sqlite3
import time
from datetime import datetime


DB_FILE = "study_sessions.db"


def setup_database():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            minutes INTEGER NOT NULL,
            date TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()


def normalize_subject(subject: str) -> str:
    return subject.strip().title()


def add_session(subject: str, minutes: int):
    subject = normalize_subject(subject)
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "INSERT INTO sessions (subject, minutes, date) VALUES (?, ?, ?)",
        (subject, minutes, today)
    )
    connection.commit()
    connection.close()


def get_all_sessions():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("SELECT subject, minutes, date FROM sessions ORDER BY date DESC")
    rows = cursor.fetchall()
    connection.close()
    return rows


def get_sessions_for_subject(subject: str):
    subject = normalize_subject(subject)
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute(
        "SELECT subject, minutes, date FROM sessions WHERE subject = ? ORDER BY date DESC",
        (subject,)
    )
    rows = cursor.fetchall()
    connection.close()
    return rows


def get_totals_by_subject():
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT subject, SUM(minutes) as total_minutes, COUNT(*) as session_count
        FROM sessions
        GROUP BY subject
        ORDER BY total_minutes DESC
    """)
    rows = cursor.fetchall()
    connection.close()
    return rows


def show_all_sessions():
    rows = get_all_sessions()
    if not rows:
        print("\nNo sessions logged yet.\n")
        return

    print("\nAll Study Sessions")
    for subject, minutes, date in rows:
        print(f"  {date} - {subject}: {minutes} minutes")
    print()


def show_sessions_for_subject():
    subject = input("Which subject do you want to view? ").strip()
    if subject == "":
        print("Subject cannot be empty.\n")
        return

    rows = get_sessions_for_subject(subject)
    if not rows:
        print(f"\nNo sessions found for {normalize_subject(subject)}.\n")
        return

    print(f"\nSessions for {normalize_subject(subject)}")
    for subj, minutes, date in rows:
        print(f"  {date}: {minutes} minutes")
    print()


def show_totals():
    rows = get_totals_by_subject()
    if not rows:
        print("\nNo sessions logged yet.\n")
        return

    print("\nTotal Time By Subject")
    for subject, total_minutes, session_count in rows:
        hours = total_minutes // 60
        minutes = total_minutes % 60
        average = round(total_minutes / session_count)
        print(f"  {subject}: {hours}h {minutes}m total, "
              f"across {session_count} session(s), "
              f"averaging {average} minutes per session")

    top_subject, top_minutes, _ = rows[0]
    print(f"\n  Most studied subject: {top_subject} ({top_minutes} minutes)")
    print()


def log_session_manually():
    subject = input("Which subject did you study? ").strip()
    if subject == "":
        print("Subject cannot be empty.\n")
        return

    minutes_input = input("How many minutes did you study? ").strip()
    if not minutes_input.isdigit():
        print("Please enter a valid number of minutes.\n")
        return

    minutes = int(minutes_input)
    add_session(subject, minutes)
    print(f"Logged {minutes} minutes of {normalize_subject(subject)}.\n")


def run_live_timer():
    subject = input("Which subject are you starting? ").strip()
    if subject == "":
        print("Subject cannot be empty.\n")
        return

    input(f"Press Enter to START studying {normalize_subject(subject)}...")
    start_time = time.time()
    print("Timer running. Press Enter again when you're done.")

    input()
    end_time = time.time()

    elapsed_seconds = end_time - start_time
    elapsed_minutes = round(elapsed_seconds / 60)

    if elapsed_minutes < 1:
        print("That session was too short to log (less than 1 minute).\n")
        return

    add_session(subject, elapsed_minutes)
    print(f"Session finished. Logged {elapsed_minutes} minutes of {normalize_subject(subject)}.\n")


def main():
    setup_database()
    print("Study Session Tracker")

    while True:
        print("What would you like to do?")
        print("  1. Start a live timed session")
        print("  2. Log a session manually (type in minutes)")
        print("  3. View all sessions")
        print("  4. View sessions for one subject")
        print("  5. View totals by subject")
        print("  6. Quit")

        choice = input("Enter a number (1-6): ").strip()

        if choice == "1":
            run_live_timer()
        elif choice == "2":
            log_session_manually()
        elif choice == "3":
            show_all_sessions()
        elif choice == "4":
            show_sessions_for_subject()
        elif choice == "5":
            show_totals()
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Please enter a number from 1 to 6.\n")


if __name__ == "__main__":
