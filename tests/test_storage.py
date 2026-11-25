import json
import tempfile
import unittest
from pathlib import Path

from animals import Dog
from people import Adopter
from shelter import Shelter
from storage import JSONStorage
from exceptions import StorageError


class StorageTests(unittest.TestCase):
    def test_missing_file_returns_empty_collections(self):
        with tempfile.TemporaryDirectory() as folder:
            storage = JSONStorage(Path(folder) / "missing.json")
            self.assertEqual(storage.load(), ({}, {}))

    def test_round_trip_preserves_animals_adopters_and_history(self):
        with tempfile.TemporaryDirectory() as folder:
            storage = JSONStorage(Path(folder) / "database.json")
            shelter = Shelter(storage=storage)
            dog = Dog("Max", 4, "male", "Labrador")
            adopter = Adopter("Ali", "09123456789", "1234567890")
            shelter.add_animal(dog)
            shelter.add_adopter(adopter)
            shelter.add_health_record(dog.animal_id, "Vaccination", "Rabies")
            shelter.adopt_animal(dog.animal_id, adopter.adopter_id)
            shelter.return_animal(dog.animal_id)

            loaded_animals, loaded_adopters = storage.load()
            loaded_dog = loaded_animals[dog.animal_id]
            loaded_adopter = loaded_adopters[adopter.adopter_id]

            self.assertIsInstance(loaded_dog, Dog)
            self.assertEqual(len(loaded_dog.health_records), 1)
            self.assertEqual(
                [item["event"] for item in loaded_dog.adoption_history],
                ["Adopted", "Returned"],
            )
            self.assertFalse(loaded_dog.adopted)
            self.assertEqual(loaded_adopter.adopted_animals, [])


    def test_round_trip_preserves_current_active_adoption(self):
        with tempfile.TemporaryDirectory() as folder:
            storage = JSONStorage(Path(folder) / "database.json")
            shelter = Shelter(storage=storage)
            dog = Dog("Rex", 2, "male", "Mixed")
            adopter = Adopter("Sara", "09111111111", "1234567891")
            shelter.add_animal(dog)
            shelter.add_adopter(adopter)
            shelter.adopt_animal(dog.animal_id, adopter.adopter_id)

            loaded_animals, loaded_adopters = storage.load()
            loaded_dog = loaded_animals[dog.animal_id]
            loaded_adopter = loaded_adopters[adopter.adopter_id]

            self.assertTrue(loaded_dog.adopted)
            self.assertEqual(loaded_dog.adopter_id, adopter.adopter_id)
            self.assertEqual(loaded_adopter.adopted_animals, [dog.animal_id])

    def test_invalid_json_raises_storage_error(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "database.json"
            path.write_text("{invalid", encoding="utf-8")
            with self.assertRaises(StorageError):
                JSONStorage(path).load()

    def test_inconsistent_adoption_records_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "database.json"
            data = {
                "schema_version": 1,
                "animals": [{
                    "animal_type": "Dog",
                    "name": "Max",
                    "age": 2,
                    "gender": "Male",
                    "breed": "Mixed",
                    "animal_id": "ANIMAL1",
                    "adopted": True,
                    "adopter_id": "ADOPTER1",
                    "health_records": [],
                    "adoption_history": [],
                }],
                "adopters": [{
                    "adopter_id": "ADOPTER1",
                    "name": "Ali",
                    "phone": "09123456789",
                    "national_id": "1234567890",
                    "adopted_animals": [],
                }],
            }
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(StorageError):
                JSONStorage(path).load()


if __name__ == "__main__":
    unittest.main()
