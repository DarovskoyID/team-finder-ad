from django.test import TestCase
from django.urls import reverse

from userManager.models import User

ownmail = 'test+1@test.ru'
othermail = 'test@test.ru'
passwd = '1234'


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email=othermail, password=passwd,
            name='Иван', surname='Иванов',
        )

        self.assertEqual(user.email, othermail)
        self.assertTrue(user.check_password(passwd))
        self.assertFalse(user.is_staff)

    def test_create_user_without_email_raises(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password=passwd)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email='admin@test.ru', password=passwd,
            name='Admin', surname='admn',
        )

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class AuthViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email=othermail, password=passwd,
            name='Иван', surname='Иванов',
        )

    def test_register_creates_user_and_redirects_to_login(self):
        response = self.client.post(reverse('users:register'), {
            'email': ownmail,
            'password': passwd,
            'name': 'Peter',
            'surname': 'PArker',
        })

        self.assertRedirects(response, '/users/login/')
        self.assertTrue(User.objects.filter(email=ownmail).exists())

    def test_login_with_valid_credentials(self):
        response = self.client.post(reverse('users:login'), {
            'email': othermail,
            'password': passwd,
        })

        self.assertRedirects(response, '/projects/list/')

    def test_login_with_wrong_password(self):
        response = self.client.post(reverse('users:login'), {
            'email': othermail,
            'password': 'wrong',
        })

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

    def test_user_detail_page_available_for_guest(self):
        response = self.client.get(
            reverse('users:info_about_user', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)

    def test_user_detail_404_for_missing_user(self):
        response = self.client.get(
            reverse('users:info_about_user', args=[999999]))
        self.assertEqual(response.status_code, 404)

    def test_edit_profile_redirects_guest(self):
        response = self.client.get(reverse('users:edit_profile'))
        self.assertEqual(response.status_code, 302)
