import os
import sqlite3
import hashlib
import datetime

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    from sqlalchemy import create_engine, text
    engine = create_engine(DATABASE_URL)

user_db_file_location = "database_file/users.db"
note_db_file_location = "database_file/notes.db"
image_db_file_location = "database_file/images.db"


def list_users():
    if DATABASE_URL:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id FROM users;"))
            return [row[0] for row in result.fetchall()]

    _conn = sqlite3.connect(user_db_file_location)
    _c = _conn.cursor()
    _c.execute("SELECT id FROM users;")
    result = [x[0] for x in _c.fetchall()]
    _conn.close()
    return result


def verify(id, pw):
    if DATABASE_URL:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT pw FROM users WHERE id = :id"), {"id": id})
            row = result.fetchone()
            return row[0] == hashlib.sha256(pw.encode()).hexdigest()

    _conn = sqlite3.connect(user_db_file_location)
    _c = _conn.cursor()
    _c.execute("SELECT pw FROM users WHERE id = ?;", (id,))
    result = _c.fetchone()[0] == hashlib.sha256(pw.encode()).hexdigest()
    _conn.close()
    return result


def delete_user_from_db(id):
    if DATABASE_URL:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM users WHERE id = :id"), {"id": id})
            conn.execute(text("DELETE FROM notes WHERE user = :id"), {"id": id})
            conn.execute(text("DELETE FROM images WHERE owner = :id"), {"id": id})
            conn.commit()
        return

    _conn = sqlite3.connect(user_db_file_location)
    _c = _conn.cursor()
    _c.execute("DELETE FROM users WHERE id = ?;", (id,))
    _conn.commit()
    _conn.close()

    _conn = sqlite3.connect(note_db_file_location)
    _c = _conn.cursor()
    _c.execute("DELETE FROM notes WHERE user = ?;", (id,))
    _conn.commit()
    _conn.close()

    _conn = sqlite3.connect(image_db_file_location)
    _c = _conn.cursor()
    _c.execute("DELETE FROM images WHERE owner = ?;", (id,))
    _conn.commit()
    _conn.close()


def add_user(id, pw):
    if DATABASE_URL:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO users VALUES (:id, :pw)"),
                {"id": id.upper(), "pw": hashlib.sha256(pw.encode()).hexdigest()}
            )
            conn.commit()
        return

    _conn = sqlite3.connect(user_db_file_location)
    _c = _conn.cursor()
    _c.execute("INSERT INTO users values(?, ?)", (id.upper(), hashlib.sha256(pw.encode()).hexdigest()))
    _conn.commit()
    _conn.close()


def read_note_from_db(id):
    if DATABASE_URL:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT note_id, timestamp, note FROM notes WHERE user = :id"),
                {"id": id.upper()}
            )
            return result.fetchall()

    _conn = sqlite3.connect(note_db_file_location)
    _c = _conn.cursor()
    _c.execute("SELECT note_id, timestamp, note FROM notes WHERE user = ?;", (id.upper(),))
    result = _c.fetchall()
    _conn.close()
    return result


def match_user_id_with_note_id(note_id):
    if DATABASE_URL:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT user FROM notes WHERE note_id = :note_id"),
                {"note_id": note_id}
            )
            return result.fetchone()[0]

    _conn = sqlite3.connect(note_db_file_location)
    _c = _conn.cursor()
    _c.execute("SELECT user FROM notes WHERE note_id = ?;", (note_id,))
    result = _c.fetchone()[0]
    _conn.close()
    return result


def write_note_into_db(id, note_to_write):
    current_timestamp = str(datetime.datetime.now())
    note_id = hashlib.sha1((id.upper() + current_timestamp).encode()).hexdigest()

    if DATABASE_URL:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO notes VALUES (:user, :timestamp, :note, :note_id)"),
                {"user": id.upper(), "timestamp": current_timestamp, "note": note_to_write, "note_id": note_id}
            )
            conn.commit()
        return

    _conn = sqlite3.connect(note_db_file_location)
    _c = _conn.cursor()
    _c.execute("INSERT INTO notes values(?, ?, ?, ?)", (id.upper(), current_timestamp, note_to_write, note_id))
    _conn.commit()
    _conn.close()


def delete_note_from_db(note_id):
    if DATABASE_URL:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM notes WHERE note_id = :note_id"), {"note_id": note_id})
            conn.commit()
        return

    _conn = sqlite3.connect(note_db_file_location)
    _c = _conn.cursor()
    _c.execute("DELETE FROM notes WHERE note_id = ?;", (note_id,))
    _conn.commit()
    _conn.close()


def image_upload_record(uid, owner, image_name, timestamp):
    if DATABASE_URL:
        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO images VALUES (:uid, :owner, :name, :timestamp)"),
                {"uid": uid, "owner": owner, "name": image_name, "timestamp": timestamp}
            )
            conn.commit()
        return

    _conn = sqlite3.connect(image_db_file_location)
    _c = _conn.cursor()
    _c.execute("INSERT INTO images VALUES (?, ?, ?, ?)", (uid, owner, image_name, timestamp))
    _conn.commit()
    _conn.close()


def list_images_for_user(owner):
    if DATABASE_URL:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT uid, timestamp, name FROM images WHERE owner = :owner"),
                {"owner": owner}
            )
            return result.fetchall()

    _conn = sqlite3.connect(image_db_file_location)
    _c = _conn.cursor()
    _c.execute("SELECT uid, timestamp, name FROM images WHERE owner = ?;", (owner,))
    result = _c.fetchall()
    _conn.close()
    return result


def match_user_id_with_image_uid(image_uid):
    if DATABASE_URL:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT owner FROM images WHERE uid = :uid"),
                {"uid": image_uid}
            )
            return result.fetchone()[0]

    _conn = sqlite3.connect(image_db_file_location)
    _c = _conn.cursor()
    _c.execute("SELECT owner FROM images WHERE uid = ?;", (image_uid,))
    result = _c.fetchone()[0]
    _conn.close()
    return result


def delete_image_from_db(image_uid):
    if DATABASE_URL:
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM images WHERE uid = :uid"), {"uid": image_uid})
            conn.commit()
        return

    _conn = sqlite3.connect(image_db_file_location)
    _c = _conn.cursor()
    _c.execute("DELETE FROM images WHERE uid = ?;", (image_uid,))
    _conn.commit()
    _conn.close()


if __name__ == "__main__":
    print(list_users())
