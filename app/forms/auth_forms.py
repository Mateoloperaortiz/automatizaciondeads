from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models.user import UserRole

class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """Form for user registration."""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=8, max=128, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

class ProfileForm(FlaskForm):
    """Form for editing user profile."""
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField('Update Profile')

class PasswordChangeForm(FlaskForm):
    """Form for changing password."""
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[
        DataRequired(), 
        Length(min=8, max=128, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(), 
        EqualTo('new_password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')

class UserEditForm(FlaskForm):
    """Form for admin to edit users."""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    role = SelectField('Role', choices=[
        (UserRole.ADMIN.value, 'Admin'),
        (UserRole.MANAGER.value, 'Manager'),
        (UserRole.ANALYST.value, 'Analyst'),
        (UserRole.VIEWER.value, 'Viewer')
    ])
    is_active = BooleanField('Active')
    password = PasswordField('New Password (leave blank to keep current)', validators=[
        Length(min=0, max=128),
        # If password is provided, it must be at least 8 characters
        # Use this custom validator to allow empty password (for unchanged)
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Update User')
    
    def validate_password(self, field):
        """Custom validator for password field."""
        if field.data and len(field.data) < 8:
            raise ValidationError('Password must be at least 8 characters long')