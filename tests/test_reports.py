import unittest

from animals import Dog, Cat
from people import Adopter
from shelter import Shelter
from reports import ShelterReports
from exceptions import AnimalNotFoundError


class ReportsTests(unittest.TestCase):
    def setUp(self):
        self.shelter = Shelter(autosave=False)
        self.dog = Dog("Max", 4, "male", "Labrador")
        self.cat = Cat("Milo", 2, "female", "Persian")
        self.adopter = Adopter("Ali", "09123456789", "1234567890")
        self.shelter.add_animal(self.dog)
        self.shelter.add_animal(self.cat)
        self.shelter.add_adopter(self.adopter)
        self.reports = ShelterReports(self.shelter)

    def test_summary_and_detailed_stats(self):
        summary = self.reports.get_summary()
        self.assertEqual(summary["total_animals"], 2)
        self.assertEqual(summary["available_animals"], 2)
        self.assertEqual(summary["species_counts"], {"Dog": 1, "Cat": 1})
        stats = self.reports.get_detailed_stats()
        self.assertEqual(stats["average_age"], 3)
        self.assertEqual(stats["available_percentage"], 100)

    def test_filter_and_sort(self):
        self.assertEqual(self.reports.filter_animals(min_age=3), [self.dog])
        self.assertEqual(self.reports.filter_animals(species=Cat), [self.cat])
        self.assertEqual(
            self.reports.sort_animals("age"),
            [self.cat, self.dog],
        )

    def test_adoption_count_and_latest_event(self):
        self.shelter.adopt_animal(self.dog.animal_id, self.adopter.adopter_id)
        self.shelter.return_animal(self.dog.animal_id)
        self.assertEqual(self.reports.get_adoption_count(self.dog.animal_id), 1)
        self.assertEqual(
            self.reports.get_latest_event(self.dog.animal_id)["event"],
            "Returned",
        )

    def test_missing_animal_history(self):
        with self.assertRaises(AnimalNotFoundError):
            self.reports.get_animal_history("UNKNOWN")


if __name__ == "__main__":
    unittest.main()
