import enum

from managers.db import DBManager, Request

web_notification_db_columns = ['id', 'recipient_id', 'description', 'channel_id', 'note_id', 'post_id']


class WebNotificationManager:

    @staticmethod
    def get_web_notification_list_unemailed():
        web_notification_list = []
        raw_notification_list = _get_notification_list_unemailed_from_db()
        if raw_notification_list:
            for raw_notification in raw_notification_list:
                # WebNotification 생성 후 list에 추가.
                notification_id = raw_notification[web_notification_db_columns.index('id')]
                recipient_id = raw_notification[web_notification_db_columns.index('recipient_id')]
                description = raw_notification[web_notification_db_columns.index('description')]
                channel_id = raw_notification[web_notification_db_columns.index('channel_id')]
                post_id = raw_notification[web_notification_db_columns.index('post_id')]
                note_id = raw_notification[web_notification_db_columns.index('note_id')]
                if post_id:
                    target_object_type = TargetObjectType.POST
                    target_object_id = post_id
                elif note_id:
                    target_object_type = TargetObjectType.NOTE
                    target_object_id = note_id
                else:
                    raise ValueError('object_id가 존재하지 않습니다.')

                web_notification = WebNotification(notification_id=notification_id,
                                                   recipient_id=recipient_id,
                                                   description=description,
                                                   channel_id=channel_id,
                                                   target_object_type=target_object_type,
                                                   target_object_id=target_object_id)

                web_notification_list.append(web_notification)

        return web_notification_list

    @staticmethod
    def set_web_notification_emailed(web_notification):
        _set_notification_emailed_to_db(web_notification)

def _get_notification_list_unemailed_from_db():
    db_manager = DBManager()
    request = Request() \
        .select(table_name='notification_notification',
                columns=web_notification_db_columns) \
        .filter(emailed='f')
    response = db_manager.response(request)
    return response


def _set_notification_emailed_to_db(web_notification):
    db_manager = DBManager()
    request = Request() \
        .update(table_name='notification_notification',
                emailed='t') \
        .filter(id=web_notification.notification_id)
    db_manager.response(request)


class TargetObjectType(enum.Enum):
    POST = 1
    NOTE = 2


class WebNotification:
    notification_id = None
    recipient_id = None
    description = None
    channel_id = None
    target_object_type = None
    target_object_id = None

    def __init__(self, notification_id, recipient_id, description, channel_id, target_object_type, target_object_id):
        self.notification_id = notification_id
        self.recipient_id = recipient_id
        self.description = description
        self.channel_id = channel_id
        self.target_object_type = target_object_type
        self.target_object_id = target_object_id

    def get_object_redirect_url(self):
        if self.target_object_type == TargetObjectType.POST:
            post_id = self.target_object_id
            channel_id = self.channel_id
            try:
                board_category_id = _get_board_category(post_id=post_id)
                redirect_url = _generate_redirect_url_for_post(channel_id, board_category_id, post_id)
                return redirect_url
            except ValueError:
                return None

        elif self.target_object_type == TargetObjectType.NOTE:
            note_id = self.target_object_id
            channel_id = self.channel_id

            redirect_url = _generate_redirect_url_for_note(channel_id, note_id)
            return redirect_url

        else:
            return None


def _get_board_category(post_id):
    # DB 재 조회 시, post 삭제 되어 있을 가능성이 있으므로 error 처리 해주어야 함.
    db_manager = DBManager()
    request = Request() \
        .select(table_name='catalog_post', columns=['catalog_post.board_category_id']) \
        .filter(id=post_id)
    response = db_manager.response(request)
    if not response:
        raise ValueError('존재하지않는 post 입니다.')
    board_category = response[0][0]
    return board_category


def _generate_redirect_url_for_post(channel_id, board_category_id, post_id):
    return f'https://genus.co.kr/catalog/{channel_id}/{board_category_id}/{post_id}'


def _generate_redirect_url_for_note(channel_id, note_id):
    return f'https://genus.co.kr/note/notes/{channel_id}/{note_id}'