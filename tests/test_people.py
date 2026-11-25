import unittest

from people import Adopter


class AdopterTests(unittest.TestCase):
    def test_valid_adopter(self):
        adopter = Adopter("Ali", "09123456789", "1234567890")
        self.assertEqual(adopter.name, "Ali")
        self.assertEqual(adopter.adopted_animals, [])

    def test_invalid_phone_and_national_id(self):
        with self.assertRaises(ValueError):
            Adopter("Ali", "0912abc6789", "1234567890")
        with self.assertRaises(ValueError):
            Adopter("Ali", "09123456789", "12345")

    def test_name_validation(self):
        with self.assertRaises(ValueError):
            Adopter(" ", "09123456789", "1234567890")

    def test_duplicate_animal_ids_rejected(self):
        with self.assertRaises(ValueError):
            Adopter(
                "Ali", "09123456789", "1234567890",
                adopted_animals=["A1", "A1"],
            )

    def test_serialization_round_trip(self):
        adopter = Adopter("Ali", "09123456789", "1234567890")
        restored = Adopter.from_dict(adopter.to_dict())
        self.assertEqual(restored.to_dict(), adopter.to_dict())


if __name__ == "__main__":
    unittest.main()
