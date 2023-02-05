import psycopg2
import os

from psycopg2.extras import NamedTupleCursor

DATABASE_URL = os.getenv('DATABASE_URL')


def create_url(url):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute("SELECT id FROM urls WHERE name=%s", (url,))
            queryset = curs.fetchone()
    return queryset


def insert_url(url, date):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute("""
                            INSERT INTO urls (name, created_at)
                            VALUES (%s, %s)
                            RETURNING id;
                            """,
                         (url, date)
                         )
            queryset = curs.fetchone()
    return queryset


def select_all():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute("""
                            SELECT
                                urls.id,
                                urls.name,
                                COALESCE(
                                MAX(url_checks.created_at)::varchar,
                                 ''
                                 ) AS date,
                                COALESCE(status_code::varchar, '') AS STATUS
                            FROM urls
                            LEFT JOIN url_checks ON url_checks.url_id = urls.id
                            GROUP BY urls.id, urls.name, url_checks.status_code
                            ORDER BY urls.id DESC;
                        """)
            queryset = curs.fetchall()
    return queryset


def select_url_by_id(id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute("""
                            SELECT
                                name, created_at
                            FROM
                                urls
                            WHERE
                            id=%s
                            """, (id,)
                         )
            queryset = curs.fetchone()
    return queryset


def select_url_checks(id):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute("""
                            SELECT
                                id,
                                status_code,
                                h1,
                                title,
                                description,
                                created_at
                            FROM
                                url_checks
                            WHERE
                                url_id=%s
                            ORDER BY
                                id
                            DESC;
                            """, (id,)
                         )
            queryset = curs.fetchall()
    return queryset


def insert_into_url_checks(id, status, h1, title, content, created_at):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
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
                             created_at
                         )
                         )
