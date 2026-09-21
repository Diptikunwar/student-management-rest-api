# Student Management REST API

A backend REST API built using **Python, Flask, MySQL, and JWT Authentication** for managing student records.

## Features

- User login with JWT authentication
- Role-based access control
- Add a student
- Update student details
- Delete a student
- Fetch all students
- Fetch student by ID
- Search students by name
- Add multiple students using a single API request
- Input validation
- Proper HTTP status codes and error responses
- MySQL database integration
- Password hashing
- REST API testing using Postman
- Automated API tests using Pytest
- Environment variables using `.env`

## Tech Stack

- Python
- Flask
- MySQL
- REST API
- JWT
- PyJWT
- Werkzeug
- Postman
- Pytest
- Git & GitHub

## Project Structure

```text
student-management-rest-api/
│
├── new.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env
│
└── tests/
    └── test_api.py