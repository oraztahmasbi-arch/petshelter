import re
import uuid
from typing import Optional


class Adopter:
    """Represent a person registered to adopt animals."""

    PHONE_PATTERN = re.compile(r"09\d{9}")
    NATIONAL_ID_PATTERN = re.compile(r"\d{10}")

    def __init__(
        self,
        name: str,
        phone: str,
        national_id: str,
        adopter_id: Optional[str] = None,
        adopted_animals: Optional[list[str]] = None,
    ) -> None:
        if not self.is_valid_name(name):
            raise ValueError("Invalid adopter name")
        if not self.is_valid_phone(phone):
            raise ValueError("Invalid phone number")
        if not self.is_valid_national_id(national_id):
            raise ValueError("Invalid national ID")
        if adopter_id is not None and (
            not isinstance(adopter_id, str) or not adopter_id.strip()
        ):
            raise ValueError("Invalid adopter ID")
        if adopted_animals is not None:
            if not isinstance(adopted_animals, list):
                raise ValueError("Adopted animals must be a list")
            if any(
                not isinstance(animal_id, str) or not animal_id.strip()
                for animal_id in adopted_animals
            ):
                raise ValueError("Invalid animal ID in adopter records")
            adopted_animals = [animal_id.strip() for animal_id in adopted_animals]
            if len(adopted_animals) != len(set(adopted_animals)):
                raise ValueError("Duplicate animal IDs in adopter records")

        self.name = name.strip()
        self.phone = phone.strip()
        self.national_id = national_id.strip()
        self.adopter_id = (
            adopter_id.strip()
            if adopter_id is not None
            else uuid.uuid4().hex[:8].upper()
        )
        self.adopted_animals = list(adopted_animals) if adopted_animals is not None else []

    @staticmethod
    def is_valid_name(name: str) -> bool:
        """Return whether the adopter name is a non-empty string."""
        return isinstance(name, str) and bool(name.strip())

    @classmethod
    def is_valid_phone(cls, phone: str) -> bool:
        """Validate an Iranian mobile number in 09xxxxxxxxx format."""
        return (
            isinstance(phone, str)
            and cls.PHONE_PATTERN.fullmatch(phone.strip()) is not None
        )

    @classmethod
    def is_valid_national_id(cls, national_id: str) -> bool:
        """Validate the ten-digit national ID format required by the assignment."""
        return (
            isinstance(national_id, str)
            and cls.NATIONAL_ID_PATTERN.fullmatch(national_id.strip()) is not None
        )

    def to_dict(self) -> dict:
        """Serialize adopter information."""
        return {
            "adopter_id": self.adopter_id,
            "name": self.name,
            "phone": self.phone,
            "national_id": self.national_id,
            "adopted_animals": list(self.adopted_animals),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Adopter":
        """Create an Adopter from a dictionary."""
        if not isinstance(data, dict):
            raise TypeError("Adopter data must be a dictionary")
        return cls(
            name=data["name"],
            phone=data["phone"],
            national_id=data["national_id"],
            adopter_id=data.get("adopter_id"),
            adopted_animals=data.get("adopted_animals", []),
        )
