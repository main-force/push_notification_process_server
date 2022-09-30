import os

import dotenv

from managers.fcm_token import FcmTokenManager
import firebase_admin
from firebase_admin import messaging


class PushNotification:
    fcm_token = None
    title = None
    body = None
    redirect_url = None

    def __init__(self, fcm_token, title, body, redirect_url=None):
        self.fcm_token = fcm_token
        self.title = title
        self.body = body
        self.redirect_url = redirect_url


class PushNotificationManager:
    initialized = False

    def __init__(self):
        dotenv_file = dotenv.find_dotenv()
        if dotenv_file:
            dotenv.load_dotenv(dotenv_file)

        credential_path = os.environ['CREDENTIAL_PATH']
        credentials = firebase_admin.credentials.Certificate(credential_path)
        if not self.initialized:
            firebase_admin.initialize_app(credentials)
        self.initialized = True

    @staticmethod
    def generate_push_notification_list(web_notification):
        """
        :param web_notification: WebNotification Object
        :return: list
        """
        recipient_id = web_notification.recipient_id

        title = 'GENUS'
        body = web_notification.description
        redirect_url = web_notification.get_object_redirect_url()

        fcm_token_list = FcmTokenManager.get_device_list_from_user_id(recipient_id)
        push_notification_list = []

        for fcm_token in fcm_token_list:
            push_notification = PushNotification(fcm_token, title, body, redirect_url)
            push_notification_list.append(push_notification)

        return push_notification_list

    @staticmethod
    def send_push_notification(push_notification):
        message = _get_notification_message_data(push_notification)
        response = messaging.send(message)
        print(response)


def _get_notification_message_data(push_notification):
    """
    :param push_notification: PushNotification Object
    :return: firebase server로 전송 가능한 메시지 객체
    """
    title = push_notification.title
    body = push_notification.body
    notification = messaging.Notification(
        title=title,
        body=body
    )

    data = {}
    redirect_url = push_notification.redirect_url
    if redirect_url:
        data['redirect_url'] = redirect_url

    fcm_token = push_notification.fcm_token
    message = messaging.Message(
        token=fcm_token,
        notification=notification,
        data=data
    )

    return message
