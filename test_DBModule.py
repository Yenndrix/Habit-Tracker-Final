import pytest
import sqlite3
from datetime import datetime, date, timedelta
from DBModule import hash_password, get_db, close_db, User, create_tables, Habit, Daily, Weekly, Monthly, Streak
from dateutil.relativedelta import relativedelta


# Tests for Utility Functions

def test_hash_password():
    """
    Test the hash_password function to ensure it hashes passwords correctly.
    """
    password = "mypassword"
    hashed = hash_password(password)
    assert hashed is not None  
    assert hashed != password  # Ensure hashed password is not the same as the original


def test_get_db():
    """
    Test the get_db function to ensure a database connection is returned and foreign keys are enabled.
    """
    db = get_db()
    assert isinstance(db, sqlite3.Connection)  # Ensure returned object is a SQLite connection
    cursor = db.cursor()
    cursor.execute("PRAGMA foreign_keys;")  
    foreign_keys_status = cursor.fetchone()[0]
    assert foreign_keys_status == 1  # Ensure foreign keys are enabled
    db.close()


def test_close_db():
    """
    Test the close_db function to ensure it closes the database connection.
    """
    db = sqlite3.connect(":memory:")  # Create an in-memory SQLite database
    assert db is not None
    close_db(db)  
    try:
        db.execute("SELECT 1")  
        assert False  # Should raise an exception
    except sqlite3.ProgrammingError:
        pass  # Pass if exception is raised


# Test for User Class

def get_test_db():
    """
    Create a test database in memory with necessary tables.
    """
    db = sqlite3.connect(":memory:")
    create_tables(db)  # Create tables for testing
    return db


def test_add_user():
    """
    Test adding a user to the database.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    assert user is not None  # Ensure user is added
    assert user.username == "testuser"  # Ensure username matches
    assert user.emailID == "testuser@example.com"  # Ensure email matches
    db.close()


def test_find_user():
    """
    Test finding an existing user by username.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    found_user = User.find_user(db, "testuser")
    assert found_user is not None  # Ensure the user is found
    assert found_user.username == "testuser"  # Ensure correct user is found
    db.close()


def test_find_user_not_found():
    """
    Test finding a user that doesn't exist.
    """
    db = get_test_db()
    found_user = User.find_user(db, "nonexistentuser")
    assert found_user is None  # Ensure no user is found
    db.close()


def test_username_exists():
    """
    Test checking if a username already exists in the database.
    """
    db = get_test_db()
    User.add_user(db, "testuser", "password123", "testuser@example.com")
    exists = User.username_exists(db, "testuser")
    assert exists is True  # Ensure username exists
    exists = User.username_exists(db, "nonexistentuser")
    assert exists is False  # Ensure username does not exist
    db.close()


def test_try_login():
    """
    Test user login with correct and incorrect credentials.
    """
    db = get_test_db()
    User.add_user(db, "testuser", "password123", "testuser@example.com")
    user = User.try_login(db, "testuser", "password123")
    assert user is not None  # Ensure user can log in with correct credentials
    assert user.username == "testuser"  # Ensure logged-in user matches
    user = User.try_login(db, "testuser", "wrongpassword")
    assert user is None  # Ensure login fails with incorrect password
    db.close()


def test_delete_user():
    """
    Test deleting a user from the database.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    assert user.delete_user(db) is True  # Ensure user is deleted
    found_user = User.find_user(db, "testuser")
    assert found_user is None  # Ensure user is no longer in the database
    db.close()


def test_delete_user_by_name():
    """
    Test deleting a user by username.
    """
    db = get_test_db()
    User.add_user(db, "testuser", "password123", "testuser@example.com")
    result = User.delete_user_by_name(db, "testuser")
    assert result is True  # Ensure user is deleted by username
    found_user = User.find_user(db, "testuser")
    assert found_user is None  # Ensure user is no longer in the database
    db.close()


# Test Habit Class

def test_add_habit():
    """
    Test adding a habit to the database.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    habit_id = Habit.add_habit(db, user, "Exercise", "Morning run", "2025-01-01", "Daily")
    assert habit_id is not None  # Ensure habit is added
    cur = db.cursor()
    cur.execute("SELECT * FROM habits WHERE habit_id = ?", (habit_id,))
    habit = cur.fetchone()
    assert habit is not None  # Ensure habit exists in the database
    assert habit[2] == "Exercise"  # Ensure habit name is correct
    db.close()


def test_complete_habit():
    """
    Test completing a daily habit and tracking streaks.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    habit_id = Daily.add_habit(db, user, "Exercise", "Morning run", "2025-01-01", "Daily")
    habit = Daily(habit_id, "Exercise", "Morning run", "2025-01-01")
    streak, changed = habit.complete(db, user.user_id)
    assert changed is True  # Ensure streak is updated
    assert streak.current_streak == 1  # Ensure current streak is 1
    assert streak.longest_streak == 1  # Ensure longest streak is 1
    db.close()


def test_list_habits_for_user():
    """
    Test listing all habits for a specific user.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    Habit.add_habit(db, user, "Exercise", "Morning run", "2025-01-01", "Daily")
    Habit.add_habit(db, user, "Read", "Read a book", "2025-01-01", "Weekly")
    habits = Habit.list_habits_for_user(db, user)
    assert len(habits) == 2  # Ensure two habits exist
    assert any(habit.habit_name == "Exercise" for habit in habits)  # Ensure "Exercise" is in the list
    assert any(habit.habit_name == "Read" for habit in habits)  # Ensure "Read" is in the list
    db.close()


def test_daily_habit_completion():
    """
    Test completing a daily habit multiple times and tracking streak changes.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    habit_id = Daily.add_habit(db, user, "Exercise", "Morning run", "2025-01-01", "Daily")
    habit = Daily(habit_id, "Exercise", "Morning run", "2025-01-01")

    today = date.today()

    # First completion: should update streak
    streak, changed = habit.complete(db, user.user_id, today)
    assert changed is True
    assert streak.current_streak == 1
    assert streak.longest_streak == 1

    # Completing again the same day should not change the streak
    streak, changed = habit.complete(db, user.user_id, today)
    assert changed is False
    assert streak.current_streak == 1
    assert streak.longest_streak == 1

    # Completing on a new day should increase streak
    streak, changed = habit.complete(db, user.user_id, today + timedelta(days=1))
    assert changed is True
    assert streak.current_streak == 2
    assert streak.longest_streak == 2

    # Completing after a gap resets the streak
    streak, changed = habit.complete(db, user.user_id, today + timedelta(days=5))
    assert changed is True
    assert streak.current_streak == 1
    assert streak.longest_streak == 2

    # Complete habit again, checking if streak increases
    streak, changed = habit.complete(db, user.user_id, today + timedelta(days=6))
    assert changed is True
    assert streak.current_streak == 2
    assert streak.longest_streak == 2

    # Complete habit again, checking if streak increases
    streak, changed = habit.complete(db, user.user_id, today + timedelta(days=7))
    assert changed is True
    assert streak.current_streak == 3
    assert streak.longest_streak == 3

    # Reset the streak after a significant gap
    streak, changed = habit.complete(db, user.user_id, today + timedelta(days=30))
    assert changed is True
    assert streak.current_streak == 1
    assert streak.longest_streak == 3

    db.close()


def test_weekly_habit_completion():
    """
    Test completing a weekly habit multiple times and tracking streak changes.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    habit_id = Weekly.add_habit(db, user, "Exercise", "Morning run", "2025-01-01", "Weekly")
    habit = Weekly(habit_id, "Exercise", "Morning run", "2025-01-01")

    today = date.today()

    # First completion: should update streak
    streak, changed = habit.complete(db, user.user_id, today)
    assert changed is True
    assert streak.current_streak == 1
    assert streak.longest_streak == 1

    # Completing again the same day should not change the streak
    streak, changed = habit.complete(db, user.user_id, today)
    assert changed is False
    assert streak.current_streak == 1
    assert streak.longest_streak == 1

    # Completing a new week should increase streak
    streak, changed = habit.complete(db, user.user_id, today + timedelta(days=7))
    assert changed is True
    assert streak.current_streak == 2
    assert streak.longest_streak == 2

    # Completing after a gap resets the streak
    streak, changed = habit.complete(db, user.user_id, today + timedelta(days=21))
    assert changed is True  # Updated expectation: Resetting still counts as a change
    assert streak.current_streak == 1  # Streak resets after 21 days
    assert streak.longest_streak == 2

    # Completing the habit again after 4 days should not change the streak
    streak, changed = habit.complete(db, user.user_id, today + timedelta(days=24))
    assert changed is False
    assert streak.current_streak == 1
    assert streak.longest_streak == 2

    # Complete habit again, checking if streak increases after the last completion
    streak, changed = habit.complete(db, user.user_id, today + timedelta(days=28))
    assert changed is True
    assert streak.current_streak == 2
    assert streak.longest_streak == 2

     # Complete habit again, checking if streak increases
    streak, changed = habit.complete(db, user.user_id, today + timedelta(days=35))
    assert changed is True
    assert streak.current_streak == 3
    assert streak.longest_streak == 3

    # Reset the streak after a significant gap
    streak, changed = habit.complete(db, user.user_id, today + timedelta(days=60))
    assert changed is True  # Updated expectation: Resetting still counts as a change
    assert streak.current_streak == 1
    assert streak.longest_streak == 3

    db.close()




def test_monthly_habit_completion():
    """
    Test completing a monthly habit multiple times and tracking streak changes.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    habit_id = Monthly.add_habit(db, user, "Exercise", "Morning run", "2025-01-01", "Monthly")
    habit = Monthly(habit_id, "Exercise", "Morning run", "2025-01-01")


    today = date.today()

    # First completion: should update streak
    streak, changed = habit.complete(db, user.user_id, today)
    assert changed is True
    assert streak.current_streak == 1
    assert streak.longest_streak == 1

    # Completing again the same day should not change the streak
    streak, changed = habit.complete(db, user.user_id, today)
    assert changed is False
    assert streak.current_streak == 1
    assert streak.longest_streak == 1

    # Completing a new month should increase streak
    streak, changed = habit.complete(db, user.user_id, today + relativedelta(months=1))
    assert changed is True
    assert streak.current_streak == 2
    assert streak.longest_streak == 2

    # Completing after a gap resets the streak
    streak, changed = habit.complete(db, user.user_id, today + relativedelta(months=4))
    assert changed is True
    assert streak.current_streak == 1
    assert streak.longest_streak == 2

    # Complete habit again, checking if streak increases
    streak, changed = habit.complete(db, user.user_id, today + relativedelta(months=5))
    assert changed is True
    assert streak.current_streak == 2
    assert streak.longest_streak == 2

    # Complete habit again, checking if streak increases
    streak, changed = habit.complete(db, user.user_id, today + relativedelta(months=6))
    assert changed is True
    assert streak.current_streak == 3
    assert streak.longest_streak == 3

    # Reset the streak after a significant gap
    streak, changed = habit.complete(db, user.user_id, today + relativedelta(months=9))
    assert changed is True
    assert streak.current_streak == 1
    assert streak.longest_streak == 3

    db.close()


def test_add_predefined_habits():
    """
    Test adding predefined habits for a user.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    Habit.add_predefined_habits(db, user)
    print("Loaded habits:", Habit.list_habits_for_user(db, user))
    habits = Habit.list_habits_for_user(db, user)
    predefined_habits = ["Drink Water", "Exercise", "Read a Book", "Weekly Review", "Monthly Budget"]
    print("Habits in DB:", [habit.habit_name for habit in habits])
    for habit_name in predefined_habits:
        assert any(habit.habit_name == habit_name for habit in habits)
    db.commit()
    db.close()


def test_add_duplicate_habit():
    """
    Test that duplicate habits cannot be added.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    habit_id = Habit.add_habit(db, user, "Exercise", "Morning run", "2025-01-01", "Daily")
    duplicate_habit_id = Habit.add_habit(db, user, "Exercise", "Morning run", "2025-01-01", "Daily")
    assert duplicate_habit_id is None  # Ensure duplicate habit cannot be added
    db.close()


# Tests for Streak

def test_get_streak():
    """
    Test getting the streak for a specific habit.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    habit_id = Habit.add_habit(db, user, "Exercise", "Morning run", "2025-01-01", "Daily")
    streak = Streak.get_streak(db, user.user_id, habit_id)
    assert streak.current_streak == 0  # Initial streak is 0
    assert streak.longest_streak == 0  # Longest streak is also 0 initially
    assert streak.last_completed is None  # No completion yet
    db.close()


def test_update_streak():
    """
    Test updating the streak after a habit is completed.
    """
    db = get_test_db()
    user = User.add_user(db, "testuser", "password123", "testuser@example.com")
    habit_id = Habit.add_habit(db, user, "Exercise", "Morning run", "2025-01-01", "Daily")
    streak = Streak(1, 1, datetime.today().date().isoformat())
    streak.update_streak(db, user.user_id, habit_id)
    updated_streak = Streak.get_streak(db, user.user_id, habit_id)
    assert updated_streak.current_streak == 1
    assert updated_streak.longest_streak == 1
    assert updated_streak.last_completed == datetime.today().date().isoformat()
    db.close()


# Test for Subclasses

def test_daily_streak():
    """
    Test daily habit streak calculation.
    """
    today = datetime.today().date()
    habit = Daily(1, "Test Daily", "Test", today.isoformat())
    assert habit.calculate_streak(today, None, 1) == (1, True)  # No prior completion
    assert habit.calculate_streak(today, (today - timedelta(days=1)).isoformat(), 2) == (3, True)  # Completed yesterday
    assert habit.calculate_streak(today, today.isoformat(), 2) == (2, False)  # Already completed today
    assert habit.calculate_streak(today, (today - timedelta(days=2)).isoformat(), 2) == (1, True)  # Reset after two days


def test_weekly_streak():
    """
    Test weekly habit streak calculation.
    """
    today = datetime.today().date()
    habit = Weekly(1, "Test Weekly", "Test", today.isoformat())
    assert habit.calculate_streak(today, None, 1) == (1, True)  # No prior completion
    assert habit.calculate_streak(today, (today - timedelta(days=6)).isoformat(), 2) == (2, False)  # Completed within the same week
    assert habit.calculate_streak(today, (today - timedelta(days=7)).isoformat(), 2) == (3, True)  # Exactly a week ago
    assert habit.calculate_streak(today, (today - timedelta(days=14)).isoformat(), 2) == (1, True)  # More than a week, reset


def test_monthly_streak():
    """
    Test monthly habit streak calculation.
    """
    today = datetime.today().date()
    habit = Monthly(1, "Test Monthly", "Test", today.isoformat())
    assert habit.calculate_streak(today, None, 1) == (1, True)  # No prior completion
    assert habit.calculate_streak(today, (today.replace(day=1)).isoformat(), 2) == (2, False)  # Within the current month
    assert habit.calculate_streak(today, (today.replace(day=1) - timedelta(days=1)).isoformat(), 2) == (3, True)  # Beginning of the new month
    assert habit.calculate_streak(today, (today - relativedelta(months=2)).isoformat(), 2) == (1, True)  # More than a month ago, reset


if __name__ == "__main__":
    pytest.main()
