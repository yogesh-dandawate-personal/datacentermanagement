"""Password hashing and verification service using Argon2"""
import logging
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash, VerificationError

logger = logging.getLogger(__name__)


class PasswordService:
    """Service for secure password hashing and verification using Argon2"""

    def __init__(self):
        """Initialize password hasher with secure defaults"""
        self.hasher = PasswordHasher(
            time_cost=2,              # Iterations over memory
            memory_cost=65536,        # 64MB memory
            parallelism=4,            # 4 parallel threads
            hash_len=32,              # 256-bit hash
            salt_len=16               # 128-bit salt
        )

    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2

        Args:
            password: Plain text password to hash

        Returns:
            Argon2 hash string

        Raises:
            ValueError: If password is empty or invalid
        """
        if not password or not isinstance(password, str):
            raise ValueError("Password must be a non-empty string")

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        try:
            hashed = self.hasher.hash(password)
            logger.info("Password successfully hashed")
            return hashed
        except Exception as e:
            logger.error(f"Failed to hash password: {str(e)}")
            raise ValueError(f"Failed to hash password: {str(e)}")

    def verify_password(self, password: str, hash_value: str) -> bool:
        """
        Verify a password against its hash

        Args:
            password: Plain text password to verify
            hash_value: Argon2 hash to verify against

        Returns:
            True if password matches hash, False otherwise

        Raises:
            ValueError: If inputs are invalid
        """
        if not password or not hash_value:
            raise ValueError("Password and hash must not be empty")

        try:
            self.hasher.verify(hash_value, password)
            logger.info("Password verified successfully")
            return True
        except VerifyMismatchError:
            logger.debug("Password verification failed: mismatch")
            return False
        except (InvalidHash, VerificationError) as e:
            logger.warning(f"Password verification error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during password verification: {str(e)}")
            raise ValueError(f"Failed to verify password: {str(e)}")


# Singleton instance
_password_service = None


def get_password_service() -> PasswordService:
    """Get or create the password service singleton"""
    global _password_service
    if _password_service is None:
        _password_service = PasswordService()
    return _password_service
