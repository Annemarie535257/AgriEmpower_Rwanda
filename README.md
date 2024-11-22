# AgriEmpower Rwanda

Welcome to AgriEmpower Rwanda! This project is designed to help farmers, cooperatives, and financial institutions manage their interactions efficiently.

Below you will find the step-by-step instructions to set up the project locally. Please ensure you follow each step carefully to get the project running without issues.

## Prerequisites

1. **Python**: Ensure Python 3.8 or above is installed. You can download it from [python.org](https://www.python.org/downloads/).
2. **Git**: Ensure Git is installed to clone the repository. You can download it from [git-scm.com](https://git-scm.com/downloads).
3. **PostgreSQL**: Ensure PostgreSQL is installed. You can download it from [postgresql.org](https://www.postgresql.org/download/).
4. **Virtual Environment (optional but recommended)**: For isolating the project's dependencies.
5. **Neon Database Account**: You'll need credentials to connect to your Neon PostgreSQL database.
6. **SMTP Email Setup**: Set up SMTP credentials for sending emails during registration.

## Setup Instructions

### 1. Clone the Repository

Clone the repository from GitHub to your local machine:

```bash
$ git clone https://github.com/Annemarie535257/AgriEmpower_Rwanda.git
$ cd AgriEmpower_Rwanda
```

### 2. Create a Virtual Environment

Create and activate a virtual environment to keep your dependencies isolated.

- **Windows**:
  ```bash
  $ python -m venv venv
  $ venv\Scripts\activate
  ```

- **macOS/Linux**:
  ```bash
  $ python3 -m venv venv
  $ source venv/bin/activate
  ```

### 3. Install Dependencies

With the virtual environment activated, install the required dependencies:

```bash
$ pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory of your project. Fill in the following details (you can refer to `.env.example` if available):

```
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PWD=your_database_password
DB_HOST=your_neon_database_host
DB_PORT=5432
SECRET_KEY=your_django_secret_key
EMAIL_HOST=your_smtp_host
EMAIL_PORT=your_smtp_port
EMAIL_HOST_USER=your_smtp_email
EMAIL_HOST_PASSWORD=your_smtp_password
```

Replace the values with your actual credentials.

### 5. Database Setup

Ensure you have PostgreSQL running, and you have created a database with the name specified in your `.env` file.

Run the following commands to create the necessary tables in your database:

```bash
$ python manage.py makemigrations
$ python manage.py migrate
```

### 6. Create a Superuser

To access the Django Admin, create a superuser:

```bash
$ python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Collect Static Files

Collect all static files for the project:

```bash
$ python manage.py collectstatic
```

### 8. Run the Development Server

You can now run the local development server:

```bash
$ python manage.py runserver
```

Open your browser and navigate to `http://127.0.0.1:8000` to see the application in action.

### 9. Access Admin Panel

To access the admin panel, go to:

```
http://127.0.0.1:8000/admin/
```

Log in with the superuser credentials you created earlier.

## Troubleshooting

- **Database Connection Issues**: Double-check your database credentials in the `.env` file. Make sure your Neon database is active.
- **Dependency Issues**: Ensure all packages are installed by running `pip install -r requirements.txt`.
- **Server Error**: Check the server logs for any traceback and debug accordingly.

## Deployment

If you wish to deploy this project, you can use services like **Render** or **Vercel**. Make sure to set up the database and environment variables correctly on the deployed platform.

## Additional Information

- **Django Admin**: The Django admin interface allows you to manage the database, add users, and perform CRUD operations on models.
- **Neon Database**: Make sure to set up connection pooling if using a managed service to avoid connection limits.

For any additional questions, please contact the repository owner or create an issue on GitHub.

Happy coding!
