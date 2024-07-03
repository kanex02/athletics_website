from flask import render_template, flash, redirect, request, url_for, session
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as db
from app import app
from app import db as _db
from app.forms import LoginForm, SearchForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import Admin, Stdntinfo, Events, stdntevents
from werkzeug.urls import url_parse
from math import ceil
from datetime import timedelta


# Define the update function, which refreshes the filter data in the cookie
# def update():
#    print('START UPDATE')
#    print(admin.form.data)
#    for attr in ['firstname', 'surname', 'formclass', 'studentid']:
#        if admin.form.data[attr] not in [' ', None]:
#            print(admin.form.data[attr])
#            dat = admin.form.data
#            session['formdata'] = dat
#            break


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)


# Route for login
@app.route('/', methods=['GET', 'POST'])
def home():
    # Redirect to admin page if user is logged in
    if current_user.is_authenticated:
        return redirect(url_for('admin'))
    form = LoginForm()
    # Deal with form data
    if form.validate_on_submit():
        # print(Admin.query.all())
        user = Admin.query.filter(Admin.username.ilike(form.username.data)).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('home'))
        login_user(user)
        # Check if user is trying to redirect to an external page, and refresh if they are
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != ' ':
            next_page = url_for('home')
        return redirect(url_for('admin'))
    return render_template('home.html', form=form)


# Route for logging students in and out
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    students = Stdntinfo.query.order_by(Stdntinfo.surname)
    events = Events.query.all()
    form = SearchForm()
    # If the current page is stored in session and the user is not requesting a new page, get the page from the cookie
    if 'currpage' in session and session['currpage'] and not request.args.get('page'):
        page = session['currpage']
    else:
        page = request.args.get('page', 1, type=int)

    # If the form is valid and no empty, apply the filters
    if form.data and form.validate_on_submit():
        # print('SEARCHING')
        formdata = form.data
        students = _db.session.query(Stdntinfo).filter(Stdntinfo.firstname.like('%{}%'.format(form.firstname.data)))

        # Check if form is empty again, thoroughly
        for fielddat in [form.firstname.data, form.surname.data, form.studentid.data, form.formclass.data]:
            if fielddat not in ['', None]:
                page = 0
                break

        # Filter students
        if form.surname.data != '':
            students = students.filter(Stdntinfo.surname.like('%{}%'.format(form.surname.data)))
        if form.studentid.data is not None:
            students = students.filter(Stdntinfo.studentid.like('%{}%'.format(form.studentid.data)))
        if form.formclass.data != '':
            students = students.filter(Stdntinfo.formclass.like('%{}%'.format(form.formclass.data)))

        # If empty, clear filters
        if students.count() == 0:
            flash('Query returned no students')
            # print('loop')
            return redirect(url_for('admin'))


    # Check if there is saved cookie data
    elif 'formdata' in session:
        # print('Retrieving form data from cookies')
        formdata = session['formdata']
        form.firstname.data = formdata['firstname']
        form.surname.data = formdata['surname']
        form.studentid.data = formdata['studentid']
        form.formclass.data = formdata['formclass']

        # Filter by saved search
        for attr in ['firstname', 'surname', 'formclass', 'studentid']:
            if formdata[attr] not in [' ', None]:
                # print('FILTERING')
                # print(formdata[attr])
                if form.firstname.data != '':
                    students = _db.session.query(Stdntinfo).filter(
                        Stdntinfo.firstname.like('%{}%'.format(formdata['firstname'])))
                if form.surname.data != '':
                    students = students.filter(Stdntinfo.surname.like('%{}%'.format(formdata['surname'])))
                if form.studentid.data is not None:
                    students = students.filter(Stdntinfo.studentid.like('%{}%'.format(formdata['studentid'])))
                if form.formclass.data != '' and form.formclass.data is not None:
                    students = students.filter(Stdntinfo.formclass.like('%{}%'.format(formdata['formclass'])))

                if students.count() == 0:
                    flash('Query returned no students')
                    session.pop('formdata')
                    return redirect(url_for('admin'))

                break

    # If no filters, query all students
    else:
        students = Stdntinfo.query.order_by(Stdntinfo.surname)

    try:
        # print('UPDATE COOKIES')
        # print(formdata)
        for attr in ['firstname', 'surname', 'formclass', 'studentid']:
            if attr in formdata and formdata[attr] not in [' ', None]:
                session['formdata'] = dict(formdata)
                break
    except UnboundLocalError:
        pass

    # Order and paginate data before rendering
    pagecount = int(ceil(students.count() / app.config['RESULTS_PER_PAGE']))
    session['currpage'] = page
    students = students.order_by(Stdntinfo.surname)
    students = students.paginate(page, app.config['RESULTS_PER_PAGE'], False)
    studentgrades = []
    for student in students.items:
        studentgrades.extend([grade for grade in student.grade.split('#') if grade not in studentgrades])
    eventgrades = []
    for event in events:
        eventgrades.extend([e.grade for e in event.grades if e.grade not in eventgrades])
    events = [event for event in events if [grade.grade for grade in event.grades if grade.grade in studentgrades]]
    currpage = students.page
    if 'collapsed' in session:
        collapsed = session['collapsed']
    else:
        collapsed = False
    session['collapsed'] = False
    return render_template('admin.html', data=students.items, events=events, form=form, pages=pagecount,
                           currpage=currpage, collapsed=collapsed)


# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home'))


# Login
@app.route('/login')
def login():
    return redirect(url_for('home'))


# Enter student in event
@app.route('/enter', methods=['GET', 'POST'])
@login_required
def enter():
    stdntid = int(request.form['stdntid'])
    eventid = int(request.form['eventid'])
    student = Stdntinfo.query.filter(Stdntinfo.id == stdntid).first()
    event = Events.query.filter(Events.id == eventid).first()

    if event not in student.events:
        student.events.append(event)

        # Save filter to session
        _db.session.add(student)
        _db.session.commit()
        # update()
        # print('ENTER')
    session['collapsed'] = True
    return redirect(url_for('admin'))


# Remove student from event
@app.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    stdntid = int(request.form['stdntid'])
    eventid = int(request.form['eventid'])
    student = Stdntinfo.query.filter(Stdntinfo.id == stdntid).first()
    event = Events.query.filter(Events.id == eventid).first()

    if event in student.events:
        student.events.remove(event)

        # Save filter to session
        _db.session.add(student)
        _db.session.commit()
        # update()
        # print('DELETE')

    session['collapsed'] = True
    return redirect(url_for('admin'))


# Clear search
@app.route('/clearsearch', methods=['GET', 'POST'])
@login_required
def clear():
    # TODO: Figure out why the code doesn't work without the print statements below
    print('random message 1')
    print('random message 2')
    print('random message 3')
    if 'formdata' in session:
        session.pop('formdata')
    if 'currpage' in session:
        session.pop('currpage')
    return redirect(url_for('admin'))


# 404
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('admin'))


# Define the function to check if a student can enter an event
@app.context_processor
def utility_processor():
    def check_available(event, student):
        if [e for e in event.grades if e.grade in student.grade.split('#')]:
            return True
        else:
            return False

    return dict(check_available=check_available)


if __name__ == '__main__':
    app.run(debug=True, port=8080)
