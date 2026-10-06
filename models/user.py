class User:
    def __init__(self, user_id=None, full_name="", email="", mobile="", username="", password=""):
        self.user_id = user_id
        self.full_name = full_name
        self.email = email
        self.mobile = mobile
        self.username = username
        self.password = password

    def display_user(self):
        print("\n========== USER PROFILE ==========")
        print(f"User ID   : {self.user_id}")
        print(f"Full Name : {self.full_name}")
        print(f"Email     : {self.email}")
        print(f"Mobile    : {self.mobile}")
        print(f"Username  : {self.username}")