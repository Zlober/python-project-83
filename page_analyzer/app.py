import socket

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    get_flashed_messages,
    url_for
)
import psycopg2
import os
from dotenv import load_dotenv, find_dotenv
import datetime
from urllib.parse import urlparse
import validators
import requests
from bs4 import BeautifulSoup


load_dotenv(find_dotenv())
DATABASE_URL = os.getenv('DATABASE_URL')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.post('/urls')
def post_urls():
    url = request.form.get('url')
    if not validators.url(url):
        flash('Некорректный URL', 'error')
        if len(url) == 0:
            flash('URL обязателен', 'error')
        if len(url) > 255:
            flash('URL превышает 255 символов', 'error')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', messages=messages), 422
    url = urlparse(url)
    url = f'{url.scheme}://{url.netloc}'
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT id FROM urls WHERE name=%s", (url,))
            id = curs.fetchone()
    if id:
        flash('Страница уже существует', 'warning')
        return redirect(url_for('get_url_id', id=id[0]))
    flash('Страница успешно добавлена', category='success')
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("""
                INSERT INTO urls (name, created_at)
                VALUES (%s, %s)
                RETURNING id;
                """,
                         (url, datetime.date.today())
                         )
            id = curs.fetchone()[0]
    return redirect(url_for('get_url_id', id=id))


@app.get('/urls')
def get_urls():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("""
                SELECT
                    urls.id,
                    urls.name,
                    COALESCE(MAX(url_checks.created_at)::varchar, '') AS date,
                    COALESCE(status_code::varchar, '') AS STATUS
                FROM urls
                LEFT JOIN url_checks ON url_checks.url_id = urls.id
                GROUP BY urls.id, urls.name, url_checks.status_code
                ORDER BY urls.id DESC;
            """)
            urls = curs.fetchall()
    return render_template('urls.html', urls=urls)


@app.get('/urls/<int:id>')
def get_url_id(id):
    message = get_flashed_messages(with_categories=True)
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("""
                SELECT
                    name, created_at
                FROM
                    urls
                WHERE
                id=%s
                """, (id,)
                         )
            name, date = curs.fetchone()
            curs.execute("""
                SELECT
                    id, status_code, h1, title, description, created_at
                FROM
                    url_checks
                WHERE
                    url_id=%s
                ORDER BY
                    id
                DESC;
                """, (id,)
                         )
            checks = curs.fetchall()

    return render_template(
        'url.html',
        url=name,
        id=id,
        created_at=date,
        messages=message,
        checks=checks
    )


@app.post('/urls/<int:id>/checks')
def post_check_id(id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("SELECT name FROM urls WHERE id=%s;", (id,))
            url = curs.fetchone()[0]
    try:
        with requests.get(url) as get:
            status = get.status_code
            html_data = get.content
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'error')
    soap = BeautifulSoup(html_data, 'html.parser')
    title = soap.title.text if soap.title is not None else ''
    h1 = soap.h1.text if soap.h1 is not None else ''
    content = soap.find('meta', {"name": "description"})
    content = content.attrs['content'] if content else ''
    flash('Страница успешно проверена', 'success')
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as curs:
            curs.execute("""
                        INSERT INTO url_checks (
                            url_id,
                            status_code,
                            h1,
                            title,
                            description,
                            created_at
                            )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                         (
                             id,
                             status,
                             h1,
                             title,
                             content,
                             datetime.date.today()
                         )
                         )
    return redirect(url_for('get_url_id', id=id))


if __name__ == '__main__':
    app.run()
