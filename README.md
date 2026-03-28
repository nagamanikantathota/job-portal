# Online Job Portal

A complete Job Portal Web Application built with Python and Django.

## Features
- **User Authentication**: Registration and Login for Job Seekers and Employers.
- **Job Seekers**:
    - Browse and search jobs by title, company, or location.
    - Apply for jobs with a resume upload.
    - View application history on the dashboard.
- **Employers**:
    - Post, edit, and delete job vacancies.
    - View applicants for each job posting, including their resumes.
- **Search Functionality**: Simple and effective search bar on the home and listing pages.

## Installation and Setup

1. **Prerequisites**: Ensure you have Python installed.
2. **Install Django**:
   ```bash
   pip install django
   ```
3. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. **Create a Superuser (Optional)**:
   ```bash
   python manage.py createsuperuser
   ```
5. **Run the Server**:
   ```bash
   python manage.py runserver
   ```
6. **Access the App**: Open your browser and go to `http://127.0.0.1:8000/`.

## Project Structure
- `job_portal/`: Project configuration (settings, urls).
- `jobs/`: Main application logic.
    - `models.py`: Database schema (Profile, Job, Application).
    - `views.py`: Request handling and business logic.
    - `forms.py`: Registration, Job Posting, and Application forms.
    - `templates/`: HTML templates for the frontend.
    - `static/css/`: Basic styling.
- `media/`: Directory where resumes are stored.
