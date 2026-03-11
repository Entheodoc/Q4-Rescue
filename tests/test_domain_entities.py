import unittest

from app.domain import Pharmacy, Prescriber, Provider


class DomainEntityAvailabilityTests(unittest.TestCase):
    def test_provider_and_pharmacy_entities_are_available(self):
        provider = Provider.create(name="Dr. Smith", phone_numbers=("555-1111",))
        pharmacy = Pharmacy.create(name="CVS", phone_numbers=("555-2222",))

        self.assertEqual(provider.name, "Dr. Smith")
        self.assertEqual(pharmacy.name, "CVS")

    def test_prescriber_alias_maps_to_provider(self):
        prescriber = Prescriber.create(name="Dr. Lopez")

        self.assertIsInstance(prescriber, Provider)
