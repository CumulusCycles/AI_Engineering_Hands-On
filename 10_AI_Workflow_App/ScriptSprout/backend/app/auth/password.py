from __future__ import annotations

import bcrypt


def hash_password(plain: str) -> str:
    """Hash sensitive input using the configured algorithm.

    Args:
        plain: Input value used to perform this operation.

    Returns:
        Result generated for the caller.

    """

    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify input validity and return the verification result.

    Args:
        plain: Input value used to perform this operation.
        hashed: Input value used to perform this operation.

    Returns:
        Result generated for the caller.

    """

    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False
