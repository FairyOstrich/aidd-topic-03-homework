from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from user.forms import RegistrationForm


class UserFlowTests(TestCase):
    def test_login_page_renders_input_fields(self):
        response = self.client.get(reverse("user:auth"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password"')
        self.assertNotContains(response, "EmailField object")

    def test_registration_page_renders_input_fields(self):
        response = self.client.get(reverse("user:registration"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')
        self.assertNotContains(response, "EmailField object")

    def test_registration_normalizes_email_and_logs_user_in(self):
        response = self.client.post(
            reverse("user:registration"),
            {
                "email": "Person@Example.com",
                "password1": "a-strong-password",
                "password2": "a-strong-password",
            },
        )

        self.assertRedirects(response, reverse("dashboard:index"))
        user = get_user_model().objects.get(username="person@example.com")
        self.assertEqual(user.email, "person@example.com")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_registration_missing_fields_returns_form_errors(self):
        response = self.client.post(reverse("user:registration"), {"email": ""})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_registration_rejects_mismatched_passwords(self):
        form = RegistrationForm(
            {
                "email": "person@example.com",
                "password1": "first-password",
                "password2": "different-password",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("Введенные пароли не совпадают", form.errors.as_text())

    def test_login_validates_required_fields(self):
        response = self.client.post(reverse("user:auth"), {})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Проверьте введенные данные.")

    def test_login_uses_normalized_email(self):
        get_user_model().objects.create_user(
            username="person@example.com",
            email="person@example.com",
            password="a-strong-password",
        )

        response = self.client.post(
            reverse("user:auth"),
            {"email": "Person@Example.com", "password": "a-strong-password"},
        )

        self.assertRedirects(response, reverse("dashboard:index"))
