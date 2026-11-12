import json

from django.test import TestCase, override_settings
from django.urls import reverse

from projectManager.models import Project, Skill
from userManager.models import User

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
class ProjectViewsTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email=ownmail,
            password=passwd,
            name="Иван",
            surname="Иванов",
        )

        self.other = User.objects.create_user(
            email=othermail,
            password=passwd,
            name="Пётр",
            surname="Петров",
        )

        self.skill = Skill.objects.create(name="Python")
        self.project = Project.objects.create(
            name="Proj",
            description="disc",
            owner=self.owner,
            status="open",
        )

        self.project.skills.add(self.skill)

    def test_list_page_available_for_guest(self):
        response = self.client.get(reverse("projects:list"))

        self.assertEqual(response.status_code, 200)

    def test_filter_by_existing_skill(self):
        response = self.client.get(
            reverse("projects:list"), {"skill": "Python"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.project, response.context["page_obj"])

    def test_filter_by_missing_skill_returns_empty(self):
        response = self.client.get(
            reverse("projects:list"), {"skill": "НетТакого"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 0)

    def test_detail_404_for_missing_project(self):
        response = self.client.get(
            reverse("projects:project_detail", args=[999999])
        )

        self.assertEqual(response.status_code, 404)

    def test_guest_cannot_create_project(self):
        response = self.client.get(reverse("projects:create_project"))

        self.assertEqual(response.status_code, 302)

    def test_owner_can_create_project(self):
        self.client.login(username=ownmail, password=passwd)

        response = self.client.post(
            reverse("projects:create_project"),
            {
                "name": "new project",
                "description": "disc",
                "github_url": "https://github.com/octocat",
                "status": "open",
            },
        )
        self.assertEqual(response.status_code, 302)
        new_project = Project.objects.get(name="new project")
        self.assertEqual(new_project.owner, self.owner)
        self.assertIn(self.owner, new_project.participants.all())

    def test_stranger_cannot_edit_project(self):
        self.client.login(username=othermail, password=passwd)
        response = self.client.post(
            reverse("projects:project_edit", args=[self.project.id]),
            {
                "name": "crack",
                "description": "x",
                "github_url": "https://x.ru",
                "status": "open",
            },
        )
        self.assertRedirects(response, "/projects/list/")
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Proj")

    def test_toggle_participate(self):
        self.client.login(username=othermail, password=passwd)
        url = reverse(
            "projects:toggle_participate", args=[self.project.id]
        )

        response = self.client.post(url)
        self.assertJSONEqual(
            response.content, {"status": "ok", "participant": True}
        )
        self.assertIn(self.other, self.project.participants.all())

        response = self.client.post(url)
        self.assertJSONEqual(
            response.content, {"status": "ok", "participant": False}
        )

    def test_toggle_participate_rejects_get(self):
        self.client.login(username=othermail, password=passwd)
        response = self.client.get(
            reverse(
                "projects:toggle_participate", args=[self.project.id]
            )
        )
        self.assertEqual(response.status_code, 405)

    def test_owner_can_complete_project(self):
        self.client.login(username=ownmail, password=passwd)
        response = self.client.post(
            reverse(
                "projects:project_complete", args=[self.project.id]
            )
        )
        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.status, "closed")

    def test_stranger_cannot_add_skill(self):
        self.client.login(username=othermail, password=passwd)
        response = self.client.post(
            reverse("projects:skill_add", args=[self.project.id]),
            data=json.dumps({"name": "Django"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_owner_can_add_new_skill(self):
        self.client.login(username=ownmail, password=passwd)
        response = self.client.post(
            reverse("projects:skill_add", args=[self.project.id]),
            data=json.dumps({"name": "Django"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            self.project.skills.filter(name="Django").exists()
        )

    def test_invalid_skill_payloads_return_bad_request(self):
        self.client.force_login(self.owner)
        url = reverse("projects:skill_add", args=[self.project.pk])
        payloads = [
            [],
            None,
            42,
            {"name": []},
            {"name": " "},
            {"name": "x" * 129},
            {"skill_id": "invalid"},
            {"skill_id": True},
            {"skill_id": "9" * 100},
        ]
        for payload in payloads:
            with self.subTest(payload=payload):
                response = self.client.post(
                    url,
                    json.dumps(payload),
                    content_type="application/json",
                )
                self.assertEqual(response.status_code, 400)

    def test_empty_skill_search_returns_list(self):
        response = self.client.get(reverse("projects:skills_search"))
        self.assertEqual(response.json(), [])

    def test_edit_saves_existing_project(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("projects:project_edit", args=[self.project.pk]),
            {
                "name": "Updated",
                "description": "",
                "github_url": "",
                "status": "closed",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Updated")
        self.assertEqual(self.project.owner, self.owner)

    def test_closed_project_rejects_participation(self):
        self.client.force_login(self.other)
        self.project.status = "closed"
        self.project.save()
        response = self.client.post(
            reverse(
                "projects:toggle_participate",
                args=[self.project.pk],
            )
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.project.participants.exists())

    def test_search_matches_prefix_and_sorts(self):
        for name in ("zzpython", "Python Z", "Python A"):
            Skill.objects.create(name=name)
        response = self.client.get(
            reverse("projects:skills_search"),
            {"q": "Py"},
        )
        self.assertEqual(
            [item["name"] for item in response.json()],
            ["Python", "Python A", "Python Z"],
        )

    def test_add_skill_reports_creation_and_duplicate(self):
        self.client.force_login(self.owner)
        url = reverse("projects:skill_add", args=[self.project.pk])
        first = self.client.post(
            url,
            {"name": "Django"},
            content_type="application/json",
        ).json()
        self.assertTrue(first["created"])
        self.assertTrue(first["added"])
        second = self.client.post(
            url,
            {"skill_id": first["skill_id"]},
            content_type="application/json",
        ).json()
        self.assertFalse(second["created"])
        self.assertFalse(second["added"])

    def test_remove_skill_keeps_skill_and_rejects_missing(self):
        self.client.force_login(self.owner)
        url = reverse(
            "projects:skill_remove",
            args=[
                self.project.pk,
                self.skill.pk,
            ],
        )
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertTrue(
            Skill.objects.filter(pk=self.skill.pk).exists()
        )
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_complete_response_and_repeat(self):
        self.client.force_login(self.owner)
        url = reverse(
            "projects:project_complete", args=[self.project.pk]
        )
        self.assertEqual(
            self.client.post(url).json(),
            {
                "status": "ok",
                "project_status": "closed",
            },
        )
        self.assertEqual(self.client.post(url).status_code, 400)

    def test_github_validation(self):
        from projectManager.forms import ProjectCreateForm

        invalid_urls = (
            "https://example.com",
            "https://github.com.evil.com/a",
            "https://github.com@evil.com/a",
        )
        for url in invalid_urls:
            form = ProjectCreateForm(
                {
                    "name": "Project",
                    "status": "open",
                    "github_url": url,
                }
            )
            self.assertFalse(form.is_valid())
            self.assertIn("github_url", form.errors)

    def test_filtered_pagination(self):
        for index in range(13):
            project = Project.objects.create(
                name=f"Project {index}",
                owner=self.owner,
                status="open",
            )
            project.skills.add(self.skill)
        response = self.client.get(
            reverse("projects:list"),
            {
                "skill": "Python",
                "page": 2,
            },
        )
        self.assertEqual(len(response.context["page_obj"]), 2)
        self.assertIn(
            "skill=Python", response.context["query_prefix"]
        )
