import psycopg2
import psycopg2.extras
from flask import g
from config import Config

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            dbname=Config.DB_NAME,
            port=Config.DB_PORT,
            sslmode='require'          # Supabase requires SSL
        )
        g.db.autocommit = False
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception:
            pass

def query_db(query, args=(), one=False, commit=False):
    """
    Executes a query and returns results as list of dicts.
    psycopg2 uses %s placeholders — same as mysql-connector, no changes needed in models.
    For INSERT with commit=True, returns the new row's id via RETURNING id.
    """
    db = get_db()
    # Add RETURNING id to INSERT statements so we can return lastrowid
    exec_query = query
    if commit and query.strip().upper().startswith('INSERT'):
        # Strip trailing semicolon if any, add RETURNING id
        exec_query = query.rstrip().rstrip(';') + ' RETURNING id'

    with db.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(exec_query, args)
        if commit:
            db.commit()
            if exec_query != query:          # was INSERT → has RETURNING
                row = cur.fetchone()
                result = row['id'] if row else None
            else:
                result = None
        else:
            result = cur.fetchone() if one else cur.fetchall()

    # Convert RealDictRow → plain dict so Jinja can handle it
    if isinstance(result, list):
        return [dict(r) for r in result]
    if result is not None and not isinstance(result, (int, type(None))):
        return dict(result)
    return result

def init_app(app):
    app.teardown_appcontext(close_db)
