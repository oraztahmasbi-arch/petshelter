import logging
from pathlib import Path

from animals import Dog, Cat, Bird, Horse
from people import Adopter
from shelter import Shelter
from storage import JSONStorage
from reports import ShelterReports
from exceptions import (
    AnimalNotFoundError,
    DuplicateAnimalError,
    AnimalAlreadyAdoptedError,
    MaximumAdoptionReachedError,
    AdopterNotFoundError,
    DuplicateAdopterError,
    StorageError,
)


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "database.json"
LOG_PATH = BASE_DIR / "logs" / "shelter.log"
logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure console and file logging."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )


def get_non_empty_input(message: str) -> str:
    """Prompt until the user enters a non-empty value."""
    while True:
        value = input(message).strip()
        if value:
            return value
        print("Input cannot be empty. Please try again.")


def get_integer_input(message: str, minimum: int | None = None) -> int | None:
    """Read an integer and return None for invalid or out-of-range input."""
    raw_value = input(message).strip()
    try:
        value = int(raw_value)
    except ValueError:
        print("Please enter a valid integer.")
        return None
    if minimum is not None and value < minimum:
        print(f"Value must be at least {minimum}.")
        return None
    return value


def confirm_action(message: str) -> bool:
    """Ask the user to confirm a potentially destructive operation."""
    return input(f"{message} (y/n): ").strip().casefold() == "y"


def show_main_menu() -> str:
    print("\n" + "=" * 50)
    print("          PET SHELTER MANAGEMENT SYSTEM")
    print("=" * 50)
    print("1. Animal Management")
    print("2. Adopter Management")
    print("3. Adoption Management")
    print("4. Health Records")
    print("5. Reports & Statistics")
    print("6. Exit")
    print("=" * 50)
    return input("Select an option (1-6): ").strip()


# -------------------- Animal management --------------------

def show_animal_menu() -> str:
    print("\n" + "=" * 45)
    print("             ANIMAL MANAGEMENT")
    print("=" * 45)
    print("1. Register New Animal")
    print("2. Remove Animal")
    print("3. Search Animal by Name")
    print("4. Search Animals by Species")
    print("5. Show All Animals")
    print("6. Show Available Animals")
    print("7. Show Adopted Animals")
    print("8. Back to Main Menu")
    print("=" * 45)
    return input("Select an option (1-8): ").strip()


def display_animal_results(animals) -> None:
    ShelterReports.display_animals(animals)


def register_animal(shelter: Shelter) -> None:
    print("\nSELECT ANIMAL SPECIES")
    print("1. Dog")
    print("2. Cat")
    print("3. Bird")
    print("4. Horse")
    animal_types = {"1": Dog, "2": Cat, "3": Bird, "4": Horse}
    animal_class = animal_types.get(input("Select species (1-4): ").strip())
    if animal_class is None:
        print("Invalid species selection.")
        return

    name = get_non_empty_input("Enter animal name: ")
    age = get_integer_input("Enter animal age: ", minimum=0)
    if age is None:
        return
    gender = get_non_empty_input("Enter gender (Male/Female): ")
    breed = get_non_empty_input("Enter animal breed: ")

    try:
        animal = animal_class(name=name, age=age, gender=gender, breed=breed)
        shelter.add_animal(animal)
    except (ValueError, TypeError, DuplicateAnimalError, StorageError) as error:
        print(f"Registration failed: {error}")
        return

    print("\nAnimal registered successfully!")
    animal.show_info()


def remove_animal_cli(shelter: Shelter) -> None:
    animal_id = get_non_empty_input("Enter animal ID: ")
    try:
        animal = shelter.get_animal(animal_id)
        if not confirm_action(f"Remove {animal.name}"):
            print("Operation cancelled.")
            return
        shelter.remove_animal(animal_id)
    except (AnimalNotFoundError, ValueError, StorageError) as error:
        print(f"Removal failed: {error}")
    else:
        print("Animal removed successfully!")


def search_animal_by_name(shelter: Shelter) -> None:
    name = get_non_empty_input("Enter animal name: ")
    try:
        display_animal_results(shelter.search_animals_by_name(name))
    except (TypeError, ValueError) as error:
        print(f"Search failed: {error}")


def search_animals_by_species(shelter: Shelter) -> None:
    print("\n1. Dog\n2. Cat\n3. Bird\n4. Horse")
    species_types = {"1": Dog, "2": Cat, "3": Bird, "4": Horse}
    species = species_types.get(input("Select species (1-4): ").strip())
    if species is None:
        print("Invalid species selection.")
        return
    display_animal_results(shelter.search_animals_by_species(species))


def animal_management_menu(shelter: Shelter) -> None:
    while True:
        choice = show_animal_menu()
        if choice == "1":
            register_animal(shelter)
        elif choice == "2":
            remove_animal_cli(shelter)
        elif choice == "3":
            search_animal_by_name(shelter)
        elif choice == "4":
            search_animals_by_species(shelter)
        elif choice == "5":
            shelter.show_animals()
        elif choice == "6":
            shelter.show_available_animals()
        elif choice == "7":
            shelter.show_adopted_animals()
        elif choice == "8":
            return
        else:
            print("Invalid choice!")


# -------------------- Adopter management --------------------

def show_adopter_menu() -> str:
    print("\n" + "=" * 45)
    print("             ADOPTER MANAGEMENT")
    print("=" * 45)
    print("1. Register New Adopter")
    print("2. Show All Adopters")
    print("3. Search Adopter by ID")
    print("4. Remove Adopter")
    print("5. Back to Main Menu")
    print("=" * 45)
    return input("Select an option (1-5): ").strip()


def register_adopter(shelter: Shelter) -> Adopter | None:
    print("\nREGISTER NEW ADOPTER")
    name = get_non_empty_input("Enter full name: ")
    phone = get_non_empty_input("Enter phone number (09xxxxxxxxx): ")
    national_id = get_non_empty_input("Enter national ID (10 digits): ")
    try:
        adopter = Adopter(name=name, phone=phone, national_id=national_id)
        shelter.add_adopter(adopter)
    except (ValueError, TypeError, DuplicateAdopterError, StorageError) as error:
        print(f"Adopter registration failed: {error}")
        return None
    print(f"Adopter registered successfully. ID: {adopter.adopter_id}")
    return adopter


def show_all_adopters(shelter: Shelter) -> None:
    if not shelter.adopters:
        print("No adopters registered.")
        return
    for index, adopter in enumerate(shelter.adopters.values(), start=1):
        print("\n" + "-" * 42)
        print(f"Adopter #{index}")
        print(f"ID: {adopter.adopter_id}")
        print(f"Name: {adopter.name}")
        print(f"Phone: {adopter.phone}")
        print(f"National ID: {adopter.national_id}")
        print(f"Active adoptions: {len(adopter.adopted_animals)}")
        print(f"Animal IDs: {', '.join(adopter.adopted_animals) or 'None'}")
    print("-" * 42)


def search_adopter(shelter: Shelter) -> None:
    adopter_id = get_non_empty_input("Enter adopter ID: ")
    try:
        adopter = shelter.get_adopter(adopter_id)
    except (AdopterNotFoundError, ValueError) as error:
        print(error)
        return
    print(f"\nID: {adopter.adopter_id}")
    print(f"Name: {adopter.name}")
    print(f"Phone: {adopter.phone}")
    print(f"National ID: {adopter.national_id}")
    print(f"Adopted animals: {adopter.adopted_animals}")


def remove_adopter_cli(shelter: Shelter) -> None:
    adopter_id = get_non_empty_input("Enter adopter ID: ")
    try:
        adopter = shelter.get_adopter(adopter_id)
        if not confirm_action(f"Remove adopter {adopter.name}"):
            print("Operation cancelled.")
            return
        shelter.remove_adopter(adopter_id)
    except (AdopterNotFoundError, ValueError, StorageError) as error:
        print(f"Adopter removal failed: {error}")
    else:
        print("Adopter removed successfully!")


def adopter_management_menu(shelter: Shelter) -> None:
    while True:
        choice = show_adopter_menu()
        if choice == "1":
            register_adopter(shelter)
        elif choice == "2":
            show_all_adopters(shelter)
        elif choice == "3":
            search_adopter(shelter)
        elif choice == "4":
            remove_adopter_cli(shelter)
        elif choice == "5":
            return
        else:
            print("Invalid choice!")


# -------------------- Adoption management --------------------

def show_adoption_menu() -> str:
    print("\n" + "=" * 45)
    print("             ADOPTION MANAGEMENT")
    print("=" * 45)
    print("1. Adopt Animal")
    print("2. Return Animal")
    print("3. Show Animal Adoption History")
    print("4. Back to Main Menu")
    print("=" * 45)
    return input("Select an option (1-4): ").strip()


def adopt_animal_cli(shelter: Shelter) -> None:
    animal_id = get_non_empty_input("Enter animal ID: ")
    try:
        animal = shelter.get_animal(animal_id)
    except (AnimalNotFoundError, ValueError) as error:
        print(error)
        return
    if animal.adopted:
        print("This animal has already been adopted.")
        return

    print("\n1. Existing Adopter")
    print("2. Register New Adopter")
    choice = input("Select an option (1-2): ").strip()

    if choice == "1":
        adopter_id = get_non_empty_input("Enter adopter ID: ")
    elif choice == "2":
        adopter = register_adopter(shelter)
        if adopter is None:
            return
        adopter_id = adopter.adopter_id
    else:
        print("Invalid choice.")
        return

    try:
        shelter.adopt_animal(animal_id=animal_id, adopter_id=adopter_id)
    except AnimalNotFoundError:
        print("Animal not found.")
    except AdopterNotFoundError:
        print("Adopter not found.")
    except AnimalAlreadyAdoptedError:
        print("Animal has already been adopted.")
    except MaximumAdoptionReachedError:
        print("Maximum adoption limit reached (9 animals).")
    except (ValueError, TypeError, StorageError) as error:
        print(f"Adoption failed: {error}")
    else:
        print("Animal adopted successfully!")


def return_animal_cli(shelter: Shelter) -> None:
    animal_id = get_non_empty_input("Enter animal ID: ")
    try:
        shelter.return_animal(animal_id)
    except (AnimalNotFoundError, AdopterNotFoundError, ValueError, StorageError) as error:
        print(f"Return failed: {error}")
    else:
        print("Animal returned successfully!")


def show_adoption_history_cli(reports: ShelterReports) -> None:
    animal_id = get_non_empty_input("Enter animal ID: ")
    try:
        reports.show_animal_history(animal_id)
    except (AnimalNotFoundError, ValueError) as error:
        print(f"Unable to display history: {error}")


def adoption_management_menu(shelter: Shelter, reports: ShelterReports) -> None:
    while True:
        choice = show_adoption_menu()
        if choice == "1":
            adopt_animal_cli(shelter)
        elif choice == "2":
            return_animal_cli(shelter)
        elif choice == "3":
            show_adoption_history_cli(reports)
        elif choice == "4":
            return
        else:
            print("Invalid choice!")


# -------------------- Health records --------------------

def show_health_menu() -> str:
    print("\n" + "=" * 45)
    print("                HEALTH RECORDS")
    print("=" * 45)
    print("1. Add Health Record")
    print("2. Show Health Records")
    print("3. Back to Main Menu")
    print("=" * 45)
    return input("Select an option (1-3): ").strip()


def add_health_record_cli(shelter: Shelter) -> None:
    animal_id = get_non_empty_input("Enter animal ID: ")
    record_type = get_non_empty_input(
        "Enter record type (vaccination/checkup/treatment/other): "
    )
    description = get_non_empty_input("Enter medical description: ")
    try:
        shelter.add_health_record(animal_id, record_type, description)
    except (AnimalNotFoundError, ValueError, TypeError, StorageError) as error:
        print(f"Health record registration failed: {error}")
    else:
        print("Health record added successfully!")


def show_health_records_cli(shelter: Shelter) -> None:
    animal_id = get_non_empty_input("Enter animal ID: ")
    try:
        shelter.show_animal_health_records(animal_id)
    except (AnimalNotFoundError, ValueError) as error:
        print(f"Unable to display health records: {error}")


def health_records_menu(shelter: Shelter) -> None:
    while True:
        choice = show_health_menu()
        if choice == "1":
            add_health_record_cli(shelter)
        elif choice == "2":
            show_health_records_cli(shelter)
        elif choice == "3":
            return
        else:
            print("Invalid choice!")


# -------------------- Reports and statistics --------------------

def show_reports_menu() -> str:
    print("\n" + "=" * 45)
    print("             REPORTS & STATISTICS")
    print("=" * 45)
    print("1. Show Summary")
    print("2. Show Detailed Statistics")
    print("3. Filter Animals")
    print("4. Sort Animals")
    print("5. Show Animal Adoption Count")
    print("6. Show Latest Animal Event")
    print("7. Back to Main Menu")
    print("=" * 45)
    return input("Select an option (1-7): ").strip()


def filter_animals_cli(reports: ShelterReports) -> None:
    print("\nLeave an optional field blank to skip that filter.")
    min_age_raw = input("Minimum age: ").strip()
    max_age_raw = input("Maximum age: ").strip()
    gender = input("Gender (Male/Female): ").strip() or None
    breed = input("Breed: ").strip() or None
    species_raw = input("Species (dog/cat/bird/horse/blank): ").strip().casefold()
    adopted_raw = input("Adoption status (yes/no/blank): ").strip().casefold()
    species_options = {
        "dog": Dog,
        "cat": Cat,
        "bird": Bird,
        "horse": Horse,
    }

    try:
        min_age = int(min_age_raw) if min_age_raw else None
        max_age = int(max_age_raw) if max_age_raw else None
        if species_raw and species_raw not in species_options:
            raise ValueError("Unknown species")
        if adopted_raw not in {"", "yes", "no"}:
            raise ValueError("Adoption status must be yes, no, or blank")
        adopted = True if adopted_raw == "yes" else False if adopted_raw == "no" else None
        results = reports.filter_animals(
            min_age=min_age,
            max_age=max_age,
            gender=gender,
            breed=breed,
            species=species_options.get(species_raw) if species_raw else None,
            adopted=adopted,
        )
    except (ValueError, TypeError) as error:
        print(f"Filter failed: {error}")
        return
    reports.display_animals(results)


def sort_animals_cli(reports: ShelterReports) -> None:
    print("\nSort by: name / age / breed / gender")
    sort_by = input("Sort field: ").strip().casefold()
    descending_raw = input("Descending? (y/n): ").strip().casefold()
    if descending_raw not in {"y", "n"}:
        print("Please enter y or n.")
        return
    try:
        results = reports.sort_animals(sort_by, descending=(descending_raw == "y"))
    except (ValueError, TypeError) as error:
        print(f"Sorting failed: {error}")
        return
    reports.display_animals(results)


def show_adoption_count_cli(reports: ShelterReports) -> None:
    animal_id = get_non_empty_input("Enter animal ID: ")
    try:
        count = reports.get_adoption_count(animal_id)
    except (AnimalNotFoundError, ValueError) as error:
        print(f"Unable to retrieve adoption count: {error}")
    else:
        print(f"Total successful adoptions: {count}")


def show_latest_event_cli(reports: ShelterReports) -> None:
    animal_id = get_non_empty_input("Enter animal ID: ")
    try:
        event = reports.get_latest_event(animal_id)
    except (AnimalNotFoundError, ValueError) as error:
        print(f"Unable to retrieve event: {error}")
        return
    if event is None:
        print("No adoption history available.")
        return
    print("\nLATEST EVENT")
    print(f"Event: {event['event']}")
    print(f"Adopter ID: {event['adopter_id']}")
    print(f"Timestamp: {event['timestamp']}")


def reports_management_menu(reports: ShelterReports) -> None:
    while True:
        choice = show_reports_menu()
        if choice == "1":
            reports.show_summary()
        elif choice == "2":
            reports.show_detailed_stats()
        elif choice == "3":
            filter_animals_cli(reports)
        elif choice == "4":
            sort_animals_cli(reports)
        elif choice == "5":
            show_adoption_count_cli(reports)
        elif choice == "6":
            show_latest_event_cli(reports)
        elif choice == "7":
            return
        else:
            print("Invalid choice!")


# -------------------- Application entry point --------------------

def main() -> None:
    """Load the database and run the interactive CLI."""
    try:
        shelter = Shelter(storage=JSONStorage(DB_PATH), autosave=True)
    except StorageError as error:
        logger.exception("Could not initialize the shelter database")
        print(f"Could not load the database: {error}")
        return

    reports = ShelterReports(shelter)
    print("\nWelcome to Pet Shelter Management System!")

    try:
        while True:
            choice = show_main_menu()
            try:
                if choice == "1":
                    animal_management_menu(shelter)
                elif choice == "2":
                    adopter_management_menu(shelter)
                elif choice == "3":
                    adoption_management_menu(shelter, reports)
                elif choice == "4":
                    health_records_menu(shelter)
                elif choice == "5":
                    reports_management_menu(reports)
                elif choice == "6":
                    shelter.save()
                    print("\nThank you for using Pet Shelter!")
                    print("Goodbye!")
                    break
                else:
                    print("Invalid choice! Please select 1-6.")
            except StorageError as error:
                logger.exception("Storage operation failed")
                print(f"Storage error: {error}")
            except (KeyboardInterrupt, EOFError):
                raise
            except Exception:
                logger.exception("Unexpected application error")
                print("An unexpected error occurred. Please try again.")
    except (KeyboardInterrupt, EOFError):
        print("\nApplication interrupted. Saving current data...")
        try:
            shelter.save()
            print("Data saved. Goodbye!")
        except StorageError:
            logger.exception("Could not save data during shutdown")
            print("Warning: the latest changes could not be saved.")


if __name__ == "__main__":
    configure_logging()
    main()
