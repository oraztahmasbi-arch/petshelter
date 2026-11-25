from typing import Optional

from animals import Animal
from people import Adopter
from decorators import log_operation, execution_time
from exceptions import (
    AnimalNotFoundError,
    DuplicateAnimalError,
    AnimalAlreadyAdoptedError,
    MaximumAdoptionReachedError,
    AdopterNotFoundError,
    DuplicateAdopterError,
)


class Shelter:
    """Coordinate animal, adopter, adoption, health, and storage operations."""

    MAX_ADOPTIONS_PER_ADOPTER = 9

    def __init__(self, storage=None, autosave: bool = True) -> None:
        self.animals: dict[str, Animal] = {}
        self.adopters: dict[str, Adopter] = {}
        self.storage = storage
        self.autosave = autosave

        if self.storage is not None:
            self.animals, self.adopters = self.storage.load()

    def save(self) -> None:
        """Persist the current shelter state when storage is configured."""
        if self.storage is not None:
            self.storage.save(self.animals, self.adopters)

    def _save_if_enabled(self) -> None:
        if self.autosave:
            self.save()

    def get_animal(self, animal_id: str) -> Animal:
        """Return an animal by ID or raise AnimalNotFoundError."""
        if not isinstance(animal_id, str) or not animal_id.strip():
            raise ValueError("Invalid animal ID")
        animal = self.animals.get(animal_id.strip())
        if animal is None:
            raise AnimalNotFoundError("Animal not found")
        return animal

    def get_adopter(self, adopter_id: str) -> Adopter:
        """Return an adopter by ID or raise AdopterNotFoundError."""
        if not isinstance(adopter_id, str) or not adopter_id.strip():
            raise ValueError("Invalid adopter ID")
        adopter = self.adopters.get(adopter_id.strip())
        if adopter is None:
            raise AdopterNotFoundError("Adopter not found")
        return adopter

    @log_operation
    @execution_time
    def add_animal(self, animal: Animal) -> None:
        """Register a new, currently available animal."""
        if not isinstance(animal, Animal):
            raise TypeError("Invalid animal object")
        if animal.animal_id in self.animals:
            raise DuplicateAnimalError("Animal already exists")
        if animal.adopted or animal.adopter_id is not None:
            raise ValueError("A newly registered animal must be available")

        self.animals[animal.animal_id] = animal
        try:
            self._save_if_enabled()
        except Exception:
            self.animals.pop(animal.animal_id, None)
            raise

    @log_operation
    @execution_time
    def remove_animal(self, animal_id: str) -> None:
        """Remove an available animal that is not linked to an adopter."""
        animal = self.get_animal(animal_id)
        if animal.adopted or animal.adopter_id is not None:
            raise ValueError("Cannot remove an adopted animal")

        for adopter in self.adopters.values():
            if animal.animal_id in adopter.adopted_animals:
                raise ValueError("Adoption records are inconsistent")

        del self.animals[animal.animal_id]
        try:
            self._save_if_enabled()
        except Exception:
            self.animals[animal.animal_id] = animal
            raise

    def search_animals_by_name(self, name: str) -> list[Animal]:
        """Find all animals whose names match, ignoring case."""
        if not isinstance(name, str):
            raise TypeError("Animal name must be a string")
        normalized = name.strip().casefold()
        if not normalized:
            raise ValueError("Search name cannot be empty")
        return [
            animal for animal in self.animals.values()
            if animal.name.casefold() == normalized
        ]

    def search_animals_by_species(self, species: type[Animal]) -> list[Animal]:
        """Find animals that are instances of the requested Animal subclass."""
        if not isinstance(species, type) or not issubclass(species, Animal):
            raise TypeError("Invalid animal species")
        return [
            animal for animal in self.animals.values()
            if isinstance(animal, species)
        ]

    def show_animals(self) -> None:
        """Display every registered animal."""
        self._display_animals(self.animals.values(), "No animals registered.")

    def show_available_animals(self) -> None:
        """Display animals that can currently be adopted."""
        available = [animal for animal in self.animals.values() if not animal.adopted]
        self._display_animals(available, "No available animals.")

    def show_adopted_animals(self) -> None:
        """Display animals that are currently adopted."""
        adopted = [animal for animal in self.animals.values() if animal.adopted]
        self._display_animals(adopted, "No adopted animals.")

    @staticmethod
    def _display_animals(animals, empty_message: str) -> None:
        animals = list(animals)
        if not animals:
            print(empty_message)
            return
        for animal in animals:
            animal.show_info()

    @log_operation
    @execution_time
    def add_adopter(self, adopter: Adopter) -> None:
        """Register an adopter and enforce unique IDs and national IDs."""
        if not isinstance(adopter, Adopter):
            raise TypeError("Invalid adopter object")
        if adopter.adopter_id in self.adopters:
            raise DuplicateAdopterError("Adopter ID already exists")
        if any(
            existing.national_id == adopter.national_id
            for existing in self.adopters.values()
        ):
            raise DuplicateAdopterError("National ID is already registered")
        if adopter.adopted_animals:
            raise ValueError("A newly registered adopter cannot have existing animals")

        self.adopters[adopter.adopter_id] = adopter
        try:
            self._save_if_enabled()
        except Exception:
            self.adopters.pop(adopter.adopter_id, None)
            raise

    @log_operation
    @execution_time
    def remove_adopter(self, adopter_id: str) -> None:
        """Remove an adopter only when they have no active adoptions."""
        adopter = self.get_adopter(adopter_id)
        if adopter.adopted_animals:
            raise ValueError("Cannot remove an adopter with adopted animals")

        del self.adopters[adopter.adopter_id]
        try:
            self._save_if_enabled()
        except Exception:
            self.adopters[adopter.adopter_id] = adopter
            raise

    @log_operation
    @execution_time
    def adopt_animal(self, animal_id: str, adopter_id: str) -> None:
        """Adopt an available animal and update both sides of the relationship."""
        animal = self.get_animal(animal_id)
        adopter = self.get_adopter(adopter_id)

        if animal.adopted or animal.adopter_id is not None:
            raise AnimalAlreadyAdoptedError("Animal already adopted")
        if not isinstance(adopter.adopted_animals, list):
            raise ValueError("Invalid adopter records")
        if animal.animal_id in adopter.adopted_animals:
            raise ValueError("Adoption records are inconsistent")
        if any(
            animal.animal_id in other.adopted_animals
            for other in self.adopters.values()
        ):
            raise ValueError("Adoption records are inconsistent")
        if len(adopter.adopted_animals) >= self.MAX_ADOPTIONS_PER_ADOPTER:
            raise MaximumAdoptionReachedError(
                "Adopter has reached the maximum adoption limit"
            )

        animal.add_adoption_event("adopted", adopter.adopter_id)
        animal.adopted = True
        animal.adopter_id = adopter.adopter_id
        adopter.adopted_animals.append(animal.animal_id)

        try:
            self._save_if_enabled()
        except Exception:
            adopter.adopted_animals.remove(animal.animal_id)
            animal.adopted = False
            animal.adopter_id = None
            animal.adoption_history.pop()
            raise

    @log_operation
    @execution_time
    def return_animal(self, animal_id: str) -> None:
        """Return an adopted animal and preserve its historical adoption event."""
        animal = self.get_animal(animal_id)

        if animal.adopted != (animal.adopter_id is not None):
            raise ValueError("Animal adoption data is inconsistent")
        if not animal.adopted:
            raise ValueError("Animal is not currently adopted")

        adopter = self.get_adopter(animal.adopter_id)
        occurrences = sum(
            other.adopted_animals.count(animal.animal_id)
            for other in self.adopters.values()
        )
        if occurrences != 1 or adopter.adopted_animals.count(animal.animal_id) != 1:
            raise ValueError("Adoption records are inconsistent")

        previous_adopter_id = adopter.adopter_id
        animal.add_adoption_event("returned", previous_adopter_id)
        adopter.adopted_animals.remove(animal.animal_id)
        animal.adopted = False
        animal.adopter_id = None

        try:
            self._save_if_enabled()
        except Exception:
            animal.adopted = True
            animal.adopter_id = previous_adopter_id
            adopter.adopted_animals.append(animal.animal_id)
            animal.adoption_history.pop()
            raise

    @log_operation
    @execution_time
    def add_health_record(
        self,
        animal_id: str,
        record_type: str,
        description: str,
    ) -> None:
        """Add a timestamped health record to an animal."""
        animal = self.get_animal(animal_id)
        animal.add_health_record(record_type, description)
        try:
            self._save_if_enabled()
        except Exception:
            animal.health_records.pop()
            raise

    def show_animal_health_records(self, animal_id: str) -> None:
        """Print all health records for an animal."""
        animal = self.get_animal(animal_id)
        if not animal.health_records:
            print("No health records found.")
            return

        print("\n" + "=" * 48)
        print(f"HEALTH RECORDS: {animal.name}")
        print("=" * 48)
        for index, record in enumerate(animal.health_records, start=1):
            print(f"\nRecord #{index}")
            print(f"Type: {record['record_type']}")
            print(f"Description: {record['description']}")
            print(f"Date: {record['timestamp']}")
        print("=" * 48)
