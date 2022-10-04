from notification import NotificationManager
from managers.session import SessionManager, Session
from managers.fcm_token import FcmTokenManager, Device
from managers.notification.push_notification import PushNotificationManager, PushNotification

if __name__ == '__main__':
    notification_manager = NotificationManager()
    notification_manager.run_push_notification_process()

# if __name__ == '__main__':
#     push_noti = PushNotification(fcm_token='test',
#                                  body='나를 기계로 사용하는구나',
#                                  title='GENUS'
#                                  )
#     push_noti_manager = PushNotificationManager()
#     push_noti_manager.send_push_notification(push_noti)
#     print('finish')
