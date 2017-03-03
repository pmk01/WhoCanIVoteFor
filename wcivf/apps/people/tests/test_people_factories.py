from django.test import TestCase

from people.tests.factories import PersonFactory

from people.models import Person

class TestFactories(TestCase):
    """
    Meta tests to ensure that the factories are working
    """

    def _test_save(self, model, factory):
        self.assertEqual(model.objects.all().count(), 0)
        created_model = factory.create()
        self.assertEqual(model.objects.all().count(), 1)
        return created_model

    def test_person_factory(self):
        model = self._test_save(Person, PersonFactory)
        self.assertEqual(model.name, "Jane Smith")

