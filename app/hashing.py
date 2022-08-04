from passlib.context import CryptContext


password_context = CryptContext(schemes=['bcrypt'],
                                deprecated='auto')


class Hasher:
    @staticmethod
    def hash_password(password):
        return password_context.hash(password)

    @staticmethod
    def verify_password(raw_password, hashed_password):
        return password_context.verify(raw_password, hashed_password)