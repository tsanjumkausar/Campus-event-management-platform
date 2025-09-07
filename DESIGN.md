# Campus Event Reporting – Design Document

## Scope
A minimal reporting system for a Campus Event Management Platform with:
- Admin portal to create events (per college).
- Student app to register, check-in (attendance), and submit feedback.
- Reports for event popularity and student participation, plus a few bonus views.

## Data to Track
- Event creation
- Student registration
- Attendance
- Feedback (rating 1–5)

## ER Diagram (mermaid)
```mermaid
erDiagram
    COLLEGES ||--o{ STUDENTS : has
    COLLEGES ||--o{ EVENTS : hosts
    STUDENTS ||--o{ REGISTRATIONS : registers_for
    STUDENTS ||--o{ ATTENDANCE : checks_in
    STUDENTS ||--o{ FEEDBACK : rates
    EVENTS ||--o{ REGISTRATIONS : includes
    EVENTS ||--o{ ATTENDANCE : records
    EVENTS ||--o{ FEEDBACK : receives

    COLLEGES {
      int id PK
      string name
    }
    STUDENTS {
      int id PK
      int college_id FK
      string roll_no
      string name
      string email
    }
    EVENTS {
      int id PK
      int college_id FK
      string title
      string type
      datetime start_time
      datetime end_time
      int capacity
    }
    REGISTRATIONS {
      int id PK
      int student_id FK
      int event_id FK
      datetime ts
    }
    ATTENDANCE {
      int id PK
      int student_id FK
      int event_id FK
      string status  // present|absent
      datetime ts
    }
    FEEDBACK {
      int id PK
      int student_id FK
      int event_id FK
      int rating  // 1..5
      text comment
      datetime ts
    }
```

### Key Constraints
- Unique (college_id, roll_no) per student.
- Unique (student_id, event_id) for registrations, attendance, and feedback.
- Rating must be 1–5.

## API Design (HTTP/JSON)
- `POST /colleges` → `{name}` → `{id,name}`
- `POST /students` → `{college_id, roll_no, name, email}` → `{id}`
- `POST /events` → `{college_id,title,type,start_time,end_time,capacity?}` → `{id}`
- `POST /register` → `{student_id,event_id}` → `{id}`
- `POST /attendance` → `{student_id,event_id,status?}` → `{id}`
- `POST /feedback` → `{student_id,event_id,rating,comment?}` → `{id}`
- `GET /reports/event-metrics?event_id=` → per-event metrics
- `GET /reports/event-popularity` → all events sorted by registrations
- `GET /reports/student-participation` → events attended per student
- **Bonus**
  - `GET /reports/top-active-students` → top 3 by events attended
  - `GET /reports/event-popularity/by-type?type=Workshop` → popularity filtered by type

## Workflows (sequence summaries)
1. **Registration**
   - Student selects event → `POST /register` (idempotent via unique constraint).
2. **Attendance**
   - On event day, staff scans QR/roll → `POST /attendance` with `present`/`absent`.
3. **Reporting**
   - Admin opens reports endpoints or runs `reports.py` to export CSVs.

## Assumptions & Edge Cases
- Duplicate registration is blocked via DB uniqueness.
- Attendance can be marked once per student/event; updates require deleting/re-adding (simple prototype).
- Feedback optional; one feedback per student/event.
- Cancelled events can be identified by omitting attendance/feedback or adding a later `status` field (out of scope for MVP).
- Scale: ~50 colleges × 500 students × 20 events/sem → well within SQLite/Flask for prototype; production would use Postgres and per-college partitioning (schema-per-college or a single schema with `college_id` and indexes). Event IDs are globally unique here; in production, they could be UUIDv7 to avoid collisions and ease sharding.

## Report Definitions
- **Event Popularity:** `count(registrations)` per event (descending).
- **Student Participation:** `count(attendance where present|absent)` per student. For strict attendance, filter `present` only.
- **Attendance %:** `present / registrations`.
- **Average Feedback:** `avg(rating)` per event.

## Simple UI (wireframe notes)
- Event list (filter by type).
- Event detail → Register button.
- Check-in screen (scan or search student).

## Non-Goals
- Auth, roles, real mobile UI, bulk imports, notifications, reschedule flows.

## Future Enhancements
- Role-based auth (Admin/Staff/Student).
- Attendance updates & audit log.
- Soft-delete and event status (`cancelled`, `completed`).
- Pagination, caching, and warehouse-style denormalized report tables.
