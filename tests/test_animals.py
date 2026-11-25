import unittest

from animals import Animal, Dog, Cat, Bird, Horse


class AnimalTests(unittest.TestCase):
    def test_valid_animal_and_status(self):
        dog = Dog(" Max ", 2, "male", " Labrador ")
        self.assertEqual(dog.name, "Max")
        self.assertEqual(dog.gender, "Male")
        self.assertEqual(dog.breed, "Labrador")
        self.assertEqual(dog.adoption_status, "Available")

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            Dog("", 2, "male", "Labrador")
        with self.assertRaises(ValueError):
            Dog("Max", -1, "male", "Labrador")
        with self.assertRaises(ValueError):
            Dog("Max", True, "male", "Labrador")
        with self.assertRaises(ValueError):
            Dog("Max", 2, "unknown", "Labrador")

    def test_adoption_state_must_be_consistent(self):
        with self.assertRaises(ValueError):
            Dog("Max", 2, "male", "Labrador", adopted=True)
        with self.assertRaises(ValueError):
            Dog("Max", 2, "male", "Labrador", adopter_id="ABC")

    def test_polymorphic_sounds(self):
        self.assertEqual(Dog("D", 1, "male", "x").make_sound(), "Woof! Woof!")
        self.assertEqual(Cat("C", 1, "female", "x").make_sound(), "Meow! Meow!")
        self.assertEqual(Bird("B", 1, "male", "x").make_sound(), "Chirp! Chirp!")
        self.assertEqual(Horse("H", 1, "female", "x").make_sound(), "Neigh! Neigh!")

    def test_serialization_preserves_subclass_and_records(self):
        dog = Dog("Max", 3, "male", "Labrador")
        dog.add_health_record("Vaccination", "Rabies vaccine")
        dog.add_adoption_event("adopted", "ADOPTER1")
        restored = Animal.from_dict(dog.to_dict())
        self.assertIsInstance(restored, Dog)
        self.assertEqual(restored.to_dict(), dog.to_dict())

    def test_from_dict_rejects_unknown_species(self):
        with self.assertRaises(ValueError):
            Animal.from_dict({
                "animal_type": "Dragon",
                "name": "D",
                "age": 1,
                "gender": "male",
                "breed": "x",
            })

    def test_record_validation(self):
        with self.assertRaises(ValueError):
            Dog("Max", 2, "male", "Labrador", health_records=["bad"])
        with self.assertRaises(ValueError):
            Dog("Max", 2, "male", "Labrador", health_records="")
        with self.assertRaises(ValueError):
            Dog(
                "Max", 2, "male", "Labrador",
                adoption_history=[{"event": "unknown", "adopter_id": "A", "timestamp": "now"}],
            )


if __name__ == "__main__":
    unittest.main()
