from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from projects.models import Project
from users.forms import EditProfileForm
from users.models import User

ownmail = "test+1@test.ru"
othermail = "test@test.ru"
passwd = "1234"


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.InMemoryStorage",
        },
        "staticfiles": {
            "BACKEND": (
                "django.contrib.staticfiles.storage."
                "StaticFilesStorage"
            ),
        },
    },
    PASSWORD_HASHERS=[
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ],
)
class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email=othermail,
            password=passwd,
            name="Иван",
            surname="Иванов",
        )

        self.assertEqual(user.email, othermail)
        self.assertTrue(user.check_password(passwd))
        self.assertFalse(user.is_staff)

    def test_create_user_without_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password=passwd)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email="admin@test.ru",
            password=passwd,
            name="Admin",
            surname="admn",
        )

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.InMemoryStorage",
        },
        "staticfiles": {
            "BACKEND": (
                "django.contrib.staticfiles.storage."
                "StaticFilesStorage"
            ),
        },
    },
    PASSWORD_HASHERS=[
        "django.contrib.auth.hashers.MD5PasswordHasher",
    ],
)
class AuthViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=othermail,
            password=passwd,
            name="Иван",
            surname="Иванов",
        )

    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "email": ownmail,
                "password": "Valid-registration-42!",
                "name": "Peter",
                "surname": "PArker",
            },
        )

        self.assertRedirects(response, reverse("users:login"))
        self.assertTrue(User.objects.filter(email=ownmail).exists())

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("users:login"),
            {
                "email": othermail,
                "password": passwd,
            },
        )

        self.assertRedirects(response, reverse("projects:list"))

    def test_login_with_wrong_password(self):
        response = self.client.post(
            reverse("users:login"),
            {
                "email": othermail,
                "password": "wrong",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)

    def test_user_detail_page_available_for_guest(self):
        response = self.client.get(
            reverse("users:info_about_user", args=[self.user.id])
        )
        self.assertEqual(response.status_code, 200)

    def test_user_detail_404_for_missing_user(self):
        response = self.client.get(
            reverse("users:info_about_user", args=[999999])
        )
        self.assertEqual(response.status_code, 404)

    def test_edit_profile_redirects_guest(self):
        response = self.client.get(reverse("users:edit_profile"))
        self.assertEqual(response.status_code, 302)

    def test_register_rejects_weak_password(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "email": ownmail,
                "password": "1234",
                "name": "Peter",
                "surname": "Parker",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email=ownmail).exists())

    def test_profile_edit_preserves_existing_avatar(self):
        self.user.avatar = "avatars/existing.png"
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("users:edit_profile"),
            {
                "name": "Updated",
                "surname": self.user.surname,
                "about": "",
                "phone": "",
                "github_url": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "Updated")
        self.assertEqual(
            self.user.avatar.name, "avatars/existing.png"
        )

    def test_phone_and_github_validation(self):

        data = {"name": "Иван", "surname": "Иванов", "phone": "abc"}
        form = EditProfileForm(data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)
        data["phone"] = "89991234567"
        form = EditProfileForm(data, instance=self.user)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, "+79991234567")
        other = User.objects.create_user(email="duplicate@test.ru")
        form = EditProfileForm(data, instance=other)
        self.assertFalse(form.is_valid())
        self.assertIn("phone", form.errors)
        data["github_url"] = "https://example.com"
        form = EditProfileForm(data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("github_url", form.errors)

    def test_change_password_keeps_session(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("users:change_password"),
            {
                "old_password": passwd,
                "new_password1": "New-strong-password-42!",
                "new_password2": "New-strong-password-42!",
            },
        )
        self.assertRedirects(
            response,
            reverse(
                "users:info_about_user",
                args=[self.user.pk],
            ),
        )
        self.user.refresh_from_db()
        self.assertTrue(
            self.user.check_password(
                "New-strong-password-42!",
            )
        )
        self.assertEqual(
            self.client.get(
                reverse("users:edit_profile"),
            ).status_code,
            200,
        )

    def test_seed_demo_is_repeatable(self):

        call_command("seed_demo", stdout=StringIO())
        count = User.objects.count()
        projects = Project.objects.count()
        call_command("seed_demo", stdout=StringIO())
        self.assertEqual(User.objects.count(), count)
        self.assertEqual(Project.objects.count(), projects)
        self.assertTrue(
            User.objects.get(
                email="admin@example.com",
            ).is_superuser
        )
        call_command("seed_demo", reset=True, stdout=StringIO())
        self.assertEqual(User.objects.count(), 15)
        self.assertEqual(Project.objects.count(), 15)
