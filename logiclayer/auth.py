import abc
from typing import Any, List, Mapping, NamedTuple, Optional

import enum


class AuthTokenType(enum.Enum):
    APIKEY = enum.auto()
    BASIC = enum.auto()
    CUSTOM = enum.auto()
    DIGEST = enum.auto()
    JWTOKEN = enum.auto()
    OAUTH10A = enum.auto()
    OAUTH20 = enum.auto()


class AuthToken(NamedTuple):
    """Defines a transport object for the parsed token used in a server request."""

    kind = AuthTokenType
    value = str


class AuthProvider(abc.ABC):
    @abc.abstractmethod
    def get_roles(self, token: Optional["AuthToken"]) -> List[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_user(self, token: Optional["AuthToken"]) -> Optional[Mapping[str, Any]]:
        raise NotImplementedError


class VoidAuthProvider(AuthProvider):
    def get_roles(self, token):
        return []

    def get_user(self, token):
        return None
