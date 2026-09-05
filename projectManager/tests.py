import json

from django.test import TestCase
from django.urls import reverse

from projectManager.models import Project, Skill
from userManager.models import User


class ProjectViewsTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='test+1@test.ru', password='1234',
            name='Иван', surname='Иванов',
        )

        self.other = User.objects.create_user(
            email='test@test.ru', password='1234',
            name='Пётр', surname='Петров',
        )

        self.skill = Skill.objects.create(name='Python')
        self.project = Project.objects.create(
            name='Proj', description='disc',
            owner=self.owner, status='open',
        )

        self.project.skills.add(self.skill)

    def test_list_page_available_for_guest(self):
        response = self.client.get(reverse('projects:list'))

        self.assertEqual(response.status_code, 200)

    def test_filter_by_existing_skill(self):
        response = self.client.get(reverse('projects:list'), {'skill': 'Python'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.project, response.context['page_obj'])

    def test_filter_by_missing_skill_returns_empty(self):
        response = self.client.get(reverse('projects:list'), {'skill': 'НетТакого'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_detail_404_for_missing_project(self):
        response = self.client.get(reverse('projects:project_detail', args=[999999]))

        self.assertEqual(response.status_code, 404)

    def test_guest_cannot_create_project(self):
        response = self.client.get(reverse('projects:create_project'))

        self.assertEqual(response.status_code, 302)

    def test_owner_can_create_project(self):
        self.client.login(username='test+1@test.ru', password='1234')

        response = self.client.post(reverse('projects:create_project'), {
            'name': 'new project',
            'description': 'disc',
            'github_url': 'https://np.ru',
            'status': 'open',
        })
        self.assertEqual(response.status_code, 302)
        new_project = Project.objects.get(name='new project')
        self.assertEqual(new_project.owner, self.owner)
        self.assertIn(self.owner, new_project.participants.all())

    def test_stranger_cannot_edit_project(self):
        self.client.login(username='test@test.ru', password='1234')
        response = self.client.post(
            reverse('projects:project_edit', args=[self.project.id]),
            {'name': 'crack', 'description': 'x',
             'github_url': 'https://x.ru', 'status': 'open'},
        )
        self.assertRedirects(response, '/projects/list/')
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Proj')

    def test_toggle_participate(self):
        self.client.login(username='test@test.ru', password='1234')
        url = reverse('projects:toggle_participate', args=[self.project.id])

        response = self.client.post(url)
        self.assertJSONEqual(response.content, {'status': 'ok', 'participant': True})
        self.assertIn(self.other, self.project.participants.all())

        response = self.client.post(url)
        self.assertJSONEqual(response.content, {'status': 'ok', 'participant': False})

    def test_toggle_participate_rejects_get(self):
        self.client.login(username='test+1@test.ru', password='1234')
        response = self.client.get(
            reverse('projects:toggle_participate', args=[self.project.id])
        )
        self.assertEqual(response.status_code, 405)

    def test_owner_can_complete_project(self):
        self.client.login(username='test@test.ru', password='1234')
        response = self.client.post(
            reverse('projects:project_complete', args=[self.project.id])
        )
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, 'closed')

    def test_stranger_cannot_add_skill(self):
        self.client.login(username='test+1@test.ru', password='1234')
        response = self.client.post(
            reverse('projects:skill_add', args=[self.project.id]),
            data=json.dumps({'name': 'Django'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 403)

    def test_owner_can_add_new_skill(self):
        self.client.login(username='test@test.ru', password='1234')
        response = self.client.post(
            reverse('projects:skill_add', args=[self.project.id]),
            data=json.dumps({'name': 'Django'}),
            content_type='application/json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.project.skills.filter(name='Django').exists())