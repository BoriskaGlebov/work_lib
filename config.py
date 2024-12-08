import os.path

current_directory = os.path.dirname(os.path.abspath(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(current_directory,'test.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))
    print(os.path.join(current_directory, "test.db"))
