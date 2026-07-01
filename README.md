# College Complaint Portal

A web application for managing and resolving complaints within a college environment.

## Features

### User Roles
- **Student**: Can submit complaints, view complaint history, and rate resolved complaints.
- **Faculty**: Same as student with additional roles based on escalation.
- **Non-Teaching Staff**: Same as student and faculty.
- **Class Teacher**: First level of escalation for complaints.
- **HOD (Head of Department)**: Second level of escalation.
- **Principal**: Third level of escalation.
- **Admin**: Full access to all complaints and management.

### Complaint Management
- **Submit Complaints**: Students/staff can file complaints with category, description, and optionally anonymously.
- **Anonymous Complaints**: Option to submit complaints without revealing identity.
- **Evidence Upload**: Attach files as evidence for complaints.
- **Complaint Tracking**: Track complaint status (Pending, Escalated, Resolved) and history.
- **Escalation System**: Complaints automatically escalate to higher authorities if not resolved within time.
- **Resolve Complaints**: Authorized users can mark complaints as resolved and send notifications.
- **Rating System**: Users can rate resolved complaints (1-5 stars).

### User Management
- **Sign Up**: New users can register and choose their role.
- **Login/Logout**: Secure authentication using Django's built-in auth system.
- **Password Reset**: Forgot password functionality with OTP sent via email.
- **User Profiles**: Each user has a profile linked to their account.

### Dashboard
- Personalized dashboard based on user role.
- Complaint statistics (total, resolved, pending, escalated).
- Category-wise complaint distribution.
- Status-wise complaint breakdown.
- Average rating of resolved complaints.
- Overdue complaints count (for admins).

## Tech Stack

### Backend
- **Framework**: Django (version 5.2.8)
- **Language**: Python
- **Email**: Django's email backend (configured for Gmail)

### Frontend
- **Templates**: Django Template Language (DTL)
- **Styling**: Custom CSS
- **Interactivity**: Vanilla JavaScript

### Database
- **Database**: SQLite3 (default Django database)
- **Models**:
  - User (built-in Django model, extended with Profile)
  - Profile (additional user info including role and phone number)
  - Category (complaint categories)
  - Complaint (main complaint model with sentiment analysis)
  - PasswordResetCode (for password reset functionality)

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd college-complain-portal
   ```

2. **Create a virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   # Activate on Windows
   .\venv\Scripts\activate
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data for TextBlob**
   ```bash
   python -m textblob.download_corpora
   ```

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional but recommended for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   Open your web browser and go to `http://localhost:8000/`

## Configuration

### Email Configuration
The application uses Gmail's SMTP server to send emails. Update the email settings in `complaint_portal/settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your email
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use an app-specific password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

### Security
- `SECRET_KEY`: Keep this secret, especially in production. Consider using environment variables.
- `DEBUG`: Set to `False` in production.
- `ALLOWED_HOSTS`: Add your domain name(s) in production.

## Project Structure

```
college-complain-portal/
├── complaint_portal/       # Main Django project
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # Project settings
│   ├── urls.py             # Project-level URLs
│   └── wsgi.py
├── portal/                 # Main application
│   ├── __init__.py
│   ├── admin.py            # Admin panel configuration
│   ├── apps.py
│   ├── forms.py            # Form definitions
│   ├── management/         # Custom management commands
│   ├── migrations/         # Database migrations
│   ├── models.py           # Database models
│   ├── signals.py          # Django signals
│   ├── static/             # Static files (CSS, JS, images)
│   ├── templates/          # HTML templates
│   │   ├── portal/         # App templates
│   │   └── registration/   # Auth templates
│   ├── urls.py             # App-level URLs
│   └── views.py            # View functions
├── media/                  # Uploaded media files
├── db.sqlite3              # SQLite database
├── manage.py               # Django management script
└── requirements.txt        # Project dependencies
```

## Usage

### Sign Up
1. Go to `/accounts/signup/`
2. Fill in your details and choose your role
3. Click "Sign Up"

### Login
1. Go to `/accounts/login/`
2. Enter your username and password
3. Click "Login"

### Submit a Complaint
1. After logging in, go to the dashboard
2. Click "New Complaint"
3. Fill in the complaint details (category, description, evidence if any, anonymous option)
4. Submit the complaint

### Reset Password
1. From the login page, click "Forgot Password"
2. Enter your email address
3. You will receive a 4-digit code
4. Enter the code
5. Set a new password

## Admin Panel
Access the admin panel at `/admin/` to manage users, categories, and complaints.

## Future Enhancements
- Add real-time notifications using Django Channels
- Implement a reporting system with charts and graphs
- Add mobile-responsive design
- Integrate SMS notifications
- Add more analytics and insights
- Role-based access control (RBAC) with more granular permissions
- Multi-department support
- Knowledge base integration

## License
This project is licensed under the MIT License.
