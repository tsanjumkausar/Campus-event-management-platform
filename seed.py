from app import create_app, db, College, Student, Event, Registration, Attendance, Feedback
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    # Wipe existing
    db.drop_all()
    db.create_all()

    # Create colleges
    c1 = College(name="NIT Springs")
    c2 = College(name="IIT Horizon")
    db.session.add_all([c1,c2]); db.session.commit()

    # Students
    s = []
    for i in range(1,11):
        s.append(Student(college_id=c1.id, roll_no=f"CSE{i:03d}", name=f"Student {i}", email=f"s{i}@nits.edu"))
    for i in range(1,6):
        s.append(Student(college_id=c2.id, roll_no=f"ECE{i:03d}", name=f"Horizon {i}", email=f"h{i}@iith.edu"))
    db.session.add_all(s); db.session.commit()

    now = datetime.utcnow()
    # Events
    e1 = Event(college_id=c1.id, title="Intro to GenAI", type="Seminar", start_time=now+timedelta(days=1), end_time=now+timedelta(days=1, hours=2), capacity=200)
    e2 = Event(college_id=c1.id, title="Web Dev Bootcamp", type="Workshop", start_time=now+timedelta(days=2), end_time=now+timedelta(days=2, hours=3), capacity=100)
    e3 = Event(college_id=c2.id, title="Tech Fest 2025", type="Fest", start_time=now+timedelta(days=5), end_time=now+timedelta(days=5, hours=8))
    db.session.add_all([e1,e2,e3]); db.session.commit()

    # Registrations
    regs = []
    for st in s[:8]:
        regs.append(Registration(student_id=st.id, event_id=e1.id))
    for st in s[2:12]:
        regs.append(Registration(student_id=st.id, event_id=e2.id))
    for st in s:
        if st.college_id == c2.id or int(st.roll_no[-3:])%2==0:
            regs.append(Registration(student_id=st.id, event_id=e3.id))
    db.session.add_all(regs); db.session.commit()

    # Attendance (some present, some absent)
    atts = []
    for r in regs:
        status = "present" if (r.student_id % 3 != 0) else "absent"
        atts.append(Attendance(student_id=r.student_id, event_id=r.event_id, status=status))
    db.session.add_all(atts); db.session.commit()

    # Feedback (1-5)
    fbs = []
    for r in regs:
        if r.student_id % 2 == 0:  # every other student leaves feedback
            fbs.append(Feedback(student_id=r.student_id, event_id=r.event_id, rating=(r.student_id % 5)+1, comment="Good"))
    db.session.add_all(fbs); db.session.commit()

    print("Seeded sample data.")
