
import json
from datetime import datetime

import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, abort

from database import get_db_connection


app = Flask(__name__)


@app.route("/")
def dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("SELECT COUNT(*) AS total FROM companies")
        companies = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM jobs")
        jobs = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM applications")
        applications = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM contacts")
        contacts = cursor.fetchone()["total"]

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "dashboard.html",
        companies=companies,
        jobs=jobs,
        applications=applications,
        contacts=contacts
    )


@app.route("/companies")
def companies():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT *
            FROM companies
            ORDER BY company_id DESC
        """)
        company_list = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "companies.html",
        companies=company_list
    )


@app.route("/companies/add", methods=["POST"])
def add_company():
    company_name = request.form.get("company_name", "").strip()

    if not company_name:
        return "Company name is required.", 400

    values = (
        company_name,
        request.form.get("industry", "").strip(),
        request.form.get("website", "").strip(),
        request.form.get("city", "").strip(),
        request.form.get("state", "").strip()
    )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO companies
            (company_name, industry, website, city, state)
            VALUES (%s, %s, %s, %s, %s)
        """, values)

        connection.commit()

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("companies"))


@app.route("/companies/edit/<int:company_id>")
def edit_company(company_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM companies WHERE company_id = %s",
            (company_id,)
        )
        company = cursor.fetchone()

    finally:
        cursor.close()
        connection.close()

    if company is None:
        abort(404)

    return render_template(
        "edit_company.html",
        company=company
    )


@app.route("/companies/update/<int:company_id>", methods=["POST"])
def update_company(company_id):
    company_name = request.form.get("company_name", "").strip()

    if not company_name:
        return "Company name is required.", 400

    values = (
        company_name,
        request.form.get("industry", "").strip(),
        request.form.get("website", "").strip(),
        request.form.get("city", "").strip(),
        request.form.get("state", "").strip(),
        company_id
    )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE companies
            SET company_name = %s,
                industry = %s,
                website = %s,
                city = %s,
                state = %s
            WHERE company_id = %s
        """, values)

        connection.commit()

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("companies"))


@app.route("/companies/delete/<int:company_id>", methods=["POST"])
def delete_company(company_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM companies WHERE company_id = %s",
            (company_id,)
        )
        connection.commit()

    except mysql.connector.IntegrityError:
        connection.rollback()
        return (
            "Cannot delete a company with related jobs "
            "or contacts. Delete those records first.",
            409
        )

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("companies"))


@app.route("/jobs")
def jobs():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT j.*, c.company_name
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY j.job_id DESC
        """)
        job_list = cursor.fetchall()

        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)
        company_list = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "jobs.html",
        jobs=job_list,
        companies=company_list
    )


@app.route("/jobs/add", methods=["POST"])
def add_job():
    job_title = request.form.get("job_title", "").strip()
    company_id = request.form.get("company_id", type=int)

    if not job_title or not company_id:
        return "Job title and company are required.", 400

    skills = [
        skill.strip()
        for skill in request.form.get("requirements", "").split(",")
        if skill.strip()
    ]

    values = (
        company_id,
        job_title,
        request.form.get("job_type") or None,
        request.form.get("salary_min") or None,
        request.form.get("salary_max") or None,
        request.form.get("job_url") or None,
        request.form.get("date_posted") or None,
        json.dumps(skills)
    )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO jobs
            (company_id, job_title, job_type, salary_min,
             salary_max, job_url, date_posted, requirements)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, values)

        connection.commit()

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("jobs"))


@app.route("/jobs/edit/<int:job_id>")
def edit_job(job_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM jobs WHERE job_id = %s",
            (job_id,)
        )
        job = cursor.fetchone()

        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)
        company_list = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    if job is None:
        abort(404)

    skills = job["requirements"] or []

    if isinstance(skills, str):
        skills = json.loads(skills)

    job["skills_text"] = ", ".join(skills)

    return render_template(
        "edit_job.html",
        job=job,
        companies=company_list
    )


@app.route("/jobs/update/<int:job_id>", methods=["POST"])
def update_job(job_id):
    job_title = request.form.get("job_title", "").strip()
    company_id = request.form.get("company_id", type=int)

    if not job_title or not company_id:
        return "Job title and company are required.", 400

    skills = [
        skill.strip()
        for skill in request.form.get("requirements", "").split(",")
        if skill.strip()
    ]

    values = (
        company_id,
        job_title,
        request.form.get("job_type") or None,
        request.form.get("salary_min") or None,
        request.form.get("salary_max") or None,
        request.form.get("job_url") or None,
        request.form.get("date_posted") or None,
        json.dumps(skills),
        job_id
    )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE jobs
            SET company_id = %s,
                job_title = %s,
                job_type = %s,
                salary_min = %s,
                salary_max = %s,
                job_url = %s,
                date_posted = %s,
                requirements = %s
            WHERE job_id = %s
        """, values)

        connection.commit()

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("jobs"))


@app.route("/jobs/delete/<int:job_id>", methods=["POST"])
def delete_job(job_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM jobs WHERE job_id = %s",
            (job_id,)
        )
        connection.commit()

    except mysql.connector.IntegrityError:
        connection.rollback()
        return "Delete related applications first.", 409

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("jobs"))


@app.route("/applications")
def applications():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT a.*, j.job_title, c.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.job_id
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY a.application_id DESC
        """)
        application_list = cursor.fetchall()

        cursor.execute("""
            SELECT j.job_id, j.job_title, c.company_name
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY c.company_name, j.job_title
        """)
        job_list = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "applications.html",
        applications=application_list,
        jobs=job_list
    )


@app.route("/applications/add", methods=["POST"])
def add_application():
    job_id = request.form.get("job_id", type=int)
    application_date = request.form.get("application_date", "")
    status = request.form.get("status", "Applied")

    valid_statuses = (
        "Applied",
        "Screening",
        "Interview",
        "Offer",
        "Rejected",
        "Withdrawn"
    )

    if not job_id or not application_date or status not in valid_statuses:
        return "Invalid application information.", 400

    try:
        datetime.strptime(application_date, "%Y-%m-%d")
    except ValueError:
        return "Invalid application date.", 400

    interview_data = json.dumps({
        "notes": request.form.get("interview_notes", "").strip()
    })

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO applications
            (job_id, application_date, status,
             resume_version, cover_letter_sent, interview_data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            job_id,
            application_date,
            status,
            request.form.get("resume_version", "").strip(),
            1 if request.form.get("cover_letter_sent") else 0,
            interview_data
        ))

        connection.commit()

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("applications"))


@app.route("/applications/edit/<int:application_id>")
def edit_application(application_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM applications WHERE application_id = %s",
            (application_id,)
        )
        application = cursor.fetchone()

        cursor.execute("""
            SELECT j.job_id, j.job_title, c.company_name
            FROM jobs j
            JOIN companies c ON j.company_id = c.company_id
            ORDER BY c.company_name, j.job_title
        """)
        job_list = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    if application is None:
        abort(404)

    data = application["interview_data"] or {}

    if isinstance(data, str):
        data = json.loads(data)

    application["interview_notes"] = data.get("notes", "")

    if application["application_date"]:
        application["application_date"] = (
            application["application_date"].strftime("%Y-%m-%d")
            if hasattr(application["application_date"], "strftime")
            else str(application["application_date"])
        )

    return render_template(
        "edit_application.html",
        application=application,
        jobs=job_list
    )


@app.route("/applications/update/<int:application_id>", methods=["POST"])
def update_application(application_id):
    job_id = request.form.get("job_id", type=int)
    application_date = request.form.get("application_date", "")
    status = request.form.get("status", "Applied")

    valid_statuses = (
        "Applied",
        "Screening",
        "Interview",
        "Offer",
        "Rejected",
        "Withdrawn"
    )

    if not job_id or not application_date or status not in valid_statuses:
        return "Invalid application information.", 400

    try:
        datetime.strptime(application_date, "%Y-%m-%d")
    except ValueError:
        return "Invalid application date.", 400

    interview_data = json.dumps({
        "notes": request.form.get("interview_notes", "").strip()
    })

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE applications
            SET job_id = %s,
                application_date = %s,
                status = %s,
                resume_version = %s,
                cover_letter_sent = %s,
                interview_data = %s
            WHERE application_id = %s
        """, (
            job_id,
            application_date,
            status,
            request.form.get("resume_version", "").strip(),
            1 if request.form.get("cover_letter_sent") else 0,
            interview_data,
            application_id
        ))

        connection.commit()

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("applications"))


@app.route("/applications/delete/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM applications WHERE application_id = %s",
            (application_id,)
        )
        connection.commit()

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("applications"))


@app.route("/contacts")
def contacts():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT ct.*, c.company_name
            FROM contacts ct
            JOIN companies c ON ct.company_id = c.company_id
            ORDER BY ct.contact_id DESC
        """)
        contact_list = cursor.fetchall()

        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)
        company_list = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "contacts.html",
        contacts=contact_list,
        companies=company_list
    )


@app.route("/contacts/add", methods=["POST"])
def add_contact():
    company_id = request.form.get("company_id", type=int)
    contact_name = request.form.get("contact_name", "").strip()

    if not company_id or not contact_name:
        return "Company and contact name are required.", 400

    if len(contact_name) > 100:
        return "Contact name must be 100 characters or fewer.", 400

    values = (
        company_id,
        contact_name,
        request.form.get("title", "").strip(),
        request.form.get("email", "").strip(),
        request.form.get("phone", "").strip(),
        request.form.get("linkedin_url", "").strip(),
        request.form.get("notes", "").strip()
    )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO contacts
            (company_id, contact_name, title, email,
             phone, linkedin_url, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, values)

        connection.commit()

    except mysql.connector.IntegrityError:
        connection.rollback()
        return "Invalid company selected.", 400

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("contacts"))


@app.route("/contacts/edit/<int:contact_id>")
def edit_contact(contact_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT * FROM contacts WHERE contact_id = %s",
            (contact_id,)
        )
        contact = cursor.fetchone()

        cursor.execute("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)
        company_list = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    if contact is None:
        abort(404)

    return render_template(
        "edit_contact.html",
        contact=contact,
        companies=company_list
    )


@app.route("/contacts/update/<int:contact_id>", methods=["POST"])
def update_contact(contact_id):
    company_id = request.form.get("company_id", type=int)
    contact_name = request.form.get("contact_name", "").strip()

    if not company_id or not contact_name:
        return "Company and contact name are required.", 400

    if len(contact_name) > 100:
        return "Contact name must be 100 characters or fewer.", 400

    values = (
        company_id,
        contact_name,
        request.form.get("title", "").strip(),
        request.form.get("email", "").strip(),
        request.form.get("phone", "").strip(),
        request.form.get("linkedin_url", "").strip(),
        request.form.get("notes", "").strip(),
        contact_id
    )

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE contacts
            SET company_id = %s,
                contact_name = %s,
                title = %s,
                email = %s,
                phone = %s,
                linkedin_url = %s,
                notes = %s
            WHERE contact_id = %s
        """, values)

        connection.commit()

    except mysql.connector.IntegrityError:
        connection.rollback()
        return "Invalid company selected.", 400

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("contacts"))


@app.route("/contacts/delete/<int:contact_id>", methods=["POST"])
def delete_contact(contact_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "DELETE FROM contacts WHERE contact_id = %s",
            (contact_id,)
        )
        connection.commit()

    except mysql.connector.Error:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()

    return redirect(url_for("contacts"))


@app.route("/job-match", methods=["GET", "POST"])
def job_match():
    skills_input = ""
    results = []

    if request.method == "POST":
        skills_input = request.form.get("skills", "").strip()

        user_skills = {
            skill.strip().casefold()
            for skill in skills_input.split(",")
            if skill.strip()
        }

        if not user_skills:
            return "Please enter at least one skill.", 400

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT j.job_id, j.job_title,
                       j.requirements, c.company_name
                FROM jobs j
                JOIN companies c
                    ON j.company_id = c.company_id
                ORDER BY j.job_title
            """)

            job_list = cursor.fetchall()

        finally:
            cursor.close()
            connection.close()

        for job in job_list:
            requirements = job["requirements"] or []

            if isinstance(requirements, str):
                requirements = json.loads(requirements)

            if not isinstance(requirements, list):
                continue

            required_skills = {
                skill.strip().casefold(): skill.strip()
                for skill in requirements
                if isinstance(skill, str) and skill.strip()
            }

            if not required_skills:
                continue

            matching = [
                original
                for normalized, original in required_skills.items()
                if normalized in user_skills
            ]

            missing = [
                original
                for normalized, original in required_skills.items()
                if normalized not in user_skills
            ]

            total = len(required_skills)
            percentage = round((len(matching) / total) * 100)

            results.append({
                "job_title": job["job_title"],
                "company_name": job["company_name"],
                "percentage": percentage,
                "matching": matching,
                "missing": missing,
                "matched_count": len(matching),
                "total_count": total
            })

        results.sort(
            key=lambda job: (
                -job["percentage"],
                job["job_title"].casefold()
            )
        )

    return render_template(
        "job_match.html",
        skills_input=skills_input,
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)
