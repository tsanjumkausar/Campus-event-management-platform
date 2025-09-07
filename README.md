# Campus Event Management Platform

This project is a simple **campus event reporting system** I built. The idea is that colleges can create different events (seminars, workshops, fests, etc.), and students can **register, mark attendance, and give feedback** for them.  

I used **Flask for the backend** and **SQLite as the database**. I created tables for things like colleges, students, events, registrations, attendance, and feedback. I also added some rules to keep the data clean—for example:
- A student can’t register twice for the same event.  
- Feedback ratings must be between **1 and 5** only.  

The system exposes a few APIs where you can:
- Add new events  
- Enroll/register students  
- Mark attendance  
- Collect feedback  

From this, I also generated some reports like:  
- Which events are trending  
- How many events a student attended  
- Who are the most active students  

I tested all this with dummy data, ran the server, and checked the reports both in **JSON format (via APIs)** and in **CSV format (exported files)**.  

---

## How to Run It (Steps I Followed)

### 1. Create and activate a virtual environment

python -m venv .venv
source .venv/bin/activate

### 2. Install the dependencies
pip install -r requirements.txt

### Initialize the Database with sample data
### Run below command to Seeded sample data
python seed.py

## Run the server
python app.py

### When I did this, I got output like:
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://10.117.83.49:8000
### Server at http://localhost:8000/health

### When I opened http://127.0.0.1:8000/health
I saw this:

*/

{
  "status": "ok"
}

/*


## Reports I Tried Out

## I directly pasted these links in my browser to check the reports:

Event Popularity Report:
http://127.0.0.1:8000/reports/event-popularity

Student Participation Report:
http://127.0.0.1:8000/reports/student-participation

Top Active Students (bonus):
http://127.0.0.1:8000/reports/top-active-students


## I also tried exporting reports using below command:
python reports.py

## It gave me output: 
- Reports exported to docs/reports

This created CSV files inside the docs/reports/ folder.


## Notes From My Side
- Tech: Flask + SQLite + SQLAlchemy.
- The data model and APIs are explained in DESIGN.md.
- I also added AI conversation screenshots in the ai_log/ directory to keep track of how I discussed and built this.





