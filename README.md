# 🚗 Vehicle Service Management System

A web-based **Vehicle Service Management System** built using **Flask, MySQL, HTML, and CSS**.
This application allows users to book vehicle services, track service status, and enables admins to manage operations efficiently through a dashboard.

---

## 📌 Features

### 👤 User Module

* User Registration & Login
* Add Vehicle Details
* Book Service Appointments
* Track Service Status
* View Service History

### 🛠️ Admin Module

* Admin Dashboard
* View & Manage Service Requests
* Update Service Status (Pending → In Progress → Completed)
* Generate Bills
* Monitor overall system activity

---

## 🧱 Tech Stack

* **Frontend:** HTML, CSS, Bootstrap
* **Backend:** Python (Flask)
* **Database:** MySQL
* **Version Control:** Git & GitHub

---

## 📂 Project Structure

```
vehicle-service-management/
│
├── app.py                  # Main Flask application
├── schema.sql              # Database schema (MySQL)
├── .gitignore              # Git ignore rules
├── LICENSE                 # License file
├── README.md               # Project documentation
│
├── templates/              # HTML templates (Flask uses this folder)
│   ├── base.html
│   ├── dashboard.html
│   ├── customers.html
│   ├── vehicles.html
│   ├── services.html
│   ├── mechanics.html
│   ├── orders.html
│   ├── order_detail.html
│   ├── payments.html
│
├── static/                 # Static files (CSS, JS)
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│
└── requirements.txt        # Python dependencies (Flask, MySQL, etc.)

```

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/ManteshB2006/Vehicle-Service-Management-System.git
cd Vehicle-Service-Management-System
```

### 2️⃣ Install dependencies

```bash
pip install flask mysql-connector-python
```

### 3️⃣ Setup Database

* Open MySQL
* Create database:

```sql
CREATE DATABASE vehicle_service_db;
```

* Import tables from `schema.sql`

### 4️⃣ Run the application

```bash
python app.py
```

* Open browser:

```
http://127.0.0.1:5000/
```

---

## 🔐 Default Roles

| Role  | Access                      |
| ----- | --------------------------- |
| User  | Book & track services       |
| Admin | Manage services & dashboard |

---

## 📊 Future Enhancements

* 🔒 Password hashing (bcrypt)
* 📧 Email notifications
* 📄 PDF invoice generation
* 📈 Analytics dashboard with charts
* 🔍 Search & filter functionality
* 🌐 REST API integration
  
---

## 🤝 Contributing

Contributions are welcome! Feel free to fork this repo and submit a pull request.

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

**Mantesh B**

* GitHub: https://github.com/ManteshB2006

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
