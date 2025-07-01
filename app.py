import os
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone, date, timedelta
from zoneinfo import ZoneInfo
from functools import wraps

# Configure application
app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Get the directory of the current file (app.py)
basedir = os.path.abspath(os.path.dirname(__file__))

# Define the database directory
db_path = os.path.join(basedir, "database.db")

# Configure CS50 Library to use SQLite database
db = SQL(f"sqlite:///{db_path}")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return render_template('landing.html')


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    """Add Category"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        category = request.form.get("category")
        category = category.strip().upper()
        message = None

        if not category:
            message = "Category Field Empty"
            return render_template("category_new.html", apology = message)
        if len(category) >= 30:
            message = "Category length too high"
            return render_template("category_new.html", apology = message)

        cat = db.execute("SELECT category_name FROM category WHERE user_id = ?", session["user_id"])
        existing_categories = [row["category_name"] for row in cat]

        if category in existing_categories:
            message = "Category already exists"
            return render_template("category_new.html", apology=message)


        db.execute("INSERT INTO category (user_id, category_name) VALUES (?, ?)",
                       session["user_id"], category)
        message = "Category Successfully Added"
        return render_template("category_new.html", apology=message)
    return render_template("category_new.html")

@app.route("/" \
"category", methods=["GET", "POST"])
def del_cat():
    categories = db.execute("SELECT category_name FROM category WHERE user_id = ?", session["user_id"])
    category_all = [row["category_name"] for row in categories]
    if request.method == "POST":
        category = request.form.get("category")
        message = None
        if category == "GENERAL":
            message = "Cant select General Category"
            return render_template("del_category.html", apology = message, category_all= category_all)
        elif category in category_all and category != "GENERAL":
            db.execute("DELETE FROM category WHERE user_id = ? AND category_name = ?", session["user_id"], category)
            db.execute("DELETE FROM tasks WHERE user_id = ? AND category = ?", session["user_id"], category)
        else:
            message = "Field Empty"
            return render_template("del_category.html", category_all = category_all, apology = message)

        message = f"Category '{category}' deleted successfully."
        return redirect("/del_category")
         
    return render_template("del_category.html", category_all=category_all)

MONTH = {1:"January", 2: "February", 3:"March", 4:"April", 5:"May", 6:"June", 7:"July", 8:"August", 9:"September", 10:"October", 11:"November", 12:"December"}

@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    categories = db.execute("SELECT category_name FROM category WHERE user_id = ?", session["user_id"])
    category_all = [row["category_name"] for row in categories]
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    today = now.date()
    if request.method == "POST":
        task = request.form.get("task").strip().upper()
        category = request.form.get("category")
        target_day = request.form.get("Target_Day")
        target_month = request.form.get("Target_Month")
        target_year = request.form.get("Target_Year")
        message = None

        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        today = now.date()

        if not task:
            message = "Task Field Empty"
            return render_template("task_new.html", apology = message, category_all=category_all, month = MONTH, today=today)
        if not category:
            category = "GENERAL"
        tasks = db.execute("SELECT task FROM tasks WHERE user_id = ?", session["user_id"])
        tasks_all = [row["task"] for row in tasks]
        if task in tasks_all:
            message = "Task Already Exist"
            return render_template("task_new.html", apology = message, category_all=category_all, month = MONTH, today=today)
        if len(task) > 30:
            message = "Task name too long"
            return render_template("task_new.html", apology = message, category_all=category_all, month = MONTH, today=today)
        
        if not target_day:
            target_day = today.day
        if not target_month:
            target_month = today.month
        if not target_year:
            target_year = today.year
        
        if not str(target_day).isdigit() or not str(target_month).isdigit() or not str(target_year).isdigit():
            message = "Input not digit"
            return render_template("task_new.html", apology = message, category_all=category_all, month = MONTH, today=today)
        
        target_day = int(target_day)
        target_month = int(target_month)
        target_year = int(target_year)
        try:
            date(target_year, target_month, target_day)
         
        except ValueError:
            message = "Invalid date"
            return render_template("task_new.html", apology = message, category_all=category_all, month = MONTH, today=today)
        
        
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        today = now.date()
        target = date(target_year, target_month, target_day)
        
        if str(target) < str(today):
            message = "Target Date cannot be in past"
            return render_template("task_new.html", apology = message, category_all=category_all, month = MONTH, today=today)

        
        if category == "GENERAL" and "GENERAL" not in category_all:
            db.execute("INSERT INTO category (user_id, category_name) VALUES (?,?)", session["user_id"], category, month = MONTH, today=today)
        
        db.execute("INSERT INTO tasks (user_id, task, category, status, target, created_at, completed_at) VALUES (?,?,?,?,?,?,?)",
                   session["user_id"], task, category, "TASK NOT STARTED", target, now, None)
            
        message = "TASK ADDED SUCCESSFULLY!"
        return render_template("task_new.html", apology = message, category_all=category_all, month = MONTH, today=today)
    return render_template("task_new.html",category_all=category_all, month = MONTH, today=today)


DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
@app.route("/add_re_task", methods=["GET", "POST"])
def add_re_task():
    categories = db.execute("SELECT category_name FROM category WHERE user_id = ?", session["user_id"])
    category_all = [row["category_name"] for row in categories]
    if request.method == "POST":
        task = request.form.get("task").strip().upper()
        category = request.form.get("category")
        type = request.form.get("type").upper()
        day = request.form.get("day")
        recur_for = 30
        streak_count = 0
        message = None

        if not task:
            message = "Task Field Empty"
            return render_template("new_recur_task.html", apology = message, category_all = category_all, day_all = DAYS)
        
        tasks = db.execute("SELECT task FROM tasks_recurring WHERE user_id = ?", session["user_id"])
        tasks_all = [row["task"] for row in tasks]
        if task in tasks_all:
            message = "Task Already Exist"
            return render_template("new_recur_task.html", apology = message, category_all=category_all, day_all = DAYS)
        if len(task) > 30:
            message = "Task name too long"
            return render_template("new_recur_task.html", apology = message, category_all=category_all, day_all = DAYS)
        
        if not type:
            type = "D"
        
        if type not in ["D","W"]:
            message = "Invalid type"
            return render_template("new_recur_task.html", apology = message, category_all = category_all, day_all = DAYS)
        
        if type == "W" and not day:
            now = datetime.now(ZoneInfo("Asia/Kolkata"))
            today = now.date()
            day = today.strftime("%A").upper()
        
        if not category:
            category = "GENERAL"
        
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        today = now.date()
        if (category == "GENERAL") and (category not in category_all):
            db.execute("INSERT INTO category (user_id, category_name) VALUES (?,?)", session["user_id"], category)
        
        if type == "D":
            x = 0
            
            while x != 30:
                db.execute("INSERT INTO tasks_recurring (user_id, task, category, status, started_at, completed_at, type) VALUES (?,?,?,?,?,?,?)",
                           session["user_id"], task, category, "TASK NOT STARTED", today + timedelta(days=x), None, type)
                x += 1
            db.execute("INSERT INTO tasks_recurring_info (user_id, task, category, start_at, end_at, streak_count, type) VALUES (?,?,?,?,?,?,?)",
                           session["user_id"], task, category, today, today + timedelta(days=x - 1), streak_count, type)
        elif type == "W":
            now = datetime.now(ZoneInfo("Asia/Kolkata"))
            today = now.date()
            today_day = today.strftime("%A").upper()
            
            if today_day == day:
                x = 0
                
                while x < 30:
                    db.execute("INSERT INTO tasks_recurring (user_id, task, category, status, started_at, completed_at, type) VALUES (?,?,?,?,?,?,?)",
                            session["user_id"], task, category, "TASK NOT STARTED", today + timedelta(days=x), None, type)
                    x += 7

                db.execute("INSERT INTO tasks_recurring_info (user_id, task, category, start_at, end_at, streak_count, type) VALUES (?,?,?,?,?,?,?)",
                           session["user_id"], task, category, today, today + timedelta(days=x - 7), streak_count, type) 
            else:
                y = 1
                targ_date = today + timedelta(days=y)
                targ_day = targ_date.strftime("%A").upper()
                while targ_day != day:
                    y += 1
                    targ_date = today + timedelta(days=y)
                    targ_day = targ_date.strftime("%A").upper()
                if targ_day == day:
                    x = y
                    while x < 30:
                        db.execute("INSERT INTO tasks_recurring (user_id, task, category, status, started_at, completed_at, type) VALUES (?,?,?,?,?,?,?)",
                                session["user_id"], task, category, "TASK NOT STARTED", today + timedelta(days=x), None, type)
                        x += 7

                    db.execute("INSERT INTO tasks_recurring_info (user_id, task, category, start_at, end_at, streak_count, type) VALUES (?,?,?,?,?,?,?)",
                               session["user_id"], task, category, targ_date, targ_date + timedelta(days=x), streak_count, type)

        message = "TASK ADDED SUCCESSFULLY!"
        categories = db.execute("SELECT category_name FROM category WHERE user_id = ?", session["user_id"])
        category_all = [row["category_name"] for row in categories]

        return render_template("new_recur_task.html", apology = message, category_all=category_all, day_all = DAYS)
    
    return render_template("new_recur_task.html",category_all=category_all, day_all = DAYS)

    
TASK_STATUS = ["TASK NOT STARTED", "TASK IN PROGRESS", "TASK DONE"]

@app.route("/edit_task", methods=["GET", "POST"])
def edit_task():
    # Load all categories for dropdown
    rows = db.execute("SELECT category_name FROM category WHERE user_id = ?", session["user_id"])
    category_all = [r["category_name"] for r in rows]
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    today = now.date()

    # Initialize context
    selected_cat = None
    selected_task = None
    status = False
    tasks_all = []
    existing_target = None
    selected_status = None
    status_msg = None
    apology = None

    if request.method == "POST":
        # Step 1 & onward: category must always be present
        selected_cat = request.form.get("cat")
        if not selected_cat:
            apology = "Category not selected"
            return render_template("edit_task.html", category_all=category_all, apology=apology, month = MONTH, today=today)

        # Fetch tasks in this category for later steps
        task_rows = db.execute("SELECT task, target, status FROM tasks WHERE user_id = ? AND category = ? AND status != ?",
                               session["user_id"], selected_cat, "TASK DONE")
        tasks_all = [r["task"] for r in task_rows]

        # Determine which step based on presence of 't' and 's'
        selected_task = request.form.get("t")
        new_status = request.form.get("s")

        # Step 2: Task selected but status/form not submitted
        if selected_task and not new_status:
            matching = [r for r in task_rows if r["task"] == selected_task]
            if not matching:
                apology = "Task not found"
            else:
                existing_target = matching[0]["target"]
                selected_status = matching[0]["status"]

                status = True
            return render_template(
                "edit_task.html",
                category_all=category_all,
                tasks_all=tasks_all,
                selected_cat=selected_cat,
                selected_task=selected_task,
                status=status,
                existing_target=existing_target,
                selected_status=selected_status,
                TASK_STATUS=TASK_STATUS,
                apology=apology,month = MONTH,
                today=today
            )

        # Step 3: Perform update when status field is present
        if selected_task and new_status:
            day   = request.form.get("Target_Day")
            month = request.form.get("Target_Month")
            year  = request.form.get("Target_Year")

            # Fetch current target for defaults
            current = [r for r in task_rows if r["task"] == selected_task][0]["target"]
            curr_dt = date.fromisoformat(current)
            try:
                d = int(day)   if day   else curr_dt.day
                m = int(month) if month else curr_dt.month
                y = int(year)  if year  else curr_dt.year
                new_target = date(y, m, d).isoformat()
            except ValueError:
                apology = "Invalid date components"
                return render_template("edit_task.html", category_all=category_all, apology=apology, month = MONTH, today=today)

            now = datetime.now(ZoneInfo("Asia/Kolkata"))
            today = now.date()
            if str(new_target) < str(today):
                message = "Target Date cannot be in past"
                return render_template("edit_task.html", apology = message, category_all=category_all, month = MONTH, today=today)

            # Apply update
            if status != "TASK DONE":
                db.execute("UPDATE tasks SET status = ?, target = ? WHERE user_id = ? AND category = ? AND task = ?",
                    new_status, new_target, session["user_id"], selected_cat, selected_task)

            else:
                db.execute("UPDATE tasks SET status = ?, target = ?, completed_at = ? WHERE user_id = ? AND category = ? AND task = ?",
                    new_status, new_target, now, session["user_id"], selected_cat, selected_task)
            
            # Fetch previous values again to compare
            matching = [r for r in task_rows if r["task"] == selected_task]
            if matching:
                existing_target = matching[0]["target"]
                selected_status = matching[0]["status"]

            if (existing_target == new_target) and (selected_status != new_status):
                status_msg = (f"Task '{selected_task}' updated → status: {new_status}")
            elif (existing_target != new_target) and (selected_status == new_status):
                status_msg = (f"Task '{selected_task}' updated → target: {new_target}")
            elif (existing_target != new_target) and (selected_status != new_status):
                status_msg = (f"Task '{selected_task}' updated → status: {new_status}, target: {new_target}")
            else:
                status = None

            # Refresh task list for re-render
            tasks_all = [r["task"] for r in db.execute("SELECT task FROM tasks WHERE user_id = ? AND category = ? AND status != ?",session["user_id"], selected_cat, "TASK DONE")]
            selected_status = new_status
            existing_target = new_target
            status = True

    # GET request or after update/render fallback
    return render_template("edit_task.html",
                           category_all=category_all,tasks_all=tasks_all,
                           selected_cat=selected_cat,selected_task=selected_task,
                           status=status,existing_target=existing_target,
                           selected_status=selected_status,TASK_STATUS=TASK_STATUS,
                           status_msg=status_msg,apology=apology,month = MONTH,today=today)


@app.route("/edit_recur_task", methods=["GET", "POST"])
def edit_re_task():
    # load categories
    rows = db.execute("SELECT category_name FROM category WHERE user_id = ?",session["user_id"])
    category_all = [r["category_name"] for r in rows]

    # initialize context
    selected_cat = None
    selected_task = None
    tasks_all = []
    selected_status = None
    status = False
    status_msg = None
    apology = None

    if request.method == "POST":
        # step 1: category must be selected
        selected_cat = request.form.get("cat")
        if not selected_cat:
            apology = "Please select a category."
            return render_template("edit_recur_task.html",category_all=category_all,apology=apology)
        
        # fetch recurring tasks for category
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        today = now.date()
        rows = db.execute("SELECT task, status FROM tasks_recurring WHERE user_id = ? AND category = ? AND started_at = ? AND status != ?",
                          session["user_id"], selected_cat, today, "TASK DONE")
        tasks_all = [r["task"] for r in rows]

        # step 2: task selection or status update
        selected_task = request.form.get("t")
        new_status = request.form.get("s")

        # if task selected but no new status -> show current status
        if selected_task and not new_status:
            match = next((r for r in rows if r["task"] == selected_task), None)
            if not match:
                apology = "Task not found."
            else:
                selected_status = match["status"]
                status = True
            return render_template("edit_recur_task.html",
                category_all=category_all,tasks_all=tasks_all,
                selected_cat=selected_cat,selected_task=selected_task,
                selected_status=selected_status,TASK_STATUS=TASK_STATUS,
                apology=apology,status=status)

        # if status update submitted
        if selected_task and new_status:
            # get old status
            match = next((r for r in rows if r["task"] == selected_task), None)
            old_status = match["status"]
            now = datetime.now(ZoneInfo("Asia/Kolkata"))
            today = now.date()
            if new_status == "TASK DONE" and old_status != new_status:
                db.execute("UPDATE tasks_recurring SET status = ?, completed_at = ? WHERE user_id = ? AND category = ? AND task = ? AND started_at = ?",
                           new_status, now, session["user_id"], selected_cat, selected_task, today)

                info = db.execute("SELECT streak_count FROM tasks_recurring_info WHERE user_id = ? AND category = ? AND task = ?",
                          session["user_id"], selected_cat, selected_task)
                tasks_streak = [r["streak_count"] for r in info]
                streak_count = tasks_streak[0]
                db.execute("UPDATE tasks_recurring_info SET streak_count = ? WHERE user_id = ? AND category = ? AND task = ?",
                           streak_count + 1, session["user_id"], selected_cat, selected_task)
             
            elif new_status != "TASK DONE" and old_status != new_status:
                db.execute("UPDATE tasks_recurring SET status = ? WHERE user_id = ? AND category = ? AND task = ? AND started_at = ?",
                           new_status, session["user_id"], selected_cat, selected_task, today)

            # prepare status message
            if old_status != new_status:
                status_msg = f"Task '{selected_task}' status updated → {new_status}"
            status = True
            selected_status = new_status

            return render_template("edit_recur_task.html", category_all=category_all,tasks_all=tasks_all,
                                   selected_cat=selected_cat,selected_task=selected_task,
                                   selected_status=selected_status,TASK_STATUS=TASK_STATUS,
                                   status_msg=status_msg,apology=apology,status=status)
            

    # final render
    return render_template("edit_recur_task.html",
                           category_all=category_all,tasks_all=tasks_all,
                           selected_cat=selected_cat,selected_task=selected_task,
                           selected_status=selected_status,TASK_STATUS=TASK_STATUS,
                           status_msg=status_msg,apology=apology,status=status)

@app.route("/del_task", methods=["GET", "POST"])
def delete_task():
    category_all = [row["category"] for row in db.execute("SELECT DISTINCT category FROM tasks WHERE user_id = ?", session["user_id"])]
    tasks_all = []
    apology = None
    status = None

    if request.method == "POST":
        if "cat" in request.form and "t" not in request.form:
            # Step 1: Category selected
            category = request.form.get("cat")
            if not category:
                apology = "Category not selected"
                return render_template("task_del.html", category_all=category_all, apology=apology)
            else:
                tasks_all = [row["task"] for row in db.execute(
                    "SELECT task FROM tasks WHERE user_id = ? AND category = ?", session["user_id"], category)]
                return render_template("task_del.html", category_all=category_all, tasks_all=tasks_all, selected_cat=category)

        elif "t" in request.form:
            # Step 2: Task selected
            task = request.form.get("t")
            category = request.form.get("cat")
            if not task or not category:
                apology = "Task or category missing"
                return render_template("task_del.html", category_all=category_all, apology=apology)
            else:
                db.execute("DELETE FROM tasks WHERE user_id = ? AND task = ? AND category = ?", session["user_id"], task, category)
                status = "Task successfully deleted"

    return render_template("task_del.html", category_all=category_all, apology=apology, status=status)

@app.route("/task_all", methods = ["GET", "POST"])
def task_all():
    tasks_all = db.execute("SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC", session["user_id"])
    return render_template("tasks_normal_display.html", tasks_all = tasks_all)

@app.route("/task_today", methods = ["GET", "POST"])
def task_today():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    today = now.date()
    tasks_all_r = db.execute("SELECT * FROM tasks_recurring WHERE user_id = ? AND DATE(started_at) = ? ORDER BY status DESC, category ASC",
                            session["user_id"], today)
    tasks_all = db.execute("SELECT * FROM tasks WHERE user_id = ? AND DATE(target) = ? ORDER BY status DESC, category ASC",
                           session["user_id"], today)
    return render_template("tasks_normal_display.html", tasks_all = tasks_all, tasks_all_r = tasks_all_r)

@app.route("/task_week", methods = ["GET", "POST"])
def task_week():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    today = now.date()
    tasks_all_r = db.execute("SELECT * FROM tasks_recurring WHERE user_id = ? AND DATE(started_at) BETWEEN ? AND ? ORDER BY category ASC",
                             session["user_id"], today, today + timedelta(days=7))
    tasks_all = db.execute("SELECT * FROM tasks WHERE user_id = ? AND DATE(target) BETWEEN ? AND ? ORDER BY category ASC, created_at DESC",
                           session["user_id"], today, today + timedelta(days=7))
    return render_template("tasks_normal_display.html", tasks_all = tasks_all)

@app.route("/task_month", methods = ["GET", "POST"])
def task_month():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    today = now.date()
    tasks_all = db.execute("SELECT * FROM tasks WHERE user_id = ? AND DATE(target) BETWEEN ? AND ? ORDER BY category ASC, created_at DESC", session["user_id"], today, today + timedelta(days=30))
    return render_template("tasks_normal_display.html", tasks_all = tasks_all)

@app.route("/task_recurring", methods = ["GET", "POST"])
def task_recurring():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    today = now.date()
    tasks_all = db.execute("SELECT * FROM tasks_recurring_info WHERE user_id = ? ORDER BY streak_count DESC, type", session["user_id"])
    return render_template("tasks_recurring_display.html", tasks_all = tasks_all)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        message = None
        # Ensure username was submitted
        if not request.form.get("username"):
            message = "Must provide username"
            return render_template("login.html", apology = message)
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            message = "Must provide password"
            return render_template("login.html", apology = message)
            
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            message = "invalid username and/or password"
            return render_template("login.html", apology = message)
        
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/task_today")
        

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get input and store in variable.
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        
        # declare variable to display message.
        message = None

        # Ensure username and password was submitted 
        if not username or not password:
            message = "Enter both Field"
            return render_template("register.html", apology = message)
        
        # Ensure password and confirm password matches.
        if password != confirmation:
            message = "Password and Confirm password dont match"
            return render_template("register.html", apology = message)
        
        # Execute query to get all usernames from users table.
        existing_user = db.execute("SELECT username FROM users WHERE username = ?", username)
        
        # Ensure username does not exist already.
        if existing_user:
            message = "Username already taken"
            return render_template("register.html", apology = message)
        
        # Hash the password
        hash = generate_password_hash(str(password), method='scrypt', salt_length=16)
        
        # current time
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        

        # Execute query to add cerdentials to users table.
        db.execute("INSERT INTO users (username, hash, created_at) VALUES (?,?,?)", username, hash, now)

        # Redirect user to login page. 
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("register.html")

if __name__ == '__main__':
    app.run(debug=True)
