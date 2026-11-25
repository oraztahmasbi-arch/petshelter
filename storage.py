import json
import os
from pathlib import Path

from animals import Animal
from people import Adopter
from exceptions import StorageError


class JSONStorage:
    """Persist shelter animals and adopters in a validated JSON database."""

    SCHEMA_VERSION = 1

    def __init__(self, file_path: str | Path = "data/database.json") -> None:
        self.file_path = Path(file_path)

    @staticmethod
    def _validate_relationships(
        animals: dict[str, Animal],
        adopters: dict[str, Adopter],
    ) -> None:
        expected_by_adopter = {adopter_id: [] for adopter_id in adopters}

        for animal_id, animal in animals.items():
            if animal_id != animal.animal_id:
                raise ValueError("Animal dictionary key does not match its ID")
            if animal.adopted != (animal.adopter_id is not None):
                raise ValueError("Inconsistent animal adoption status")
            if animal.adopted:
                if animal.adopter_id not in adopters:
                    raise ValueError("Adopted animal references an unknown adopter")
                expected_by_adopter[animal.adopter_id].append(animal_id)

        national_ids = set()
        for adopter_id, adopter in adopters.items():
            if adopter_id != adopter.adopter_id:
                raise ValueError("Adopter dictionary key does not match its ID")
            if adopter.national_id in national_ids:
                raise ValueError("Duplicate national ID")
            national_ids.add(adopter.national_id)

            expected = expected_by_adopter[adopter_id]
            actual = adopter.adopted_animals
            if sorted(actual) != sorted(expected):
                raise ValueError("Animal/adopter adoption records are inconsistent")
            if len(actual) > 9:
                raise ValueError("Maximum adoption limit exceeded")

    def save(
        self,
        animals: dict[str, Animal],
        adopters: dict[str, Adopter],
    ) -> None:
        """Atomically write a consistent snapshot of the shelter to JSON."""
        temp_path = self.file_path.with_name(self.file_path.name + ".tmp")

        try:
            if not isinstance(animals, dict) or not isinstance(adopters, dict):
                raise TypeError("Animals and adopters must be dictionaries")
            if any(not isinstance(item, Animal) for item in animals.values()):
                raise TypeError("Invalid animal object in storage")
            if any(not isinstance(item, Adopter) for item in adopters.values()):
                raise TypeError("Invalid adopter object in storage")

            self._validate_relationships(animals, adopters)

            data = {
                "schema_version": self.SCHEMA_VERSION,
                "animals": [animal.to_dict() for animal in animals.values()],
                "adopters": [adopter.to_dict() for adopter in adopters.values()],
            }

            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                    allow_nan=False,
                )
                file.flush()
                os.fsync(file.fileno())

            temp_path.replace(self.file_path)

        except (OSError, TypeError, ValueError, KeyError) as error:
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise StorageError("Failed to save the shelter database") from error

    def load(self) -> tuple[dict[str, Animal], dict[str, Adopter]]:
        """Load and validate all records from JSON."""
        if not self.file_path.exists():
            return {}, {}

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise StorageError("Database contains invalid JSON") from error
        except OSError as error:
            raise StorageError("Could not read the shelter database") from error

        try:
            if not isinstance(data, dict):
                raise ValueError("Invalid database root")
            schema_version = data.get("schema_version")
            if type(schema_version) is not int or schema_version != self.SCHEMA_VERSION:
                raise ValueError("Unsupported database schema version")

            animals_data = data.get("animals")
            adopters_data = data.get("adopters")
            if not isinstance(animals_data, list) or not isinstance(adopters_data, list):
                raise ValueError("Invalid database record collections")

            loaded_adopters: dict[str, Adopter] = {}
            declared_adoptions: dict[str, list[str]] = {}
            national_ids = set()

            for adopter_data in adopters_data:
                adopter = Adopter.from_dict(adopter_data)
                if adopter.adopter_id in loaded_adopters:
                    raise ValueError("Duplicate adopter ID")
                if adopter.national_id in national_ids:
                    raise ValueError("Duplicate national ID")
                national_ids.add(adopter.national_id)
                declared_adoptions[adopter.adopter_id] = list(adopter.adopted_animals)
                adopter.adopted_animals.clear()
                loaded_adopters[adopter.adopter_id] = adopter

            loaded_animals: dict[str, Animal] = {}
            for animal_data in animals_data:
                animal = Animal.from_dict(animal_data)
                if animal.animal_id in loaded_animals:
                    raise ValueError("Duplicate animal ID")

                if animal.adopted:
                    adopter = loaded_adopters.get(animal.adopter_id)
                    if adopter is None:
                        raise ValueError("Adopted animal references an unknown adopter")
                    adopter.adopted_animals.append(animal.animal_id)

                loaded_animals[animal.animal_id] = animal

            for adopter_id, adopter in loaded_adopters.items():
                declared = declared_adoptions[adopter_id]
                rebuilt = adopter.adopted_animals
                if sorted(declared) != sorted(rebuilt):
                    raise ValueError("Stored adoption records are inconsistent")
                if len(rebuilt) > 9:
                    raise ValueError("Maximum adoption limit exceeded")

            self._validate_relationships(loaded_animals, loaded_adopters)
            return loaded_animals, loaded_adopters

        except (KeyError, TypeError, ValueError) as error:
            raise StorageError(
                "Database contains invalid or inconsistent records"
            ) from error
