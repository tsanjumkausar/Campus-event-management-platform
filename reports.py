from app import create_app, db, Event, Registration, Attendance, Feedback, Student
from sqlalchemy import func
import csv, os

def export_reports(outdir="docs/reports"):
    app = create_app()
    with app.app_context():
        # Event Popularity
        q1 = db.session.query(
            Event.id, Event.title, Event.type, func.count(Registration.id).label("registrations")
        ).outerjoin(Registration, Registration.event_id==Event.id).group_by(Event.id).order_by(func.count(Registration.id).desc())
        rows1 = [{"event_id":i, "title":t, "type":ty, "registrations":r} for i,t,ty,r in q1]
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir,"event_popularity.csv"),"w",newline="") as f:
            w=csv.DictWriter(f, fieldnames=rows1[0].keys()); w.writeheader(); w.writerows(rows1)

        # Student Participation
        q2 = db.session.query(
            Student.id, Student.name, func.count(Attendance.id).label("events_attended")
        ).outerjoin(Attendance, Attendance.student_id==Student.id).group_by(Student.id).order_by(func.count(Attendance.id).desc(), Student.name.asc())
        rows2 = [{"student_id":i, "name":n, "events_attended":ea} for i,n,ea in q2]
        with open(os.path.join(outdir,"student_participation.csv"),"w",newline="") as f:
            w=csv.DictWriter(f, fieldnames=rows2[0].keys()); w.writeheader(); w.writerows(rows2)

        # Top 3 active (bonus)
        rows3 = rows2[:3]
        with open(os.path.join(outdir,"top3_active_students.csv"),"w",newline="") as f:
            w=csv.DictWriter(f, fieldnames=rows3[0].keys()); w.writeheader(); w.writerows(rows3)

        print("Reports exported to", outdir)

if __name__ == "__main__":
    export_reports()
