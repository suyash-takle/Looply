# Looply - A Simple Task & Habit Manager

## Video Demo: <https://www.youtube.com/watch?v=djZKAKkgcuw>

## Description

Looply is a lightweight and focused task manager I built using Flask and SQLite. The goal was to make something that helps users manage both one-time tasks and recurring habits without being overwhelmed by too many features.

A lot of task managers out there either feel too minimal or too bloated. I wanted to strike a balance — something that’s simple to use, yet powerful enough to keep you on track with your goals. That’s where Looply comes in. You can add regular tasks with deadlines, recurring tasks for daily or weekly habits, and track your progress over time with visual streaks.

---

## Features

Here’s what you can do with Looply:

- **User Accounts**: Sign up and log in with your own account. Everything is private and personalized.
- **Categories**: Organize your tasks into categories. You can add new categories, switch between them, and delete them (except for the default “General” one).
- **Add Tasks**: Create one-time tasks with deadlines. Great for reminders, deadlines, and to-dos.
- **Recurring Tasks**: Set up daily or weekly tasks that repeat. Looply will help you build streaks by keeping track of how consistently you complete them.
- **Task Views**: View tasks based on their due date — whether they’re for today, this week, or this month. These views include both one-time and recurring tasks.
- **Edit & Delete**: Update or remove tasks and categories as needed.
- **Streak Tracking**: When you complete recurring tasks on time, your streak increases. Miss a day, and it resets. It’s a fun little way to stay motivated.

---

## How It Works (Under the Hood)

Looply is built using Python (Flask) for the backend and Jinja templates for the frontend. Here’s a breakdown of what I wrote:

- `app.py`: The heart of the app — it contains all the routes and core logic (handling login, task operations, etc).
- `helpers.py`: Custom helper functions that make the code cleaner — things like user verification.
- `templates/`: This is where all the HTML templates live. I used a base layout and extended it across all pages to keep things consistent.
- `tasks.db`: SQLite database file that stores everything — users, tasks, categories, and streaks.
- `requirements.txt`: List of all Python packages needed to run the app.

---

## Some Design Choices

One thing I debated early on was how to handle recurring tasks. Should I just mark them as “recurring” and treat them the same as normal tasks? I decided against that and instead gave them their own space in the database. This allowed me to handle streaks and reset logic much more cleanly.

Another decision was to keep the frontend simple and avoid using JavaScript. I wanted to focus on backend logic and routing, and I didn’t want the frontend to get too complicated. Even though the UI is basic, I think it serves the purpose well.

---

## Final Thoughts

Looply is the kind of tool I’d personally want to use — simple, fast, and focused. I learned a lot about structuring Flask apps, working with databases, and thinking through user experience. There’s still plenty of room to grow — features like reminders, due-time notifications, or adding pomodoro could be fun to add later.

For now, I’m happy with where it’s at. Thanks for checking it out!
