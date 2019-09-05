from app import create_app, db
from app.models import User, Post  #импортирует переменную app ('экземпляр класса App), входящую в пакет app.

app = create_app()


@app.shell_context_processor #создает контекст оболочки, который добавляет экземпляр и модели базы данных в сеанс оболочки
def make_shell_context():
    return {'db': db, 'User': User, 'Post': Post}