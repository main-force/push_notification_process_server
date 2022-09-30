from notification import NotificationManager
# from managers.session import SessionManager, Session
# from managers.fcm_token import FcmTokenManager, Device
# from managers.notification.push_notification import PushNotificationManager, PushNotification

if __name__ == 'run':
    notification_manager = NotificationManager()
    notification_manager.run_push_notification_process()

# if __name__ == '__main__':
#     session_manager = SessionManager()
#     session = Session(session_key='cqzf860kt3xh9bb92g2fw2y29g522ie9')
#     print(SessionManager.get_user_id(session))
#     print(FcmTokenManager.get_device_list_from_user_id(5))
#     device = Device(user_id=156, fcm_token='eoWmwmDgwURMqBvGk70PLm:APA91bEEEorrf0YizlxyhTW-KHm41lCXL9nsfgEcVTdn8mP5C7D2CzEXIwiJGNKVIIzCr_hj39QhZ9yngyVKwaHshbv2aztIGaRsvT85l5BKNerOX4Ny0WrLCUeCFy_tYyQ6h4OZpixC')
#     FcmTokenManager.set_device_to_db(device)
#     push_noti = PushNotification(fcm_token='eoWmwmDgwURMqBvGk70PLm:APA91bEEEorrf0YizlxyhTW-KHm41lCXL9nsfgEcVTdn8mP5C7D2CzEXIwiJGNKVIIzCr_hj39QhZ9yngyVKwaHshbv2aztIGaRsvT85l5BKNerOX4Ny0WrLCUeCFy_tYyQ6h4OZpixC',
#                                  body='나를 기계로 사용하는구나',
#                                  title='GENUS'
#                                  )
#     push_noti_manager = PushNotificationManager()
#     push_noti_manager.send_push_notification(push_noti)
#     print('finish')