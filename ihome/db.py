from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask import current_app
import click

engine = create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'], )
db_session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine
))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    """ mysql数据库初始化， 根据模型创建表格 """
    from ihome import models
    Base.metadata.create_all(bind=engine)


def shutdown_session(exception=None):
    """ 关闭数据库session """
    db_session.remove()


@click.command('init-db')
def init_db_command():
    """ 为数据库初始化添加命令行命令 """
    init_db()
    click.echo('Intialized mysql database!')


def init_app(app):
    app.teardown_appcontext(shutdown_session)
    app.cli.add_command(init_db_command)
