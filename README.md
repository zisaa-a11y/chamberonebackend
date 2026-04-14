# The Chamber One - Backend

A Django REST Framework backend for "The Chamber One" legal services application.

## 🚀 Features

- **User Authentication & Authorization** - Custom user model with role-based access (Admin, Lawyer, Client)
- **Lawyer Management** - Lawyer profiles, practice areas, and availability scheduling
- **Appointment System** - Book consultations with lawyers
- **Case Management** - Track legal cases, documents, notes, and timelines
- **Payment & Invoicing** - Invoice generation and payment processing
- **Blog System** - Content management with categories, tags, and comments
- **Landing Page Management** - Dynamic content for the public website

## 📸 Admin Panel Screenshots

### Dashboard Overview
<p align="center">
  <img src="screenshots/admin_dashboard.png" alt="Admin Dashboard" width="800"/>
</p>

*Main admin dashboard showing all available modules including Appointments, Authentication, Blog & Content, Cases Management*

### Admin Dashboard (Extended View)
<p align="center">
  <img src="screenshots/admin_dashboard_extended.png" alt="Admin Dashboard Extended" width="800"/>
</p>

*Extended view showing Landing Page Content, Lawyers Management, Payments & Invoices, and User Accounts modules*

### Appointment Management
<p align="center">
  <img src="screenshots/add_appointment.png" alt="Add Appointment" width="800"/>
</p>

*Form for creating new appointments with client selection, lawyer assignment, date/time picker, duration settings, and appointment type*

### User & Group Management
<p align="center">
  <img src="screenshots/add_group.png" alt="Add Group" width="800"/>
</p>

*Permission management interface for creating user groups with granular permission control*

### Case Management
<p align="center">
  <img src="screenshots/add_case.png" alt="Add Case" width="800"/>
</p>

*Case creation form with case number, title, description, court name, client/lawyer assignment, and practice area selection*

### Contact Submissions
<p align="center">
  <img src="screenshots/contact_submission.png" alt="Contact Submission" width="800"/>
</p>

*Contact form submission management with read/replied status tracking*

### User Registration
<p align="center">
  <img src="screenshots/add_user.png" alt="Add User" width="800"/>
</p>

*User creation form with email-based authentication, role selection (Client/Lawyer/Admin), and staff status*

### Invoice Items
<p align="center">
  <img src="screenshots/invoice_item.png" alt="Invoice Item" width="800"/>
</p>

*Invoice item creation with description, quantity, unit price, and total amount calculation*

## 🛠️ Tech Stack

- **Framework:** Django 5.x
- **API:** Django REST Framework
- **Database:** SQLite (Development) / PostgreSQL (Production)
- **Authentication:** JWT Token Authentication
- **CORS:** django-cors-headers
- **Filtering:** django-filter

## 📁 Project Structure

```
thechamberonebackend/
├── accounts/           # User authentication and profiles
│   ├── models.py       # Custom User and ClientProfile models
│   ├── views.py        # Auth views (Register, Login, Profile)
│   ├── serializers.py  # User serializers
│   └── urls.py         # Auth routes
├── lawyers/            # Lawyer management
│   ├── models.py       # LawyerProfile, PracticeArea, Availability
│   ├── views.py        # Lawyer API views
│   ├── serializers.py  # Lawyer serializers
│   └── urls.py         # Lawyer routes
├── appointments/       # Appointment booking
│   ├── models.py       # Appointment model
│   ├── views.py        # Appointment API views
│   ├── serializers.py  # Appointment serializers
│   └── urls.py         # Appointment routes
├── cases/              # Case management
│   ├── models.py       # Case, CaseDocument, CaseNote, CaseTimeline
│   ├── views.py        # Case API views
│   ├── serializers.py  # Case serializers
│   └── urls.py         # Case routes
├── payments/           # Invoice and payment processing
│   ├── models.py       # Invoice, InvoiceItem, Payment models
│   ├── views.py        # Payment API views
│   ├── serializers.py  # Payment serializers
│   └── urls.py         # Payment routes
├── blog/               # Blog content management
│   ├── models.py       # Category, Tag, BlogPost, Comment
│   ├── views.py        # Blog API views
│   ├── serializers.py  # Blog serializers
│   └── urls.py         # Blog routes
├── landing/            # Landing page content
│   ├── models.py       # HeroSection, Service, Testimonial, etc.
│   ├── views.py        # Landing page API views
│   ├── serializers.py  # Landing serializers
│   └── urls.py         # Landing routes
├── core/               # Main project settings
│   ├── settings.py     # Django settings
│   └── urls.py         # Main URL configuration
├── manage.py           # Django management script
└── requirements.txt    # Python dependencies
```

## 🔧 Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

1. **Clone the repository**
```bash
git clone git@github.com:zisaa-a11y/the_chamber_backend.git
cd the_chamber_backend
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

If you want to deploy backend code without changing the production database schema, skip the `migrate` step during deployment and run it manually only when you intentionally need a schema change.

5. **Create superuser**
```bash
python manage.py createsuperuser
```

6. **Run the development server**
```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

## 📚 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounts/register/` | Register new user |
| POST | `/api/accounts/login/` | User login |
| GET | `/api/accounts/profile/` | Get user profile |
| PUT | `/api/accounts/profile/` | Update user profile |

### Lawyers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/lawyers/` | List all lawyers |
| GET | `/api/lawyers/{id}/` | Get lawyer details |
| GET | `/api/lawyers/practice-areas/` | List practice areas |
| GET | `/api/lawyers/{id}/availability/` | Get lawyer availability |

### Appointments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/appointments/` | List appointments |
| POST | `/api/appointments/` | Create appointment |
| GET | `/api/appointments/{id}/` | Get appointment details |
| PUT | `/api/appointments/{id}/` | Update appointment |
| DELETE | `/api/appointments/{id}/` | Cancel appointment |

### Cases
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cases/` | List cases |
| POST | `/api/cases/` | Create case |
| GET | `/api/cases/{id}/` | Get case details |
| PUT | `/api/cases/{id}/` | Update case |
| GET | `/api/cases/{id}/documents/` | Get case documents |
| GET | `/api/cases/{id}/notes/` | Get case notes |
| GET | `/api/cases/{id}/timeline/` | Get case timeline |

### Payments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/payments/invoices/` | List invoices |
| POST | `/api/payments/invoices/` | Create invoice |
| GET | `/api/payments/invoices/{id}/` | Get invoice details |
| POST | `/api/payments/` | Create payment |

### Blog
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/blog/posts/` | List blog posts |
| GET | `/api/blog/posts/{slug}/` | Get post by slug |
| GET | `/api/blog/categories/` | List categories |
| GET | `/api/blog/tags/` | List tags |
| POST | `/api/blog/posts/{id}/comments/` | Add comment |

### Landing Page
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/landing/hero/` | Get hero sections |
| GET | `/api/landing/services/` | Get services |
| GET | `/api/landing/testimonials/` | Get testimonials |
| GET | `/api/landing/team/` | Get team members |
| GET | `/api/landing/faqs/` | Get FAQs |
| GET | `/api/landing/statistics/` | Get statistics |
| POST | `/api/landing/contact/` | Submit contact form |

## 👤 Default Admin Credentials

| Field | Value |
|-------|-------|
| Email | `admin@example.com` |
| Password | `admin123` |

⚠️ **Note:** Change these credentials before deploying to production!

## 🔒 Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for PostgreSQL production)
DATABASE_URL=postgres://user:password@localhost:5432/thechamberone

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 🧪 Running Tests

```bash
python manage.py test
```

## 📝 License

This project is licensed under the MIT License.

## 👥 Contributors

- **Thingkers** - Development Team

---

Made with ❤️ for The Chamber One Legal Services
