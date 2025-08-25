import bcrypt
from src.core.logger import logger


class PasswordHandler:
    @staticmethod
    def hash(password: str) -> str:
        # Implement password hashing logic here
        pwd_bytes = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
        return str(hashed_password.decode("utf-8"))

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            password_byte_enc = plain_password.encode("utf-8")
            hashed_password_bytes = hashed_password.encode("utf-8")
            return bool(bcrypt.checkpw(password_byte_enc, hashed_password_bytes))
        except Exception as err:  # pylint: disable=broad-except
            logger.error("PasswordHandler Exception verify_password %s", err)
            return False
