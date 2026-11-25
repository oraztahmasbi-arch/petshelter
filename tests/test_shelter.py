import unittest

from animals import Dog, Cat
from people import Adopter
from shelter import Shelter
from exceptions import (
    AnimalNotFoundError,
    DuplicateAnimalError,
    AnimalAlreadyAdoptedError,
    MaximumAdoptionReachedError,
    DuplicateAdopterError,
)
from storage import JSONStorage
from exceptions import StorageError


class FailingStorage:
    def load(self):
        return {}, {}

    def save(self, animals, adopters):
        raise StorageError("simulated disk failure")


class ShelterTests(unittest.TestCase):
    def setUp(self):
        self.shelter = Shelter(autosave=False)
        self.dog = Dog("Max", 3, "male", "Labrador")
        self.adopter = Adopter("Ali", "09123456789", "1234567890")
        self.shelter.add_animal(self.dog)
        self.shelter.add_adopter(self.adopter)

    def test_add_duplicate_and_remove_animal(self):
        with self.assertRaises(DuplicateAnimalError):
            self.shelter.add_animal(self.dog)
        self.shelter.remove_animal(self.dog.animal_id)
        self.assertNotIn(self.dog.animal_id, self.shelter.animals)

    def test_search_by_name_and_species(self):
        self.shelter.add_animal(Cat("Milo", 1, "female", "Persian"))
        self.assertEqual(self.shelter.search_animals_by_name(" max "), [self.dog])
        self.assertEqual(self.shelter.search_animals_by_species(Dog), [self.dog])
        with self.assertRaises(ValueError):
            self.shelter.search_animals_by_name(" ")

    def test_invalid_species(self):
        with self.assertRaises(TypeError):
            self.shelter.search_animals_by_species(str)

    def test_adopt_and_return_update_both_sides_and_history(self):
        self.shelter.adopt_animal(self.dog.animal_id, self.adopter.adopter_id)
        self.assertTrue(self.dog.adopted)
        self.assertEqual(self.dog.adopter_id, self.adopter.adopter_id)
        self.assertEqual(self.adopter.adopted_animals, [self.dog.animal_id])
        self.assertEqual(self.dog.adoption_history[-1]["event"], "Adopted")

        self.shelter.return_animal(self.dog.animal_id)
        self.assertFalse(self.dog.adopted)
        self.assertIsNone(self.dog.adopter_id)
        self.assertEqual(self.adopter.adopted_animals, [])
        self.assertEqual(self.dog.adoption_history[-1]["event"], "Returned")

    def test_already_adopted_and_missing_animal(self):
        self.shelter.adopt_animal(self.dog.animal_id, self.adopter.adopter_id)
        with self.assertRaises(AnimalAlreadyAdoptedError):
            self.shelter.adopt_animal(self.dog.animal_id, self.adopter.adopter_id)
        with self.assertRaises(AnimalNotFoundError):
            self.shelter.return_animal("MISSING")

    def test_adoption_limit_is_nine(self):
        animals = [self.dog]
        for index in range(9):
            animal = Dog(f"Dog{index}", 1, "male", "Mixed")
            self.shelter.add_animal(animal)
            animals.append(animal)

        for animal in animals[:9]:
            self.shelter.adopt_animal(animal.animal_id, self.adopter.adopter_id)

        with self.assertRaises(MaximumAdoptionReachedError):
            self.shelter.adopt_animal(animals[9].animal_id, self.adopter.adopter_id)
        self.assertEqual(len(self.adopter.adopted_animals), 9)

    def test_duplicate_national_id_is_rejected(self):
        duplicate = Adopter("Reza", "09111111111", "1234567890")
        with self.assertRaises(DuplicateAdopterError):
            self.shelter.add_adopter(duplicate)

    def test_cannot_remove_adopted_animal_or_adopter(self):
        self.shelter.adopt_animal(self.dog.animal_id, self.adopter.adopter_id)
        with self.assertRaises(ValueError):
            self.shelter.remove_animal(self.dog.animal_id)
        with self.assertRaises(ValueError):
            self.shelter.remove_adopter(self.adopter.adopter_id)

    def test_remove_adopter_without_active_adoptions(self):
        self.shelter.remove_adopter(self.adopter.adopter_id)
        self.assertEqual(self.shelter.adopters, {})


    def test_failed_save_rolls_back_adoption(self):
        shelter = Shelter(storage=FailingStorage(), autosave=False)
        animal = Dog("Rex", 2, "male", "Mixed")
        adopter = Adopter("Sara", "09111111111", "1234567891")
        shelter.add_animal(animal)
        shelter.add_adopter(adopter)
        shelter.autosave = True

        with self.assertRaises(StorageError):
            shelter.adopt_animal(animal.animal_id, adopter.adopter_id)

        self.assertFalse(animal.adopted)
        self.assertIsNone(animal.adopter_id)
        self.assertEqual(adopter.adopted_animals, [])
        self.assertEqual(animal.adoption_history, [])

    def test_failed_save_rolls_back_health_record(self):
        shelter = Shelter(storage=FailingStorage(), autosave=False)
        animal = Dog("Rex", 2, "male", "Mixed")
        shelter.add_animal(animal)
        shelter.autosave = True

        with self.assertRaises(StorageError):
            shelter.add_health_record(animal.animal_id, "Checkup", "Healthy")

        self.assertEqual(animal.health_records, [])

    def test_health_record(self):
        self.shelter.add_health_record(
            self.dog.animal_id, "Checkup", "Healthy"
        )
        self.assertEqual(self.dog.health_records[0]["description"], "Healthy")

    def test_failed_save_rolls_back_add_animal(self):
        shelter = Shelter(storage=FailingStorage(), autosave=True)
        animal = Dog("Rex", 2, "male", "Mixed")
        with self.assertRaises(StorageError):
            shelter.add_animal(animal)
        self.assertEqual(shelter.animals, {})


if __name__ == "__main__":
    unittest.main()
