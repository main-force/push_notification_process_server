import base64
import zlib
import json

from managers.db import Request, DBManager

SESSION_DATA_LENGTH = 227
AUTH_USER_STR = '.eJx'


class Session:
    session_key = None
    session_data = None

    def __init__(self, session_key):
        self.session_key = session_key
        SessionManager.set_session_data(self)


class SessionManager:
    @staticmethod
    def set_session_data(session):
        if not session.session_key:
            raise ValueError('Session 객체에 session_key가 존재하지 않습니다.')
        db_manager = DBManager()
        request = Request().select('django_session', ['session_data']).filter(session_key=session.session_key)
        response = db_manager.response(request)

        if not response:
            raise ValueError(f'해당 session_key의 데이터가 없습니다: {session.session_key}')
        session_data_raw = response[0][0]
        session_data_processed = _clean_session_data(session_data_raw)
        session.session_data = session_data_processed

    @staticmethod
    def get_user_id(session):
        if not session.session_data.startswith(AUTH_USER_STR):
            # Anonymous User
            user_id = None
        else:
            # Auth User
            data_json = _extract_session_data_to_json(session.session_data)
            user_id = int(data_json['_auth_user_id'])
        return user_id


def _clean_session_data(session_data):
    session_data_len = len(session_data)
    if session_data_len > SESSION_DATA_LENGTH:
        session_data = session_data[:SESSION_DATA_LENGTH]
    else:
        session_data = session_data.ljust(SESSION_DATA_LENGTH, '0')
    return session_data


def _extract_session_data_to_json(session_data):
    data_decoded = base64.urlsafe_b64decode(session_data)
    data_decompressed = zlib.decompress(data_decoded)
    data_json = json.loads(data_decompressed)
    return data_json
