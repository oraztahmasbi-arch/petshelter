class AnimalNotFoundError(Exception):
    """Raised when an animal cannot be found."""
    pass


class DuplicateAnimalError(Exception):
    """Raised when an animal ID already exists."""
    pass


class AnimalAlreadyAdoptedError(Exception):
    """Raised when an unavailable animal is adopted again."""
    pass


class MaximumAdoptionReachedError(Exception):
    """Raised when an adopter reaches the adoption limit."""
    pass


class AdopterNotFoundError(Exception):
    """Raised when an adopter cannot be found."""
    pass


class DuplicateAdopterError(Exception):
    """Raised when an adopter ID or national ID already exists."""
    pass


class StorageError(Exception):
    """Raised when persistent storage cannot be read or written."""
    pass
