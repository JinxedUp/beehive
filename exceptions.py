class DiscordError(Exception):
    """Base exception for Discord-related errors"""
    pass

class RateLimitError(DiscordError):
    """Raised when a rate limit is hit"""
    def __init__(self, retry_after: float, message: str = None):
        self.retry_after = retry_after
        super().__init__(message or f"Rate limit hit. Try again in {retry_after:.2f}s")

class PermissionError(DiscordError):
    """Raised when the bot lacks required permissions"""
    def __init__(self, permission: str, message: str = None):
        self.permission = permission
        super().__init__(message or f"Missing required permission: {permission}")

class HTTPError(DiscordError):
    """Raised when a Discord API request fails"""
    def __init__(self, status: int, message: str):
        self.status = status
        super().__init__(f"HTTP {status}: {message}")

class NotFoundError(DiscordError):
    """Raised when a resource is not found"""
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found")

class ForbiddenError(DiscordError):
    """Raised when access is forbidden"""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message)
