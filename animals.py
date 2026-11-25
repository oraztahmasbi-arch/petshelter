import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Optional


class Animal:
    """Represent an animal registered in the pet shelter."""

    def __init__(
        self,
        name: str,
        age: int,
        gender: str,
        breed: str,
        animal_id: Optional[str] = None,
        adopted: bool = False,
        adopter_id: Optional[str] = None,
        health_records: Optional[list[dict]] = None,
        adoption_history: Optional[list[dict]] = None,
    ) -> None:
        if not self.is_valid_name(name):
            raise ValueError("Invalid animal name")
        if not self.is_valid_age(age):
            raise ValueError("Invalid animal age")
        if not self.is_valid_gender(gender):
            raise ValueError("Invalid animal gender")
        if not self.is_valid_breed(breed):
            raise ValueError("Invalid animal breed")
        if not isinstance(adopted, bool):
            raise ValueError("Adoption status must be a boolean")
        if animal_id is not None and (
            not isinstance(animal_id, str) or not animal_id.strip()
        ):
            raise ValueError("Invalid animal ID")
        if adopter_id is not None and (
            not isinstance(adopter_id, str) or not adopter_id.strip()
        ):
            raise ValueError("Invalid adopter ID")
        if adopted != (adopter_id is not None):
            raise ValueError("Adoption status and adopter ID are inconsistent")

        self._validate_health_records(
            [] if health_records is None else health_records
        )
        self._validate_adoption_history(
            [] if adoption_history is None else adoption_history
        )

        self.name = name.strip()
        self.age = age
        self.gender = gender.strip().capitalize()
        self.breed = breed.strip()
        self.animal_id = (
            animal_id.strip()
            if animal_id is not None
            else uuid.uuid4().hex[:8].upper()
        )
        self.adopted = adopted
        self.adopter_id = adopter_id.strip() if adopter_id is not None else None
        self.health_records = deepcopy(health_records) if health_records is not None else []
        self.adoption_history = deepcopy(adoption_history) if adoption_history is not None else []

    @property
    def adoption_status(self) -> str:
        """Return the human-readable adoption status."""
        return "Adopted" if self.adopted else "Available"

    def show_info(self) -> None:
        """Print the animal's details, health records, and adoption history."""
        print("\n" + "-" * 48)
        print(f"Animal Type: {type(self).__name__}")
        print(f"Animal ID: {self.animal_id}")
        print(f"Name: {self.name}")
        print(f"Age: {self.age}")
        print(f"Gender: {self.gender}")
        print(f"Breed: {self.breed}")
        print(f"Adoption Status: {self.adoption_status}")
        print(f"Adopter ID: {self.adopter_id or 'N/A'}")

        print("\nHealth Records:")
        if not self.health_records:
            print("No health records available.")
        else:
            for index, record in enumerate(self.health_records, start=1):
                print(
                    f"{index}. {record['record_type']} | "
                    f"{record['description']} | {record['timestamp']}"
                )

        print("\nAdoption History:")
        if not self.adoption_history:
            print("No adoption history available.")
        else:
            for index, event in enumerate(self.adoption_history, start=1):
                print(
                    f"{index}. {event['event']} | "
                    f"Adopter: {event['adopter_id']} | "
                    f"{event['timestamp']}"
                )
        print("-" * 48)

    @staticmethod
    def is_valid_name(name: str) -> bool:
        """Return whether a name is a non-empty string."""
        return isinstance(name, str) and bool(name.strip())

    @staticmethod
    def is_valid_age(age: int) -> bool:
        """Return whether age is a non-negative integer (not a boolean)."""
        return isinstance(age, int) and not isinstance(age, bool) and age >= 0

    @staticmethod
    def is_valid_breed(breed: str) -> bool:
        """Return whether breed is a non-empty string."""
        return isinstance(breed, str) and bool(breed.strip())

    @staticmethod
    def is_valid_gender(gender: str) -> bool:
        """Accept the supported gender values."""
        return (
            isinstance(gender, str)
            and gender.strip().casefold() in {"male", "female"}
        )

    @staticmethod
    def _validate_health_records(records: list) -> None:
        if not isinstance(records, list):
            raise ValueError("Health records must be a list")
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("Each health record must be a dictionary")
            required = {"record_type", "description", "timestamp"}
            if not required.issubset(record):
                raise ValueError("Incomplete health record")
            if any(
                not isinstance(record[key], str) or not record[key].strip()
                for key in required
            ):
                raise ValueError("Invalid health record fields")

    @staticmethod
    def _validate_adoption_history(history: list) -> None:
        if not isinstance(history, list):
            raise ValueError("Adoption history must be a list")
        for event in history:
            if not isinstance(event, dict):
                raise ValueError("Each adoption event must be a dictionary")
            required = {"event", "adopter_id", "timestamp"}
            if not required.issubset(event):
                raise ValueError("Incomplete adoption history event")
            if any(
                not isinstance(event[key], str) or not event[key].strip()
                for key in required
            ):
                raise ValueError("Invalid adoption history fields")
            if event["event"].casefold() not in {"adopted", "returned"}:
                raise ValueError("Unknown adoption history event")

    def add_health_record(self, record_type: str, description: str) -> None:
        """Append a timestamped health record."""
        if not isinstance(record_type, str) or not record_type.strip():
            raise ValueError("Invalid health record type")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Invalid health record description")

        self.health_records.append(
            {
                "record_type": record_type.strip(),
                "description": description.strip(),
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        )

    def add_adoption_event(self, event: str, adopter_id: str) -> None:
        """Append a timestamped adoption or return event."""
        if not isinstance(event, str) or event.strip().casefold() not in {
            "adopted", "returned"
        }:
            raise ValueError("Unknown adoption event")
        if not isinstance(adopter_id, str) or not adopter_id.strip():
            raise ValueError("Invalid adopter ID")

        self.adoption_history.append(
            {
                "event": event.strip().capitalize(),
                "adopter_id": adopter_id.strip(),
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
        )

    def to_dict(self) -> dict:
        """Serialize this animal, including its concrete subclass type."""
        return {
            "animal_type": type(self).__name__,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "breed": self.breed,
            "animal_id": self.animal_id,
            "adopted": self.adopted,
            "adopter_id": self.adopter_id,
            "health_records": deepcopy(self.health_records),
            "adoption_history": deepcopy(self.adoption_history),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Animal":
        """Rebuild the correct Animal subclass from serialized data."""
        if not isinstance(data, dict):
            raise TypeError("Animal data must be a dictionary")

        animal_classes = {
            "Animal": Animal,
            "Dog": Dog,
            "Cat": Cat,
            "Bird": Bird,
            "Horse": Horse,
        }
        animal_type = data.get("animal_type", cls.__name__)
        if not isinstance(animal_type, str):
            raise ValueError("Invalid animal type")

        animal_class = animal_classes.get(animal_type)
        if animal_class is None:
            raise ValueError(f"Unknown animal type: {animal_type}")

        if cls is not Animal and not issubclass(animal_class, cls):
            raise ValueError("Animal type mismatch")

        return animal_class(
            name=data["name"],
            age=data["age"],
            gender=data["gender"],
            breed=data["breed"],
            animal_id=data.get("animal_id"),
            adopted=data.get("adopted", False),
            adopter_id=data.get("adopter_id"),
            health_records=data.get("health_records", []),
            adoption_history=data.get("adoption_history", []),
        )

    def make_sound(self) -> str:
        """Return a generic animal sound."""
        return "Animal makes a sound"


class Dog(Animal):
    """Represent a dog."""

    def make_sound(self) -> str:
        return "Woof! Woof!"


class Cat(Animal):
    """Represent a cat."""

    def make_sound(self) -> str:
        return "Meow! Meow!"


class Bird(Animal):
    """Represent a bird."""

    def make_sound(self) -> str:
        return "Chirp! Chirp!"


class Horse(Animal):
    """Represent a horse, the additional animal species selected for this project."""

    def make_sound(self) -> str:
        return "Neigh! Neigh!"
