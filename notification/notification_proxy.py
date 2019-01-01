import ast


class NotificationProxy(object):
    def __init__(self, notif):
        self.verb = notif.verb
        self.description = notif.description
        self.link = ast.literal_eval(notif.data['data'])['link']
        self.unread = notif.unread
        self.logo_url = notif.target.logo_url()
