import abc
import enum
from typing import Any, Iterable, Mapping, NamedTuple, Optional, Set

from .common import LogicLayerException


class NotAuthorized(LogicLayerException):
    """The roles provided don't match the roles needed to access some of the
    requested parameters."""

    def __init__(self, resource: str, roles: Iterable[str]) -> None:
        super().__init__(
            f"Requested resource '{resource}' is not allowed for the roles "
            f"provided by authorization credentials: '{', '.join(roles)}'"
        )
        self.resource = resource
        self.roles = roles


class AuthTokenType(enum.Enum):
    SEARCHPARAM = enum.auto()
    BASIC = enum.auto()
    CUSTOM = enum.auto()
    DIGEST = enum.auto()
    JWTOKEN = enum.auto()
    OAUTH10A = enum.auto()
    OAUTH20 = enum.auto()


class AuthToken(NamedTuple):
    """Defines a container for the parsed token used in a server request."""

    kind: AuthTokenType
    value: str


class AuthProvider(abc.ABC):
    @abc.abstractmethod
    def get_roles(self, token: Optional["AuthToken"]) -> Set[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, token: Optional["AuthToken"]) -> Optional[Mapping[str, Any]]:
        raise NotImplementedError


class VoidAuthProvider(AuthProvider):
    def get_roles(self, token):
        return set()

    def get_user(self, token):
        return None
