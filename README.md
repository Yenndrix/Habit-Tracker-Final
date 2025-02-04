# My Habit Tracking APP Project

The HabitTracker app is designed to provide users with an easy way to track and analyze their habits. 

## About the project?

Have you ever wondered how to successfully build new routines or maintain consistency with your habits? 
This habit-tracking application provides a robust backend solution to help users:

- Create and manage customizable habits tailored to their goals.
- Track daily, weekly and monthly completions to stay accountable.
- Analyze their progress with powerful insights trough streak tracking.
  
The application is designed for scalability and data persistence. The system is split into three core components to ensure a clean and modular design: a command-line interface (CLI), an analytical module for logic and insights, and a database module to handle all storage and retrieval operations. It uses SQLite for storing user and habit information. Libraries like datetime are leveraged for precise date calculations, such as tracking streaks and determining periodicity. Additionally, user passwords are securely hashed using Python’s hashlib library to ensure the confidentiality and integrity of user data.

This project was developed as a practical assignment for exploring object-oriented and functional programming concepts in Python.

## Features

1. **User Registration and Authentication**  
   - Secure user account creation with support for username, password, and email.  
   - Login functionality to ensure personalized habit tracking.

2. **Customizable and Predefined Habits**  
   - Create fully customized habits tailored to your goals.  
   - Access predefined habits for common routines to save time.

3. **Flexible Habit Scheduling**  
   - Track habits on **daily**, **weekly**, or **monthly** schedules.  
   - Perfect for building habits across diverse timeframes.

4. **Completion Tracking and Streaks**  
   - Monitor progress by marking habits as complete.  
   - Build and maintain streaks to stay motivated and consistent.

5. **Data Persistence and Advanced Analytics**  
   - All user and habit data is stored persistently in an SQLite database.  
   - Gain insights into your habits with detailed reports and analytics.


Language: **EN**

**Python Version: 3.7**


## How to istall it?

1. **Download** the **ZIP folder** of the Habit Tracking App.

2. **Install** dependencies by running:

``` shell

pip install -r requirements.txt

```

## Usage

**Start the app by running:**

``` shell

python main.py

```

## Testing

**To run the tests, follow these steps:**

**1. pip install pytest**

``` shell

pip install pytest

```
**2. Run the test suite from the project's root directory:**

``` shell

pytest

```
**3. Run a specific test file (if needed):**

``` shell

pytest test_DBModule.py

```