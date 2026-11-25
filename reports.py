from copy import deepcopy
from statistics import mean

from animals import Animal
from exceptions import AnimalNotFoundError


class ShelterReports:
    """Provide summaries, filtering, sorting, and adoption-history reports."""

    def __init__(self, shelter) -> None:
        self.shelter = shelter

    def get_summary(self) -> dict:
        """Return the main shelter totals and species distribution."""
        animals = list(self.shelter.animals.values())
        total = len(animals)
        adopted = sum(animal.adopted for animal in animals)
        species_counts: dict[str, int] = {}

        for animal in animals:
            species = type(animal).__name__
            species_counts[species] = species_counts.get(species, 0) + 1

        total_adoption_events = sum(
            event["event"].casefold() == "adopted"
            for animal in animals
            for event in animal.adoption_history
        )

        return {
            "total_animals": total,
            "adopted_animals": adopted,
            "available_animals": total - adopted,
            "total_adopters": len(self.shelter.adopters),
            "species_counts": species_counts,
            "total_adoption_events": total_adoption_events,
        }

    def show_summary(self) -> None:
        """Print the main shelter summary."""
        summary = self.get_summary()
        print("\n" + "=" * 46)
        print("PET SHELTER SUMMARY")
        print("=" * 46)
        print(f"Total Animals: {summary['total_animals']}")
        print(f"Adopted Animals: {summary['adopted_animals']}")
        print(f"Available Animals: {summary['available_animals']}")
        print(f"Total Adopters: {summary['total_adopters']}")
        print(f"Historical Adoptions: {summary['total_adoption_events']}")
        print("\nAnimals by Species:")
        if summary["species_counts"]:
            for species, count in sorted(summary["species_counts"].items()):
                print(f"{species}: {count}")
        else:
            print("No animals registered.")
        print("=" * 46)

    def filter_animals(
        self,
        min_age: int | None = None,
        max_age: int | None = None,
        gender: str | None = None,
        breed: str | None = None,
        species: type[Animal] | None = None,
        adopted: bool | None = None,
    ) -> list[Animal]:
        """Filter animals by one or more optional attributes."""
        if min_age is not None and not Animal.is_valid_age(min_age):
            raise ValueError("Invalid minimum age")
        if max_age is not None and not Animal.is_valid_age(max_age):
            raise ValueError("Invalid maximum age")
        if min_age is not None and max_age is not None and min_age > max_age:
            raise ValueError("Minimum age cannot exceed maximum age")
        if gender is not None and not Animal.is_valid_gender(gender):
            raise ValueError("Invalid gender")
        if breed is not None and (
            not isinstance(breed, str) or not breed.strip()
        ):
            raise ValueError("Invalid breed")
        if species is not None and (
            not isinstance(species, type) or not issubclass(species, Animal)
        ):
            raise TypeError("Invalid animal species")
        if adopted is not None and not isinstance(adopted, bool):
            raise TypeError("Adopted must be a boolean")

        results = []
        for animal in self.shelter.animals.values():
            if min_age is not None and animal.age < min_age:
                continue
            if max_age is not None and animal.age > max_age:
                continue
            if gender is not None and animal.gender.casefold() != gender.strip().casefold():
                continue
            if breed is not None and animal.breed.casefold() != breed.strip().casefold():
                continue
            if species is not None and not isinstance(animal, species):
                continue
            if adopted is not None and animal.adopted != adopted:
                continue
            results.append(animal)
        return results

    def sort_animals(
        self,
        sort_by: str = "name",
        descending: bool = False,
    ) -> list[Animal]:
        """Return animals sorted by name, age, breed, or gender."""
        sort_options = {
            "name": lambda animal: animal.name.casefold(),
            "age": lambda animal: animal.age,
            "breed": lambda animal: animal.breed.casefold(),
            "gender": lambda animal: animal.gender.casefold(),
        }
        if not isinstance(sort_by, str) or sort_by not in sort_options:
            raise ValueError("Invalid sorting option")
        if not isinstance(descending, bool):
            raise TypeError("Descending must be a boolean")
        return sorted(
            self.shelter.animals.values(),
            key=sort_options[sort_by],
            reverse=descending,
        )

    @staticmethod
    def display_animals(animals: list[Animal]) -> None:
        """Display a list of animals."""
        if not animals:
            print("No animals found.")
            return
        print(f"\nFound {len(animals)} animal(s):")
        for index, animal in enumerate(animals, start=1):
            print(f"\nAnimal #{index}")
            animal.show_info()

    def get_detailed_stats(self) -> dict:
        """Calculate age, gender, and adoption percentages."""
        animals = list(self.shelter.animals.values())
        total = len(animals)
        adopted = sum(animal.adopted for animal in animals)
        available = total - adopted

        gender_counts: dict[str, int] = {}
        for animal in animals:
            gender_counts[animal.gender] = gender_counts.get(animal.gender, 0) + 1

        average_age = mean(animal.age for animal in animals) if total else 0
        return {
            "average_age": round(average_age, 2),
            "gender_counts": gender_counts,
            "adopted_percentage": round(adopted / total * 100, 2) if total else 0,
            "available_percentage": round(available / total * 100, 2) if total else 0,
        }

    def show_detailed_stats(self) -> None:
        """Print detailed shelter statistics."""
        stats = self.get_detailed_stats()
        print("\n" + "=" * 46)
        print("DETAILED SHELTER STATISTICS")
        print("=" * 46)
        print(f"Average Age: {stats['average_age']}")
        print("\nGender Distribution:")
        if stats["gender_counts"]:
            for gender, count in sorted(stats["gender_counts"].items()):
                print(f"{gender}: {count}")
        else:
            print("No animal data.")
        print("\nAdoption Statistics:")
        print(f"Adopted: {stats['adopted_percentage']}%")
        print(f"Available: {stats['available_percentage']}%")
        print("=" * 46)

    def get_animal_history(self, animal_id: str) -> list[dict]:
        """Return a defensive copy of an animal's adoption history."""
        if not isinstance(animal_id, str) or not animal_id.strip():
            raise ValueError("Invalid animal ID")
        animal = self.shelter.animals.get(animal_id.strip())
        if animal is None:
            raise AnimalNotFoundError("Animal not found")
        return deepcopy(animal.adoption_history)

    def show_animal_history(self, animal_id: str) -> None:
        """Print an animal's full adoption and return history."""
        history = self.get_animal_history(animal_id)
        if not history:
            print("No adoption history found.")
            return

        print("\n" + "=" * 46)
        print("ANIMAL ADOPTION HISTORY")
        print("=" * 46)
        for index, event in enumerate(history, start=1):
            print(f"\nEvent #{index}")
            print(f"Event: {event['event']}")
            print(f"Adopter ID: {event['adopter_id']}")
            print(f"Date: {event['timestamp']}")
        print("=" * 46)

    def get_adoption_count(self, animal_id: str) -> int:
        """Return the lifetime number of successful adoptions for an animal."""
        history = self.get_animal_history(animal_id)
        return sum(event["event"].casefold() == "adopted" for event in history)

    def get_latest_event(self, animal_id: str) -> dict | None:
        """Return the most recent history event, or None when there is no history."""
        history = self.get_animal_history(animal_id)
        return history[-1] if history else None
