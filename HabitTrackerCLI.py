# Initializes a User CLI 
from DBModule import User, Habit, Streak, get_db, close_db, create_tables, hash_password
from AnalyticalModule import user_dashboard


def cli():
    """
    Command Line Interface (CLI) for the Habit Tracking App.

    This function provides an interactive command-line interface that allows users to:
    - Register a new account
    - Log in to an existing account
    - Access their user dashboard
    - Manage their habits

    The function connects to the database, prompts the user for authentication, 
    and redirects them to the appropriate actions.

    Database connection is maintained throughout the session and closed upon exit.
    """
    print("Welcome to the Habit Tracking App!")

    # Establish database connection and ensure required tables exist
    db = get_db()
    create_tables(db)

    user = None  # Initialize user variable

    while True:
        if not user:
            # Prompt the user for authentication choice
            choice = input("Do you want to register or login? (login/register): ").strip().lower()

            if choice == "login":
                # Handle user login
                username = input("Please enter your username: ").strip()
                password = input("Please enter your password: ").strip()
                user = User.try_login(db, username, hash_password(password))

                if user:
                    print(f"Welcome back, {user.username}!")
                else:
                    print("Error: Can't find this user. Please try again.")

            elif choice == "register":
                # Handle new user registration
                username = input("Choose a username: ").strip()
                plain_password = input("Choose a password: ").strip()
                email = input("Enter your email: ").strip()

                # Check if the chosen username is already taken
                if User.username_exists(db, username):
                    print(f"Error: The username '{username}' is already taken. Please choose a different one.")
                    continue

                hashed_password = hash_password(plain_password)

                # Attempt to create a new user
                user = User.add_user(db, username, hashed_password, email)
                if user:
                    print(f"Account for '{username}' created successfully!")
                    # Add predefined habits for the new user
                    Habit.add_predefined_habits(db, user)
                else:
                    print("Error: Registration failed. Please try again.")

            else:
                print("Invalid choice. Please enter 'login' or 'register'.")

        else:
            # Redirect the authenticated user to their dashboard
            user_dashboard(db, user)
            user = None  # Log out the user after the dashboard session

    # Close the database connection when the application exits
    close_db(db)


if __name__ == "__main__":
    cli()
