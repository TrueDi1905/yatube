from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи именён:
         about:author и about:tech, доступен."""
        url_names = {
            'about:author': 200,
            'about:tech': 200,
        }
        for url, status in url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse(url)).status_code
                self.assertEqual(response, status)

    def test_about_template(self):
        """При запросе к  about:author и about:tech
        применяются шаблоны about:author.html и about:tech.html."""
        templates_url_names = {
            'about_author.html': 'about:author',
            'about_tech.html': 'about:tech',
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse(reverse_name))
                self.assertTemplateUsed(response, template)
