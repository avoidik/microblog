from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, InputRequired, Length, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField(_l("Username"), validators=[
        InputRequired(message=_l("Username required")),
        Length(min=3, max=32, message=_l("Username length between 3 and 32"))
    ])
    about_me = TextAreaField(_l("About me"), validators=[
        Length(min=0, max=140)
    ])
    submit = SubmitField(_l("Submit"))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_("Such username is taken %(username)s!", username=username.data))

class PostForm(FlaskForm):
    post = TextAreaField(_l("Post"), validators=[
        InputRequired(message=_l("Post text required")),
        Length(min=5, max=140, message=_l("Post text length betweetn 5 and 140"))
    ])
    submit = SubmitField(_l("Submit"))
