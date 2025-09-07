import sqlite3, os, csv
from datetime import datetime, timedelta

BASE = os.path.dirname(os.path.dirname(__file__))
DB = os.path.join(BASE, "events_offline_demo.db")
OUT = os.path.join(BASE, "docs", "reports")
os.makedirs(OUT, exist_ok=True)

con = sqlite3.connect(DB)
cur = con.cursor()

cur.executescript("""
PRAGMA foreign_keys=ON;
DROP TABLE IF EXISTS feedback;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS registrations;
DROP TABLE IF EXISTS events;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS colleges;

CREATE TABLE colleges(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL);
CREATE TABLE students(id INTEGER PRIMARY KEY, college_id INTEGER NOT NULL, roll_no TEXT NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL, UNIQUE(college_id, roll_no));
CREATE TABLE events(id INTEGER PRIMARY KEY, college_id INTEGER NOT NULL, title TEXT NOT NULL, type TEXT NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL, capacity INTEGER);
CREATE TABLE registrations(id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL, event_id INTEGER NOT NULL, ts TEXT NOT NULL, UNIQUE(student_id,event_id));
CREATE TABLE attendance(id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL, event_id INTEGER NOT NULL, status TEXT NOT NULL, ts TEXT NOT NULL, UNIQUE(student_id,event_id));
CREATE TABLE feedback(id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL, event_id INTEGER NOT NULL, rating INTEGER NOT NULL, comment TEXT, ts TEXT NOT NULL, UNIQUE(student_id,event_id));
""")

# seed
cur.execute("INSERT INTO colleges(name) VALUES (?)", ("NIT Springs",))
c1 = cur.lastrowid
cur.execute("INSERT INTO colleges(name) VALUES (?)", ("IIT Horizon",))
c2 = cur.lastrowid

for i in range(1,11):
    cur.execute("INSERT INTO students(college_id,roll_no,name,email) VALUES (?,?,?,?)",
                (c1, f"CSE{i:03d}", f"Student {i}", f"s{i}@nits.edu"))
for i in range(1,6):
    cur.execute("INSERT INTO students(college_id,roll_no,name,email) VALUES (?,?,?,?)",
                (c2, f"ECE{i:03d}", f"Horizon {i}", f"h{i}@iith.edu"))

from datetime import datetime, timedelta
now = datetime.utcnow()
events = [
    (c1, "Intro to GenAI", "Seminar", now, now+timedelta(hours=2), 200),
    (c1, "Web Dev Bootcamp", "Workshop", now+timedelta(days=1), now+timedelta(days=1,hours=3), 100),
    (c2, "Tech Fest 2025", "Fest", now+timedelta(days=5), now+timedelta(days=5,hours=8), None),
]
for e in events:
    cur.execute("INSERT INTO events(college_id,title,type,start_time,end_time,capacity) VALUES (?,?,?,?,?,?)",
                (e[0], e[1], e[2], e[3].isoformat(), e[4].isoformat(), e[5]))

# map ids
cur.execute("SELECT id FROM events ORDER BY id")
eids = [r[0] for r in cur.fetchall()]
cur.execute("SELECT id,college_id FROM students ORDER BY id")
students = cur.fetchall()

# registrations
import random
def reg(student_id, event_id):
    cur.execute("INSERT INTO registrations(student_id,event_id,ts) VALUES (?,?,?)",
                (student_id, event_id, datetime.utcnow().isoformat()))

for sid, college in students[:8]:
    reg(sid, eids[0])
for sid, college in students[2:12]:
    reg(sid, eids[1])
for sid, college in students:
    if college == c2 or (sid % 2 == 0):
        reg(sid, eids[2])

# attendance
def att(student_id,event_id,status):
    cur.execute("INSERT INTO attendance(student_id,event_id,status,ts) VALUES (?,?,?,?)",
                (student_id, event_id, status, datetime.utcnow().isoformat()))
cur.execute("SELECT student_id,event_id FROM registrations")
for sid,eid in cur.fetchall():
    status = "present" if (sid % 3 != 0) else "absent"
    att(sid,eid,status)

# feedback every other student
def fb(student_id,event_id,rating,comment):
    cur.execute("INSERT INTO feedback(student_id,event_id,rating,comment,ts) VALUES (?,?,?,?,?)",
                (student_id,event_id,rating,comment,datetime.utcnow().isoformat()))
cur.execute("SELECT student_id,event_id FROM registrations")
for sid,eid in cur.fetchall():
    if sid % 2 == 0:
        fb(sid,eid,(sid % 5)+1,"Good")

con.commit()

# Reports
# Event popularity
cur.execute("""
SELECT e.id, e.title, e.type, COUNT(r.id) as registrations
FROM events e
LEFT JOIN registrations r ON r.event_id = e.id
GROUP BY e.id
ORDER BY registrations DESC
""")
rows1 = [{"event_id":r[0],"title":r[1],"type":r[2],"registrations":r[3]} for r in cur.fetchall()]
with open(os.path.join(OUT,"event_popularity.csv"),"w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=["event_id","title","type","registrations"]); w.writeheader(); w.writerows(rows1)

# Student participation
cur.execute("""
SELECT s.id, s.name, COUNT(a.id) as events_attended
FROM students s
LEFT JOIN attendance a ON a.student_id = s.id
GROUP BY s.id
ORDER BY events_attended DESC, s.name ASC
""")
rows2 = [{"student_id":r[0],"name":r[1],"events_attended":r[2]} for r in cur.fetchall()]
with open(os.path.join(OUT,"student_participation.csv"),"w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=["student_id","name","events_attended"]); w.writeheader(); w.writerows(rows2)

# Top 3 most active students
with open(os.path.join(OUT,"top3_active_students.csv"),"w",newline="") as f:
    w=csv.DictWriter(f, fieldnames=["student_id","name","events_attended"]); w.writeheader(); w.writerows(rows2[:3])

print("Offline demo DB and CSV reports generated.")
