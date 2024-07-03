from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, IntegerField, ValidationError
from wtforms.validators import DataRequired, Optional
from app import db
from app.models import Stdntinfo

#Create list of valid formclasses
formclasses = [s.formclass for s in db.session.query(Stdntinfo.__table__.c.formclass).distinct()]
acceptedord = list(range(65, 123))
acceptedord.append(45)

#Define validators
def only_letters(form, field):
    if field.data:
        for character in field.data:
            if ord(character) not in acceptedord:
                raise ValidationError('Field must contain only one name (hyphented names are allowed)')

def valid_formclass(form, field):
    if field.data: 
        if field.data.upper() not in formclasses:
            raise ValidationError('Not a valid formclass')

#Define forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class SearchForm(FlaskForm):
    style = {'style': 'width:20vw;'}
    firstname = StringField('Firstname', validators=[only_letters], render_kw={"placeholder": "FIRSTNAME"})
    surname = StringField('Surname', validators=[only_letters], render_kw={"placeholder": "SURNAME"})
    studentid = IntegerField('Student Id', validators=[Optional()], render_kw={"placeholder": "STUDENT ID"})
    formclass = StringField('Form Class', validators=[valid_formclass], render_kw={"placeholder": "FORMCLASS"})
    submit = SubmitField('Search')

#class SelectEvent(FlaskForm):
#    select = BooleanField(default='checked', widget=widgets.HiddenInput())
#    stdntid = HiddenField()
#    eventid = HiddenField()
#    submit = SubmitField()