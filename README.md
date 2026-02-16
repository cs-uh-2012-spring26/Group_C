# Fitness Class Management System_GroupC

This project is a simplified backend API for managing fitness classes, built using Flask for Sprint 1 of CS-UH 2012 Software Engineering.

Currently implemented features:

---

## Feature 1: Create Class

**Endpoint:** `POST /classes`

Allows an Admin or Trainer to create a new fitness class.

### Requirements:
- The request must include header:
  ```
  Role: Admin
  ```
  or
  ```
  Role: Trainer
  ```

- Required JSON fields:
  - title
  - venue
  - capacity (must be a positive number)
  - date
  - start_time
  - end_time

### Responses:
- `201 Created` – Class created successfully
- `400 Bad Request` – Missing or invalid input
- `403 Forbidden` – Unauthorized role

Classes are stored persistently in `classes_db.json`.

---

## Feature 2: View Class List

**Endpoint:** `GET /classes`

- Accessible to all users.
- Returns all created classes.
- Returns a message if no classes exist.

---

# How to Run the Project

## 1. Clone the Repository

```bash
git clone <repository-url>
cd Group_C
```

## 2. Create and Activate Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the Server

```bash
python app.py
```

The server will run at:

```
http://127.0.0.1:5000
```

Note: The root URL (`/`) is not defined. Use `/classes` to interact with the API.

---

# Notes

- Class data is saved in `classes_db.json` to allow persistence between server restarts.
