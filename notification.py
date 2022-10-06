import time

from managers.notification.web_notification import WebNotificationManager
from managers.notification.push_notification import PushNotificationManager

DEFAULT_RETRIEVE_PERIOD = 10


class NotificationManager:
    last_retrieve_time = None
    retrieve_period = None
    must_sleep_time = None

    def __init__(self, retrieve_period=DEFAULT_RETRIEVE_PERIOD):
        self.retrieve_period = retrieve_period
        self.last_retrieve_time = time.time() - retrieve_period

    def run_push_notification_process(self):
        push_notification_manager = PushNotificationManager()
        while self._is_time_to_retrieve():
            try:
                web_notification_list = self._retrieve_unemailed_web_notification()
                for web_notification in web_notification_list:
                    push_notification_list = push_notification_manager.generate_push_notification_list(web_notification)
                    for push_notification in push_notification_list:
                        push_notification_manager.send_push_notification(push_notification)
                    WebNotificationManager.set_web_notification_emailed(web_notification)
            finally:
                current_time_str = time.strftime('%c', time.localtime(time.time()))
                print(f'[{current_time_str}] Finish a cycle for processing unemailed WebNotifications')

    def _retrieve_unemailed_web_notification(self):
        retrieve_time = time.time()
        web_notification_list = WebNotificationManager.get_web_notification_list_unemailed()
        self.last_retrieve_time = retrieve_time

        return web_notification_list

    def _is_time_to_retrieve(self):
        current_time = time.time()
        last_retrieve_time = self.last_retrieve_time
        time_gap = current_time - last_retrieve_time

        if self.retrieve_period > time_gap:
            self.must_sleep_time = self.retrieve_period - time_gap
            self._sleep()

        return True

    def _sleep(self):
        current_time_str = time.strftime('%c', time.localtime(time.time()))
        print(f'[{current_time_str}] Sleep {self.must_sleep_time}s...')
        time.sleep(self.must_sleep_time)
