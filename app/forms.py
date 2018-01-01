from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, InputRequired, Length, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[
        InputRequired(message="Username can not be empty"),
        Length(min=3, max=32, message="Username length between 3 and 32")
    ])
    password = PasswordField("Password", validators=[
        InputRequired(message="Password can not be empty"),
        Length(min=3, max=32, message="Password length between 3 and 32")
    ])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[
        InputRequired(message="Username required"),
        Length(min=3, max=32, message="Username length between 3 and 32")
    ])
    email = StringField("Email", validators=[
        InputRequired(message="Email required"),
        Length(min=3, max=64, message="Email length between 3 and 64"),
        Email(message="Email is invalid")
    ])
    password = PasswordField("Password", validators=[
        InputRequired(message="Password required"),
        Length(min=3, max=64, message="Password length between 3 and 64")
    ])
    password2 = PasswordField("Repeat password", validators=[
        InputRequired(message="Password repeat required"),
        Length(min=3, max=64, message="Password repeat length between 3 and 64"),
        EqualTo("password", message="Passwords doesn't match")
    ])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username already exist")

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError("Email already taken")

class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[
        InputRequired(message="Username required"),
        Length(min=3, max=32, message="Username length between 3 and 32")
    ])
    about_me = TextAreaField("About me", validators=[
        Length(min=0, max=140)
    ])
    submit = SubmitField("Submit")

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError("Such username is taken {} {}!".format(self.username.data, username.data))
