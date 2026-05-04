from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class ContactForm(FlaskForm):
    name = StringField('Имя / Ник', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    team = SelectField('Любимая команда', choices=[
        ('ferrari', 'Scuderia Ferrari'),
        ('mclaren', 'McLaren'),
        ('redbull', 'Red Bull Racing'),
        ('mercedes', 'Mercedes AMG'),
        ('aston', 'Aston Martin'),
        ('williams', 'Williams'),
        ('haas', 'Haas'),
        ('alpine', 'Alpine'),
        ('audi', 'Audi'),
        ('cadillac', 'Cadillac'),
        ('other', 'Другая')
    ])
    message = TextAreaField('Сообщение', validators=[Length(max=500)])

class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    confirm = PasswordField('Подтвердите пароль', validators=[DataRequired(), EqualTo('password')])
    team = SelectField('Любимая команда', choices=[
        ('ferrari', 'Scuderia Ferrari'),
        ('mclaren', 'McLaren'),
        ('redbull', 'Red Bull Racing'),
        ('mercedes', 'Mercedes AMG'),
        ('aston', 'Aston Martin'),
        ('williams', 'Williams'),
        ('haas', 'Haas'),
        ('alpine', 'Alpine'),
        ('audi', 'Audi'),
        ('cadillac', 'Cadillac'),
        ('other', 'Другая')
    ])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить')