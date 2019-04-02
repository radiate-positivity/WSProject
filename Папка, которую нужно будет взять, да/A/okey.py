from flask import Flask
from flask_bootstrap import Bootstrap
from flask import render_template, request
from flask import session, make_response
from flask import redirect, jsonify
from flask import request, send_from_directory
from random import choice
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from db import DB
from db import UsersModel
from db import LettersModel
from db import DialogModel


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dialog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'super_secret_key'
app.jinja_env.tests['equalto'] = lambda value, other: value == other


def split(stright, a):
    return stright.split(a)


app.jinja_env.globals.update(split=split)

bootstrap = Bootstrap(app)

db = DB()
LettersModel(db.get_connection()).init_table()
UsersModel(db.get_connection()).init_table()
DialogModel(db.get_connection()).init_table()


class LoginForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Регистрация')


class AddDialogForm(FlaskForm):
    content = TextAreaField('Напишите сообщение', validators=[DataRequired()])
    submit = SubmitField('Отправить')


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    # user_model = UsersModel(db.get_connection())
    # print(user_model.get_all())
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
            return redirect('/dialog')
    return render_template('login.html', title='Вход', form=form, status='Регистрация')


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/index')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        all_users = list(map(lambda x: x[1], user_model.get_all()))
        #print(all_users, user_name)
        if user_name in all_users:
            return redirect('/registration_err')
        user_model.insert(user_name, password)
        exists = user_model.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
            return redirect('/dialog')
    return render_template('login.html', title='Регистрация', form=form, status='Войти')


@app.route('/registration_err', methods=['GET', 'POST'])
def registration_err():
    form = RegistrationForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        all_users = list(map(lambda x: x[1], user_model.get_all()))
        #print(all_users, user_name)
        if user_name in all_users:
            return redirect('/registration_err')
        user_model.insert(user_name, password)
        exists = user_model.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
            return redirect('/dialog')
    return render_template('error.html', title='Регистрация', form=form, status='Войти')

@app.route('/dialog')
def dialog():
    if 'username' not in session:
        return redirect('/index')
    dialogs = DialogModel(db.get_connection()).get_all(session['user_id'])
    um = UsersModel(db.get_connection()).get_all()
    lm = LettersModel(db.get_connection()).get_all()
    return render_template('dialog.html', title='Мои диалоги', username=session['username'], dialogs=dialogs, users=um, letters=lm)


@app.route('/dialog/<int:di_id>', methods=['GET', 'POST'])
def one_dialog(di_id):
    if 'username' not in session:
        return redirect('/index')
    form = AddDialogForm()
    lm = LettersModel(db.get_connection())
    dm = DialogModel(db.get_connection()).get(di_id)
    letters = lm.get_all(di_id)
    if form.validate_on_submit():
        content = [form.content.data]
        #content = form.content.data
        if dm[1] == session['user_id']:
            other = dm[2]
        else:
            other = dm[1]
        lm.insert(content, session['user_id'], other, di_id)
        return redirect('/dialog/{}#end'.format(di_id))
    return render_template('message.html', title='Диалог', form=form, letters=letters, user=session['user_id'])


@app.route('/new_dialog', methods=['GET', 'POST'])
def new_dialog():
    if 'username' not in session:
        return redirect('/index')
    form = AddDialogForm()
    if form.validate_on_submit():
        content = [form.content.data]
        lm = LettersModel(db.get_connection())
        ur = UsersModel(db.get_connection()).get_all()
        dm = DialogModel(db.get_connection())
        n = choice(ur)[0]
        while n == session['user_id']:
            n = choice(ur)[0]
        dm.insert(session['user_id'], n)
        di = dm.get_all(session['user_id'])[-1][0]
        lm.insert(content, session['user_id'], n, di)
        return redirect('/dialog/{}'.format(di))
    return render_template('new_d.html', title='Новый диалог', form=form, username=session['username'])


@app.route('/delete_dialog/<int:di_id>', methods=['GET'])
def delete_dialog(di_id):
    if 'username' not in session:
        return redirect('/index')
    nm = DialogModel(db.get_connection())
    nm.delete(di_id)
    return redirect("/dialog")


@app.route('/delete_me/<int:me_id>', methods=['GET'])
def delete_me(me_id):
    if 'username' not in session:
        return redirect('/index')
    nm = UsersModel(db.get_connection())
    nm.delete(me_id)
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/index')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
