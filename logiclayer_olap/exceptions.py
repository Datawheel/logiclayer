from fastapi import HTTPException


class HTTPError(HTTPException):
    """Base class for exceptions in this module."""
    pass


class InvalidFormatHTTPError(HTTPError):
    """Should be raised if while attempting to contact an upstream server, the
    library points the format requested is not valid.

    Returns a 400 HTTP status code, and gives details about the error.
    """

    def __init__(self, extension: str) -> None:
        message = "Requested response format {} is not supported for this operation.".format(extension)
        super().__init__(status_code=400, detail=message)


class InvalidParameterHTTPError(HTTPError):
    def __init__(self, param_name: str) -> None:
        message = "The parameter {} in the request is not valid.".format(param_name)
        super().__init__(status_code=400, detail=message)


class UpstreamUnavailableHTTPError(HTTPError):
    def __init__(self) -> None:
        message = "The origin server is not available at the moment. Try again in a few minutes."
        super().__init__(status_code=504, detail=message)
