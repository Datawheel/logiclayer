import abc
from typing import Any, Coroutine, Union

from fastapi import APIRouter


class LogicLayerModule(abc.ABC):
    """Base class for LogicLayer Modules.

    Modules should follow the structure of this class on their implementation.
    A LogicLayer Module only needs a `router` property, containing an instance
    of FastAPI APIRouter class, and a `setup` method which doesn't take
    additional parameters and returns the router instance.
    This `setup` method should initialize any needed
    """

    @abc.abstractmethod
    def setup(self, router: APIRouter) -> Union[None, Coroutine[Any, Any, None]]:
        pass
