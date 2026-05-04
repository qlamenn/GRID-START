import os
import json
import requests
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from config import Config
from models import db, User, Message, Reaction
from forms import ContactForm, RegisterForm, LoginForm
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid
from PIL import Image

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    with open('data/news.json', 'r', encoding='utf-8') as f:
        news = json.load(f)

    for i, item in enumerate(news):
        likes = Reaction.query.filter_by(news_id=i, action='like').count()
        dislikes = Reaction.query.filter_by(news_id=i, action='dislike').count()
        item['likes'] = likes
        item['dislikes'] = dislikes
        item['id'] = i
        if current_user.is_authenticated:
            user_react = Reaction.query.filter_by(user_id=current_user.id, news_id=i).first()
            item['user_action'] = user_react.action if user_react else None
        else:
            item['user_action'] = None

    driver_names = {
        1: 'Норрис', 81: 'Пиастри', 63: 'Расселл', 12: 'Антонелли',
        3: 'Ферстаппен', 6: 'Хаджар', 16: 'Леклер', 44: 'Хэмилтон',
        23: 'Албон', 55: 'Сайнс', 41: 'Линдблад', 30: 'Лоусон',
        18: 'Стролл', 14: 'Алонсо', 31: 'Окон', 87: 'Берман',
        27: 'Хюлкенберг', 5: 'Бортолето', 10: 'Гасли', 43: 'Колапинто',
        11: 'Перес', 77: 'Боттас'
    }

    drivers = []
    constructors = []
    try:
        sessions_resp = requests.get('https://api.openf1.org/v1/sessions?year=2026&session_name=Race', timeout=10)
        if sessions_resp.status_code == 200:
            sessions = sessions_resp.json()
            done = [s for s in sessions if s['date_end'] < '2026-05-04T00:00:00']
            if done:
                session_key = done[-1]['session_key']

                dr_resp = requests.get(f'https://api.openf1.org/v1/championship_drivers?session_key={session_key}',
                                       timeout=10)
                if dr_resp.status_code == 200:
                    drivers = sorted(dr_resp.json(), key=lambda x: x['position_current'])
                    for d in drivers:
                        d['name'] = driver_names.get(d['driver_number'], str(d['driver_number']))

                tm_resp = requests.get(f'https://api.openf1.org/v1/championship_teams?session_key={session_key}',
                                       timeout=10)
                if tm_resp.status_code == 200:
                    constructors = sorted(tm_resp.json(), key=lambda x: x['position_current'])
    except:
        pass

    return render_template('index.html', news=news, drivers=drivers, constructors=constructors)


@app.route('/races')
def races():
    meetings = []
    error = None
    try:
        resp = requests.get('https://api.openf1.org/v1/meetings?year=2026', timeout=10)
        if resp.status_code == 200:
            meetings = resp.json()
            meetings.sort(key=lambda x: x['date_start'])
        else:
            error = 'API недоступен'
    except:
        error = 'Не удалось загрузить данные'

    return render_template('races.html', meetings=meetings, error=error, now=datetime.utcnow().isoformat())

@app.route('/drivers')
def drivers():
    drivers_data = [
        {'name': 'Ландо Норрис', 'number': '1', 'team': 'McLaren', 'country': 'Великобритания', 'born': '13.11.1999', 'image': 'norris.jpg'},
        {'name': 'Оскар Пиастри', 'number': '81', 'team': 'McLaren', 'country': 'Австралия', 'born': '06.04.2001', 'image': 'piastri.jpg'},
        {'name': 'Джордж Расселл', 'number': '63', 'team': 'Mercedes', 'country': 'Великобритания', 'born': '15.02.1998', 'image': 'russell.jpg'},
        {'name': 'Андреа Кими Антонелли', 'number': '12', 'team': 'Mercedes', 'country': 'Италия', 'born': '25.08.2006', 'image': 'antonelli.jpg'},
        {'name': 'Макс Ферстаппен', 'number': '3', 'team': 'Red Bull', 'country': 'Нидерланды', 'born': '30.09.1997', 'image': 'verstappen.jpg'},
        {'name': 'Айзек Хаджар', 'number': '6', 'team': 'Red Bull', 'country': 'Франция', 'born': '28.09.2004', 'image': 'hadjar.jpg'},
        {'name': 'Шарль Леклер', 'number': '16', 'team': 'Ferrari', 'country': 'Монако', 'born': '16.10.1997', 'image': 'leclerc.jpg'},
        {'name': 'Льюис Хэмилтон', 'number': '44', 'team': 'Ferrari', 'country': 'Великобритания', 'born': '07.01.1985', 'image': 'hamilton.jpg'},
        {'name': 'Алекс Элбон', 'number': '23', 'team': 'Williams', 'country': 'Таиланд', 'born': '23.03.1996', 'image': 'albon.jpg'},
        {'name': 'Карлос Сайнс', 'number': '55', 'team': 'Williams', 'country': 'Испания', 'born': '01.09.1994', 'image': 'sainz.jpg'},
        {'name': 'Арвид Линдблад', 'number': '41', 'team': 'Racing Bulls', 'country': 'Великобритания', 'born': '08.08.2007', 'image': 'lindblad.jpg'},
        {'name': 'Лиам Лоусон', 'number': '30', 'team': 'Racing Bulls', 'country': 'Новая Зеландия', 'born': '11.02.2002', 'image': 'lawson.jpg'},
        {'name': 'Лэнс Стролл', 'number': '18', 'team': 'Aston Martin', 'country': 'Канада', 'born': '29.10.1998', 'image': 'stroll.jpg'},
        {'name': 'Фернандо Алонсо', 'number': '14', 'team': 'Aston Martin', 'country': 'Испания', 'born': '29.07.1981', 'image': 'alonso.jpg'},
        {'name': 'Эстебан Окон', 'number': '31', 'team': 'Haas', 'country': 'Франция', 'born': '17.09.1996', 'image': 'ocon.jpg'},
        {'name': 'Оливер Берман', 'number': '87', 'team': 'Haas', 'country': 'Великобритания', 'born': '08.05.2005', 'image': 'bearman.jpg'},
        {'name': 'Нико Хюлкенберг', 'number': '27', 'team': 'Audi', 'country': 'Германия', 'born': '19.08.1987', 'image': 'hulkenberg.jpg'},
        {'name': 'Габриэль Бортолето', 'number': '5', 'team': 'Audi', 'country': 'Бразилия', 'born': '14.10.2004', 'image': 'bortoleto.jpg'},
        {'name': 'Пьер Гасли', 'number': '10', 'team': 'Alpine', 'country': 'Франция', 'born': '07.02.1996', 'image': 'gasly.jpg'},
        {'name': 'Франко Колапинто', 'number': '43', 'team': 'Alpine', 'country': 'Аргентина', 'born': '27.05.2003', 'image': 'colapinto.jpg'},
        {'name': 'Серхио Перес', 'number': '11', 'team': 'Cadillac', 'country': 'Мексика', 'born': '26.01.1990', 'image': 'perez.jpg'},
        {'name': 'Валттери Боттас', 'number': '77', 'team': 'Cadillac', 'country': 'Финляндия', 'born': '28.08.1989', 'image': 'bottas.jpg'},
    ]
    return render_template('drivers.html', drivers=drivers_data)


@app.route('/circuits')
def circuits():
    lengths = {
        'Melbourne': 5.278, 'Shanghai': 5.451, 'Suzuka': 5.807, 'Miami': 5.412,
        'Montreal': 4.361, 'Monte Carlo': 3.337, 'Barcelona': 4.657, 'Spielberg': 4.318,
        'Silverstone': 5.891, 'Spa-Francorchamps': 7.004, 'Hungaroring': 4.381, 'Zandvoort': 4.259,
        'Monza': 5.793, 'Madring': 5.474, 'Baku': 6.003, 'Singapore': 4.94,
        'Austin': 5.513, 'Mexico City': 4.304, 'Interlagos': 4.309, 'Las Vegas': 6.201,
        'Lusail': 5.419, 'Yas Marina Circuit': 5.281, 'Jeddah': 6.174, 'Sakhir': 5.412
    }

    circuits = {}
    error = None
    try:
        resp = requests.get('https://api.openf1.org/v1/meetings?year=2026', timeout=10)
        if resp.status_code == 200:
            meetings = resp.json()
            for m in meetings:
                key = m['circuit_short_name']
                if key not in circuits:
                    circuits[key] = {
                        'name': m['circuit_short_name'],
                        'country': m['country_name'],
                        'location': m['location'],
                        'type': m['circuit_type'],
                        'image': m.get('circuit_image', ''),
                        'length': lengths.get(m['circuit_short_name'], '—')
                    }
        else:
            error = 'API недоступен'
    except:
        error = 'Не удалось загрузить данные'

    return render_template('circuits.html', circuits=circuits.values(), error=error)

@app.route('/teams')
def teams():
    teams_data = [
        {
            'name': 'Mercedes AMG F1',
            'engine': 'Mercedes',
            'base': 'Брэкли, Великобритания',
            'drivers': 'Расселл, Антонелли',
            'country': 'Германия',
            'image': 'mersedes.jpg'
        },
        {
            'name': 'Scuderia Ferrari',
            'engine': 'Ferrari',
            'base': 'Маранелло, Италия',
            'drivers': 'Леклер, Хэмилтон',
            'country': 'Италия',
            'image': 'ferrari.jpg'
        },
        {
            'name': 'McLaren',
            'engine': 'Mercedes',
            'base': 'Уокинг, Великобритания',
            'drivers': 'Норрис, Пиастри',
            'country': 'Великобритания',
            'image': 'mclaren.jpg'
        },
        {
            'name': 'Haas',
            'engine': 'Ferrari',
            'base': 'Каннаполис, США',
            'drivers': 'Берман, Окон',
            'country': 'США',
            'image': 'haas.jpg'
        },
        {
            'name': 'Alpine',
            'engine': 'Mercedes',
            'base': 'Энстоун, Великобритания',
            'drivers': 'Гасли, Колапинто',
            'country': 'Франция',
            'image': 'alpine.jpg'
        },
        {
            'name': 'Red Bull Racing',
            'engine': 'Ford',
            'base': 'Милтон-Кинс, Великобритания',
            'drivers': 'Ферстаппен, Хаджар',
            'country': 'Австрия',
            'image': 'redbull.jpg'
        },
        {
            'name': 'Racing Bulls',
            'engine': 'Honda RBPT',
            'base': 'Фаэнца, Италия',
            'drivers': 'Линблад, Лоусон',
            'country': 'Италия',
            'image': 'racingbulls.jpg'
        },
        {
            'name': 'Audi',
            'engine': 'Audi',
            'base': 'Хинвиль, Швейцария',
            'drivers': 'Хюлькенберг, Борталлето',
            'country': 'Германия',
            'image': 'audi.jpg'
        },
        {
            'name': 'Williams',
            'engine': 'Mercedes',
            'base': 'Гроув, Великобритания',
            'drivers': 'Сайнс, Албон',
            'country': 'Великобритания',
            'image': 'williams.jpg'
        },
        {
            'name': 'Cadillac',
            'engine': 'Ferrari',
            'base': 'США',
            'drivers': 'Перес, Боттас',
            'country': 'США',
            'image': 'cadillac.jpg'
        }
    ]
    return render_template('teams.html', teams=teams_data)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(
            name=form.name.data,
            email=form.email.data,
            team=form.team.data,
            text=form.message.data
        )
        if current_user.is_authenticated:
            msg.user_id = current_user.id
        db.session.add(msg)
        db.session.commit()
        flash('Сообщение отправлено!', 'success')
        return redirect(url_for('contact'))
    return render_template('form.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed,
            team=form.team.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Вы вошли в систему!', 'success')
            return redirect(url_for('index'))
        flash('Неверный email или пароль', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile')
@login_required
def profile():
    messages = Message.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user=current_user, messages=messages)


@app.route('/react/<int:news_id>/<action>')
@login_required
def react(news_id, action):
    if action not in ['like', 'dislike']:
        return {'error': 'invalid action'}, 400

    existing = Reaction.query.filter_by(user_id=current_user.id, news_id=news_id).first()
    if existing:
        if existing.action == action:
            db.session.delete(existing)
        else:
            existing.action = action
    else:
        r = Reaction(user_id=current_user.id, news_id=news_id, action=action)
        db.session.add(r)

    db.session.commit()

    likes = Reaction.query.filter_by(news_id=news_id, action='like').count()
    dislikes = Reaction.query.filter_by(news_id=news_id, action='dislike').count()

    user_action = None
    if current_user.is_authenticated:
        user_react = Reaction.query.filter_by(user_id=current_user.id, news_id=news_id).first()
        if user_react:
            user_action = user_react.action

    return {'likes': likes, 'dislikes': dislikes, 'user_action': user_action}


@app.route('/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('Файл не выбран', 'danger')
        return redirect(url_for('profile'))
    file = request.files['avatar']
    if file.filename == '':
        flash('Файл не выбран', 'danger')
        return redirect(url_for('profile'))
    if file:
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'gif']:
            flash('Разрешены только JPG, PNG, GIF', 'danger')
            return redirect(url_for('profile'))
        filename = str(uuid.uuid4()) + '.jpg'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        img = Image.open(file)
        img = img.convert('RGB')
        img = img.resize((300, 300), Image.Resampling.LANCZOS)
        img.save(filepath, 'JPEG', quality=85)

        current_user.avatar = filename
        db.session.commit()
        flash('Аватар обновлён!', 'success')
    return redirect(url_for('profile'))

@app.route('/reset')
def reset():
    db.drop_all()
    db.create_all()
    return 'ok'

@app.route('/profile/password', methods=['POST'])
@login_required
def change_password():
    old = request.form.get('old_password')
    new = request.form.get('new_password')
    confirm = request.form.get('confirm_password')

    if not bcrypt.check_password_hash(current_user.password, old):
        flash('Неверный текущий пароль', 'danger')
    elif new != confirm:
        flash('Новые пароли не совпадают', 'danger')
    elif len(new) < 6:
        flash('Пароль минимум 6 символов', 'danger')
    else:
        current_user.password = bcrypt.generate_password_hash(new).decode('utf-8')
        db.session.commit()
        flash('Пароль изменён!', 'success')

    return redirect(url_for('profile'))

@app.route('/api/news')
def api_news():
    with open('data/news.json', 'r', encoding='utf-8') as f:
        news = json.load(f)
    return news

@app.route('/api/standings')
def api_standings():
    with open('data/standings.json', 'r', encoding='utf-8') as f:
        standings = json.load(f)
    return standings

@app.route('/api/calendar')
def api_calendar():
    with open('data/calendar.json', 'r', encoding='utf-8') as f:
        calendar = json.load(f)
    return calendar

@app.route('/api/races')
def api_races():
    try:
        resp = requests.get('https://api.openf1.org/v1/meetings?year=2026', timeout=10)
        return resp.json()
    except:
        return {'error': 'API unavailable'}, 500


if __name__ == '__main__':
    app.run(debug=True)