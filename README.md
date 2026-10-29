# Job Application Tracker

**Student:** Ainoa Perez-Calderon  
**University:** Florida International University  
**Course:** COP4751 – Advanced Database Management  
**Project:** Final Project

## Project Overview

The Job Application Tracker is a full-stack web application designed to help users organize their job search. Users can manage companies, job listings, applications, and professional contacts through a website connected to a MySQL database.

The application also includes a Job Match feature that compares a user's skills with the requirements of saved jobs and calculates a matching percentage.

## Technologies Used

- Python 3
- Flask
- MySQL 8.0
- MySQL Connector/Python
- HTML and CSS
- Jinja2 Templates
- python-dotenv
- Git and GitHub

## Main Features

### Dashboard
Displays an overview of the job search, including the total number of companies, jobs, applications, and contacts.

### Company Management
- Add new companies.
- View saved companies.
- Edit company information.
- Delete companies with confirmation.

### Job Management
- Add job opportunities associated with companies.
- View job listings.
- Edit job information.
- Delete job listings.
- Store required skills in a JSON database column.

### Application Tracking
- Record applications submitted for jobs.
- Track application dates and statuses.
- Record resume versions and cover letter information.
- Store interview notes using JSON.
- Edit and delete application records.

### Contact Management
- Add professional contacts.
- Associate contacts with companies.
- Store contact names, positions, email addresses, phone numbers, LinkedIn profiles, and notes.
- Edit and delete contacts.

### Job Match
- Enter personal skills separated by commas.
- Compare those skills against saved job requirements.
- Calculate the percentage of matching skills.
- Identify matching and missing skills.
- Display jobs ranked by match percentage.

## Database Design

The application uses a MySQL database named `job_tracker`, containing four main tables:

1. `companies` – Stores company information.
2. `jobs` – Stores job opportunities and their requirements.
3. `applications` – Stores application records and statuses.
4. `contacts` – Stores professional contact information.

The tables are connected using foreign keys:

- `jobs.company_id` references `companies.company_id`.
- `applications.job_id` references `jobs.job_id`.
- `contacts.company_id` references `companies.company_id`.

The database uses primary keys, foreign keys, and JSON data types.

The `schema.sql` file contains the database structure.

## Project Structure

    job_tracker/
    ├── app.py
    ├── database.py
    ├── schema.sql
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── README.md
    ├── AI_USAGE.md
    ├── static/
    │   └── style.css
    └── templates/
        ├── base.html
        ├── dashboard.html
        ├── companies.html
        ├── edit_company.html
        ├── jobs.html
        ├── edit_job.html
        ├── applications.html
        ├── edit_application.html
        ├── contacts.html
        ├── edit_contact.html
        └── job_match.html

## Installation and Setup

### Step 1: Download the Project

Clone the GitHub repository:

```bash
git clone https://github.com/ainoaperez-git/job-tracker.git
cd job-tracker
```

Alternatively, download the repository as a ZIP file and extract it.

### Step 2: Install Python Dependencies

Make sure Python 3 and MySQL Server are installed.

In the project directory, run:

```bash
python -m pip install -r requirements.txt
```

### Step 3: Set Up the MySQL Database

Open MySQL Workbench and connect to a local MySQL server.

Open the included `schema.sql` file and execute it to create the database tables.

If the exported SQL script does not automatically create the `job_tracker` database, create that database before executing the script.

### Step 4: Configure Environment Variables

Create a `.env` file in the main project folder using `.env.example` as a template.

Example:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=job_tracker
```

Replace `your_mysql_password` with your actual MySQL password.

The `.env` file is excluded from GitHub to protect database credentials.

### Step 5: Run the Application

Open a terminal in the project directory and run:

```bash
python app.py
```

### Step 6: Open the Website

Open a web browser and visit:

http://127.0.0.1:5000/

The navigation bar provides access to Dashboard, Companies, Jobs, Applications, Contacts, and Job Match.

## Job Match Algorithm

The Job Match feature compares user-provided skills against the required skills for each job.

The formula is:

**Match Percentage = (Matching Skills / Total Required Skills) × 100**

For example, a job requires:

Python, SQL, Flask, Excel

The user enters:

Python, SQL, Flask

Three of the four required skills match:

**(3 / 4) × 100 = 75%**

The application displays the match percentage and identifies any missing skills.

Jobs are ranked from highest to lowest match percentage.

## Testing

The application was developed and tested locally using Flask and MySQL Workbench.

Testing includes:

- Adding, viewing, editing, and deleting companies.
- Adding, viewing, editing, and deleting jobs.
- Adding, viewing, editing, and deleting applications.
- Adding, viewing, editing, and deleting contacts.
- Checking database relationships.
- Verifying dashboard statistics.
- Checking Job Match percentages and missing skills.
- Testing page navigation and forms.

## Generative AI Usage

ChatGPT was used during the development process to assist with writing Flask routes, connecting Python to MySQL, troubleshooting errors, implementing CRUD operations, designing HTML/CSS pages, and developing the Job Match feature.

Generated code was integrated into the project and tested through the local application.

Additional documentation is provided in `AI_USAGE.md`.

## Course Information

**COP4751 – Advanced Database Management**  
**Florida International University**  
**Final Project: Job Application Tracker**
