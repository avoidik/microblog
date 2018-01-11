from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, InputRequired, Length, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User

class LoginForm(FlaskForm):
    username = StringField(_l("Username"), validators=[
        InputRequired(message=_l("Username can not be empty")),
        Length(min=3, max=32, message=_l("Username length between 3 and 32"))
    ])
    password = PasswordField(_l("Password"), validators=[
        InputRequired(message=_l("Password can not be empty")),
        Length(min=3, max=32, message=_l("Password length between 3 and 32"))
    ])
    remember_me = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l("Sign In"))

class RegistrationForm(FlaskForm):
    username = StringField(_l("Username"), validators=[
        InputRequired(message=_l("Username required")),
        Length(min=3, max=32, message=_("Username length between 3 and 32"))
    ])
    email = StringField(_l("Email"), validators=[
        InputRequired(message=_l("Email required")),
        Length(min=3, max=64, message=_l("Email length between 3 and 64")),
        Email(message=_l("Email is invalid"))
    ])
    password = PasswordField(_l("Password"), validators=[
        InputRequired(message=_l("Password required")),
        Length(min=3, max=64, message=_l("Password length between 3 and 64"))
    ])
    password2 = PasswordField(_l("Repeat password"), validators=[
        InputRequired(message=_l("Password repeat required")),
        Length(min=3, max=64, message=_l("Password repeat length between 3 and 64")),
        EqualTo("password", message=_l("Passwords doesn't match"))
    ])
    submit = SubmitField(_l("Register"))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_("Username already exist"))

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data).first()
        if email is not None:
            raise ValidationError(_("Email already taken"))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l("Email"), validators=[
        InputRequired(message=_l("Email required")),
        Length(min=3, max=64, message=_l("Email length between 3 and 64")),
        Email(message=_l("Email is invalid"))
    ])
    submit = SubmitField(_l("Reset"))

class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l("Password"), validators=[
        InputRequired(message=_l("Password required")),
        Length(min=3, max=64, message=_l("Password length between 3 and 64"))
    ])
    password2 = PasswordField(_l("Repeat password"), validators=[
        InputRequired(message=_l("Password repeat required")),
        Length(min=3, max=64, message=_l("Password repeat length between 3 and 64")),
        EqualTo("password", message=_l("Passwords doesn't match"))
    ])
    submit = SubmitField(_l("Submit"))
