from flask import Flask, request, jsonify
from datetime import datetime
from dateutil import parser as dateparser
from models import db, College, Student, Event, Registration, Attendance, Feedback

def create_app(db_path="sqlite:///events.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health():
        return {"status":"ok"}

    # Admin: create college
    @app.post("/colleges")
    def create_college():
        data = request.get_json()
        c = College(name=data["name"])
        db.session.add(c)
        db.session.commit()
        return jsonify({"id": c.id, "name": c.name}), 201

    # Admin: create student
    @app.post("/students")
    def create_student():
        data = request.get_json()
        s = Student(college_id=data["college_id"], roll_no=data["roll_no"], name=data["name"], email=data["email"])
        db.session.add(s)
        db.session.commit()
        return jsonify({"id": s.id}), 201

    # Admin: create event
    @app.post("/events")
    def create_event():
        data = request.get_json()
        e = Event(
            college_id=data["college_id"],
            title=data["title"],
            type=data["type"],
            start_time=dateparser.parse(data["start_time"]),
            end_time=dateparser.parse(data["end_time"]),
            capacity=data.get("capacity")
        )
        db.session.add(e)
        db.session.commit()
        return jsonify({"id": e.id}), 201

    # Student: register for event
    @app.post("/register")
    def register():
        data = request.get_json()
        r = Registration(student_id=data["student_id"], event_id=data["event_id"])
        db.session.add(r)
        db.session.commit()
        return jsonify({"id": r.id}), 201

    # Staff: mark attendance
    @app.post("/attendance")
    def mark_attendance():
        data = request.get_json()
        a = Attendance(student_id=data["student_id"], event_id=data["event_id"], status=data.get("status","present"))
        db.session.add(a)
        db.session.commit()
        return jsonify({"id": a.id}), 201

    # Student: submit feedback
    @app.post("/feedback")
    def submit_feedback():
        data = request.get_json()
        f = Feedback(student_id=data["student_id"], event_id=data["event_id"], rating=data["rating"], comment=data.get("comment"))
        db.session.add(f)
        db.session.commit()
        return jsonify({"id": f.id}), 201

    # Reports
    # Event metrics for one event
    @app.get("/reports/event-metrics")
    def event_metrics():
        event_id = int(request.args["event_id"])
        from sqlalchemy import func
        reg_count = db.session.query(func.count(Registration.id)).filter_by(event_id=event_id).scalar()
        att_present = db.session.query(func.count(Attendance.id)).filter_by(event_id=event_id, status="present").scalar()
        att_total = db.session.query(func.count(Attendance.id)).filter_by(event_id=event_id).scalar()
        avg_rating = db.session.query(func.avg(Feedback.rating)).filter_by(event_id=event_id).scalar()
        attendance_pct = (att_present / reg_count * 100.0) if reg_count else 0.0
        return jsonify({
            "event_id": event_id,
            "registrations": reg_count,
            "attendance_present": att_present,
            "attendance_records": att_total,
            "attendance_pct": round(attendance_pct,2),
            "avg_feedback": round(float(avg_rating),2) if avg_rating is not None else None
        })

    # Event Popularity Report (sorted by registrations)
    @app.get("/reports/event-popularity")
    def event_popularity():
        from sqlalchemy import func
        q = db.session.query(
            Event.id, Event.title, Event.type, Event.college_id,
            func.count(Registration.id).label("registrations")
        ).outerjoin(Registration, Registration.event_id == Event.id).group_by(Event.id).order_by(func.count(Registration.id).desc())
        return jsonify([{"event_id":i, "title":t, "type":ty, "college_id":c, "registrations":r} for i,t,ty,c,r in q])

    # Student Participation Report
    @app.get("/reports/student-participation")
    def student_participation():
        from sqlalchemy import func
        q = db.session.query(
            Student.id, Student.name,
            func.count(Attendance.id).label("events_attended")
        ).outerjoin(Attendance, Attendance.student_id == Student.id).group_by(Student.id).order_by(func.count(Attendance.id).desc(), Student.name.asc())
        return jsonify([{"student_id":i, "name":n, "events_attended":ea} for i,n,ea in q])

    # Top 3 most active students (bonus)
    @app.get("/reports/top-active-students")
    def top_active_students():
        from sqlalchemy import func
        q = db.session.query(
            Student.id, Student.name, func.count(Attendance.id).label("events_attended")
        ).outerjoin(Attendance, Attendance.student_id == Student.id).group_by(Student.id).order_by(func.count(Attendance.id).desc()).limit(3)
        return jsonify([{"student_id":i, "name":n, "events_attended":ea} for i,n,ea in q])

    # Flexible filter by event type (bonus)
    @app.get("/reports/event-popularity/by-type")
    def event_popularity_by_type():
        from sqlalchemy import func
        etype = request.args.get("type")
        q = db.session.query(
            Event.type, Event.id, Event.title, func.count(Registration.id).label("registrations")
        ).outerjoin(Registration, Registration.event_id == Event.id)
        if etype:
            q = q.filter(Event.type == etype)
        q = q.group_by(Event.id).order_by(func.count(Registration.id).desc())
        return jsonify([{"event_id":i, "title":t, "type":ty, "registrations":r} for ty,i,t,r in q])

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000, debug=True)
