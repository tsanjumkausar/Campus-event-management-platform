Campus Event Management Platform

## Project Summary

This is a basic campus event reporting system. It allows colleges to create events such as seminars, workshops, or fests. Students can register, take attendance, and provide feedback.

The backend is done using Flask and SQLite is used for the database. I created tables for colleges, students, events, registrations, attendance, and feedback. Rules such as "no duplicate registrations" and "feedback rating between 1–5" are maintained to keep it clean.

The system offers APIs to add events, enroll students, mark attendance, and receive feedback. Reports are created to verify:

what events are trending,

how many events a student attended,

and the most active students.

I have tested it by inserting dummy data, executing the server, and verifying the reports in JSON and CSV format.

## Quick Start

First run below commands:-

## First Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

## And install all the requirements
pip install -r requirements.txt

## Initialize DB with sample data
## Run below command to Seeded sample data
python seed.py

# Run server
python app.py

## Once you run the above command you can see servers like this:-
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://10.117.83.49:8000
## Server at http://localhost:8000/health

## When you open http://127.0.0.1:8000/health
you can see output like this -

*/

{
  "status": "ok"
}

/*


## You can also try these endpoints

## Try the below reports endpoints [you can directly paste them in browser so can access below reports]:

Event Popularity Report:
http://127.0.0.1:8000/reports/event-popularity

Student Participation Report:
http://127.0.0.1:8000/reports/student-participation

Top Active Students (bonus):
http://127.0.0.1:8000/reports/top-active-students


## Next You Can Export CSV Reports by using below command:
python reports.py
## You can see output like this - 
- Reports exported to docs/reports
This will create a CSV file in your docs/reports


## Notes
- Tech: Flask + SQLite + SQLAlchemy.
- Data model & APIs are in `DESIGN.md`.
- Added AI conversation screenshots to `ai_log/` directory.

