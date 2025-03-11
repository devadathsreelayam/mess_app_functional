from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user
from functools import wraps

db = SQLAlchemy()
DB_NAME = 'mess_app_db'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'my app secret key'

    # SQLAlchemy Configuration (using PyMySQL as the driver)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:root@localhost/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'path/to/profile_pictures'

    db.init_app(app)

    from .views import views
    from .auth import auth
    from .inmates import inmates
    from .summaries import summaries

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(inmates, url_prefix='/')
    app.register_blueprint(summaries, url_prefix='/')

    from .models import Inmate, User, MessStatus, MealsLog, GuestLog, MonthlyBillInfo, Expense, Bill

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(id)

    return app


def role_required(*roles):
    """Decorator to restrict access to users with specific roles."""
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                abort(403)  # Forbidden access
            return func(*args, **kwargs)
        return wrapper
    return decorator