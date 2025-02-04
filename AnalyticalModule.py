# Analytical Module - Handles user interactions and habit tracking
import logging
LOG_LEVEL = logging.DEBUG  
logging.basicConfig(level=LOG_LEVEL)
from datetime import datetime, date 
from DBModule import User, Habit, Streak, get_db, close_db, create_tables, hash_password

def user_dashboard(db, user):
    """
    Displays the main user dashboard and handles habit-related operations.

    Allows the user to:
    - Create a new habit
    - Mark a habit as completed
    - Analyze their habits and streaks
    - Log out or delete their account

    Parameters:
    db (sqlite3.Connection): Database connection object.
    user (User): The currently logged-in user.
    """
    
    user_id = user.user_id  # Extract the user's unique ID

    while True:
        # Display main menu options
        print("\nHere is your dashboard!")
        print("This Habit Tracker App allows you to:")
        print("1. Create a new habit")
        print("2. Complete an existing habit")
        print("3. Analyze your performance over time")
        print("4. Log out")
        print("5. Delete your account")

        choice = input("Enter your choice (1/2/3/4/5): ").strip()

        # ---- Option 1: Create a New Habit ----
        if choice == "1":
            habit_name = input("Please enter habit name: ").strip()
            habit_description = input("Enter habit description: ").strip()
            start_date = input("Enter start date (YYYY-MM-DD). This is optional: ").strip()
            if not start_date:
                start_date = datetime.today().strftime('%Y-%m-%d')
                logging.info(f"No start date provided. Defaulting to {start_date}")
            habit_type = input("Enter habit type (Daily, Weekly, Monthly): ").strip()

            if habit_type not in ("Daily", "Weekly", "Monthly"):
                print("Invalid habit type. Please choose from Daily, Weekly, or Monthly")
                continue

            logging.info(f"Creating habit '{habit_name}' for user {user.username} ({user.user_id})")# Debugging

            # Add habit to database
            habit = Habit.add_habit(db, user, habit_name, habit_description, start_date, habit_type)
            
            if habit:
                print(f"Habit '{habit_name}' added successfully!")
            else:
                print("Error: Failed to create habit. Please try again.")

        # ---- Option 2: Complete a Habit ----
        elif choice == "2":
            habits = user.list_habits(db)

            if not habits:
                print("You haven't created any habits yet.")
                continue

            # Display available habits
            print("Your habits:")
            for i, habit in enumerate(habits, start=1):
                print(f"{i}. {habit.habit_name}")  

            # Get user selection
            habit_choice = input("Enter the number of the habit you want to complete: ").strip()

            if habit_choice.isdigit():
                habit_index = int(habit_choice) - 1
                if 0 <= habit_index < len(habits):
                    habit = habits[habit_index]

                    logging.info(f"Completing habit '{habit.habit_name}' for user {user.username} ({user_id})")  # Debugging
                    
                    streak, changed = habit.complete(db, user_id)
                    if changed:
                        print(f"Streak of {habit.habit_name} is now {streak.current_streak}, Longest Streak = {streak.longest_streak}")
                else:
                    print("Invalid habit number. Please try again.")
            else:
                print("Invalid input. Please enter a valid number.")

        # ---- Option 3: Analyze Habits ----
        elif choice == "3":
            print("What would you like to know?")
            print("1. Show me a list of all my habits.")
            print("2. Show me all my habits with the same periodicity. (Daily, Weekly, Monthly)")
            print("3. Show me the longest streak for all of my habits.")
            print("4. Show me the longest streak for a specific habit!")

            try:
                choice_action = int(input("Please choose an action: ").strip())

                if choice_action == 1:
                    habits = user.list_habits(db)
                    if not habits:
                        print("You haven't created any habits yet.")
                    else:
                        print("Your habits:")
                        for i, habit in enumerate(habits, start=1):
                            print(f"{i}. {habit.habit_name}")

                elif choice_action == 2:
                    periodicity = input("Enter the periodicity (Daily, Weekly, Monthly): ").strip().capitalize()
                    valid_periods = ["Daily", "Weekly", "Monthly"]

                    if periodicity not in valid_periods:
                        print("Invalid periodicity. Please choose from Daily, Weekly, Monthly")
                    else:
                        habits = [habit for habit in user.list_habits(db) if habit.habit_type == periodicity]

                        if not habits:
                            print(f"No habits found for periodicity: {periodicity}.")
                        else:
                            print(f"Your {periodicity} habits:")
                            for i, habit in enumerate(habits, start=1):
                                print(f"{i}. {habit.habit_name}")

                elif choice_action == 3:
                    habits = user.list_habits(db)
                    if not habits:
                        print("You haven't created any habits yet.")
                    else:
                        print("Longest streaks for all your habits:")
                        for habit in habits:
                            streak = Streak.get_streak(db, user.user_id, habit.habit_id)
                            print(f"Habit: {habit.habit_name}, Longest Streak: {streak.longest_streak}")

                elif choice_action == 4:
                    habits = user.list_habits(db)
                    if not habits:
                        print("You haven't created any habits yet.")
                    else:
                        print("Your habits:")
                        for i, habit in enumerate(habits, start=1):
                            print(f"{i}. {habit.habit_name}")

                        try:
                            selected_habit_index = int(input("Select the habit number to view the longest streak: ").strip())
                            if 1 <= selected_habit_index <= len(habits):
                                selected_habit = habits[selected_habit_index - 1]
                                streak = Streak.get_streak(db, user.user_id, selected_habit.habit_id)
                                print(f"Habit: {selected_habit.habit_name}, Longest Streak: {streak.longest_streak}")
                            else:
                                print("Invalid habit number.")
                        except ValueError:
                            print("Please enter a valid number.")

                else:
                    print("Invalid choice. Please select a valid option.")

            except ValueError:
                print("Please enter a valid number.")

        # ---- Option 4: Log Out ----
        elif choice == "4":
            print(f"Goodbye, {user.username}! You have been logged out.")
            break

        # ---- Option 5: Delete Account ----
        elif choice == "5":
            delete_choice = input(f"Are you sure you want to delete your account, {user.username}? (yes/no): ").strip().lower()
            if delete_choice == "yes":
                print(f"DEBUG: Attempting to delete account for user {user.username} ({user.user_id})")  # Debugging
                if user.delete_user(db):  
                    print("Your account has been deleted successfully.")
                    break
                else:
                    print("Error: Failed to delete account. Please try again.")
            else:
                print("Account deletion canceled.")

        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
