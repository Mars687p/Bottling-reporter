from app.Configuration import get_user_id


class User():
    def __init__(self, usr_id, quantity_notifications=0):
        self.id = usr_id
        self.quantity_notifications = quantity_notifications

def get_lst_users():  
    return [User(i) for i in get_user_id()]
