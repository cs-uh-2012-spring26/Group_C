---

# Fitness Class Management System — Group C

This project is a simplified backend REST API for managing fitness classes, built using **Flask** for **Sprint 1 — CS-UH 2012 Software Engineering**.

The system allows admins/trainers to create classes and members to book them.

---

## Implemented Features

---

## Feature 1: Create Class

**Endpoint:** `POST /classes`

Allows an **Admin** or **Trainer** to create a new fitness class.

### Required Header

```
Role: Admin
```

or

```
Role: Trainer
```

### Required JSON Body

```json
{
  "title": "Yoga",
  "venue": "Studio 1",
  "capacity": 10,
  "date": "2026-02-20",
  "start_time": "10:00",
  "end_time": "11:00"
}
```

### Responses

| Status            | Meaning                    |
| ----------------- | -------------------------- |
| `201 Created`     | Class created successfully |
| `400 Bad Request` | Missing or invalid input   |
| `403 Forbidden`   | Unauthorized role          |

Classes are saved in `classes_db.json`.

---

## Feature 2: View Class List

**Endpoint:** `GET /classes`

Accessible to **everyone** (Admin, Trainer, Member, Guest).

### Behavior

* Returns all available classes
* If none exist → returns message `"No classes available"`

---

## Feature 3: Book Class

**Endpoint:** `POST /classes/<class_id>/book`

Allows a **Member** to book a fitness class.

### Required Headers

```
Role: Member
User: <member_name>
```

### Responses

| Status            | Meaning                      |
| ----------------- | ---------------------------- |
| `200 OK`          | Booking successful           |
| `400 Bad Request` | Class full or already booked |
| `403 Forbidden`   | Only members can book        |
| `404 Not Found`   | Class does not exist         |

### Rules

* A member cannot book the same class twice
* Booking fails if capacity is full

---

## Feature 4: View Members of a Class

**Endpoint:** `GET /classes/<class_id>/members`

Allows **Admin or Trainer** to view booked members.

### Required Header

```
Role: Admin
```

or

```
Role: Trainer
```

### Responses

| Status          | Meaning                                 |
| --------------- | --------------------------------------- |
| `200 OK`        | Returns list of booked members          |
| `200 OK`        | "No members have booked this class yet" |
| `403 Forbidden` | Unauthorized role                       |
| `404 Not Found` | Class not found                         |

---

## How to Run the Project

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Group_C
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
python app.py
```

Server runs at:

```
http://127.0.0.1:5000
```

> Note: The root URL `/` is not implemented. Use `/apidocs`.

---

## Data Persistence

All class data is stored locally in:

```
classes_db.json
```

This allows classes and bookings to remain saved after restarting the server.

---

