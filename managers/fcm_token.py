from managers.db import DBManager, Request


class FcmTokenManager:
    @staticmethod
    def get_fcm_token_list_from_user_id(user_id):
        # user_id를 가진 DB 조회
        db_manager = DBManager()
        request = Request().select('fcm_device', ['fcm_token']).filter(user_id=user_id)
        response = db_manager.response(request)

        fcm_token_list = [fcm_token[0] for fcm_token in response]

        return fcm_token_list

    @staticmethod
    def set_device_to_db(device):
        user_id = device.user_id
        fcm_token = device.fcm_token
        db_manager = DBManager()
        # user_id - fcm_token 쌍이 같은 Device일 경우, insert하지 않음 = 중복제거
        request = Request().select('fcm_device', ['fcm_token']).filter(user_id=user_id, fcm_token=fcm_token)
        response = db_manager.response(request)
        if not response:
            request = Request().insert('fcm_device', user_id=user_id, fcm_token=fcm_token)
            db_manager.response(request)

    @staticmethod
    def delete_devices(fcm_token):
        db_manager = DBManager()
        request = Request().delete('fcm_device').filter(fcm_token=f"'{fcm_token}'")
        db_manager.response(request)


class Device:
    user_id = None
    fcm_token = None

    def __init__(self, user_id, fcm_token):
        self._set_user_id(user_id)
        self._set_fcm_token(fcm_token)

    def _set_user_id(self, user_id):
        self.user_id = user_id

    def _set_fcm_token(self, fcm_token):
        self.fcm_token = fcm_token
