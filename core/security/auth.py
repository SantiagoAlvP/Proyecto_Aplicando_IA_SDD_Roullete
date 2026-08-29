from typing import Optional



class User:
    def __init__(self, user_id: int, name: str = ""):
        self.id = user_id
        self.name = name


async def get_optional_current_user() -> Optional[User]:
    """Placeholder dependency. Returns None (unauthenticated).

    Replace with real token parsing and user lookup when auth is available.
    """
    return None


def is_owner(user: Optional[User], owner_id: int) -> bool:
    if not user:
        return False
    return user.id == owner_id


def has_permission(user: Optional[User], permission: str) -> bool:
    # Placeholder: always False. Integrate with roles/permissions system.
    return False
