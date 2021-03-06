"""Hackbright Project Tracker.

A front-end for a database that allows users to work with students, class
projects, and the grades students receive in class projects.
"""
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///hackbright'
    db.app = app
    db.init_app(app)


def get_student_by_github(github):
    """Given a github account name, print information about the matching student."""

    QUERY = """
        SELECT first_name, last_name, github
        FROM Students
        WHERE github = :github
        """
    db_cursor = db.session.execute(QUERY, {'github': github})
    row = db_cursor.fetchone()
    print "Student: %s %s\nGithub account: %s" % (row[0], row[1], row[2])


def make_new_student(first_name, last_name, github):
    """Add a new student and print confirmation.

    Given a first name, last name, and GitHub account, add student to the
    database and print a confirmation message.
    """
    QUERY = """INSERT INTO Students VALUES (:first_name, :last_name, :github)"""
    db_cursor = db.session.execute(QUERY, {'first_name': first_name, 'last_name': last_name, 'github': github})
    db.session.commit()

    print "Successfully added student: %s %s" % (first_name, last_name)


def get_project_by_title(title):
    """Given a project title, print information about the project."""
    QUERY = """SELECT * FROM projects WHERE title = :title """
    db_cursor = db.session.execute(QUERY, {'title': title})
    matching_projects = db_cursor.fetchall()
    for row in matching_projects:
        print "Project %s: ID is %i; Description: %s; Max Possible Grade is %i."% (row[1], row[0], row[2], row[3])


def get_grade_by_github_title(user_entered_github, user_entered_title):
    """Print grade student received for a project."""
    QUERY = """SELECT grade 
    FROM grades 
    WHERE student_github = :github AND
    project_title = :title"""

    db_cursor = db.session.execute(QUERY, {'github': user_entered_github, 'title': user_entered_title})
    row = db_cursor.fetchone()
    print "The grade for that project is: %i" % (row[0])

# def assign_grade(github, title, grade):                       #assuming project grade does not exist
#     """Assign a student a grade on an assignment and print a confirmation."""
#     QUERY = """ INSERT INTO grades (student_github, project_title, grade) 
#                 VALUES (:github, :title, :grade) """
#     db_cursor = db.session.execute(QUERY, {'github': github, 'title': title, 'grade': int(grade)})
#     db.session.commit()

#     print "Successfully added grade for %s: %s earned %i" % (title, github, int(grade))

def assign_grade(github, title, grade):
    """Assign a student a grade on an assignment that has a prior grade and print a confirmation."""
    QUERY = """UPDATE grades 
                SET grade = :grade
                WHERE student_github = :github AND project_title = :title"""
    db_cursor = db.session.execute(QUERY, {'grade': int(grade), 'title': title, 'github': github})
    db.session.commit()

    print "Successfully updated grade for %s: %s now has grade %i" % (title, github, int(grade))

def add_project(title, description, max_grade):
    """Add a project, including the project title, description, and maximum grade."""
    QUERY = """ INSERT INTO projects (title, description, max_grade) 
                VALUES (:title, :description, :max_grade) """

    desc_string = " ".join(description)

    db_cursor = db.session.execute(QUERY, {'title': title, 'description': desc_string, 'max_grade': int(max_grade)})
    db.session.commit()

    print "Successfully added project %s with description %s and maximum grade %i" % (title, desc_string, int(max_grade))


def handle_input():
    """Main loop.

    Repeatedly prompt for commands, performing them, until 'quit' is received as a
    command."""

    command = None

    while command != "quit":
        input_string = raw_input("HBA Database> ")
        tokens = input_string.split()
        command = tokens[0]
        args = tokens[1:]

        if command == "student":
            github = args[0]
            get_student_by_github(github)

        elif command == "new_student":
            first_name, last_name, github = args   # unpack!
            make_new_student(first_name, last_name, github)

        elif command == "project_info":
            title = args[0]
            get_project_by_title(title)

        elif command == "grade_info":
            user_entered_github, user_entered_title = args
            get_grade_by_github_title(user_entered_github, user_entered_title)

        elif command == "set_grade":
            github, title, grade = args
            assign_grade(github, title, grade)

        elif command == "new_project":
            title = args[0]
            max_grade = args[-1]
            description = args[1:-1]
            add_project(title, description, max_grade)

        else:
            if command != "quit":
                print "Invalid Entry. Try again."


if __name__ == "__main__":
    app = Flask(__name__)
    connect_to_db(app)

    handle_input()

    db.session.close()
