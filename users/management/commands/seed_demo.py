from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.sessions.models import Session
from django.core.management.base import BaseCommand
from django.db import transaction

from projects.models import Project, Skill


class Command(BaseCommand):
    help = "Заполняет базу демонстрационными данными TeamFinder."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Удалить текущих пользователей и проекты.",
        )
        parser.add_argument(
            "--password", default="TeamFinder-demo-42!"
        )

    @transaction.atomic
    def handle(self, *args, **options):
        user_model = get_user_model()
        if options["reset"]:
            Session.objects.all().delete()
            LogEntry.objects.all().delete()
            Project.objects.all().delete()
            Skill.objects.all().delete()
            user_model.objects.all().delete()

        names = [
            ("Иван", "Иванов"),
            ("Анна", "Смирнова"),
            ("Михаил", "Кузнецов"),
            ("Елена", "Попова"),
            ("Павел", "Соколов"),
            ("Мария", "Лебедева"),
            ("Дмитрий", "Козлов"),
            ("Ольга", "Новикова"),
            ("Алексей", "Морозов"),
            ("Софья", "Волкова"),
            ("Андрей", "Зайцев"),
            ("Дарья", "Павлова"),
            ("Никита", "Семёнов"),
            ("Вера", "Голубева"),
        ]
        titles = [
            "Поиск команды",
            "Планировщик путешествий",
            "Библиотека рецептов",
            "Трекер привычек",
            "Карта городских событий",
            "Обмен книгами",
            "Учёт личных расходов",
            "Дневник тренировок",
            "Каталог настольных игр",
            "Платформа наставников",
            "Сервис волонтёрства",
            "Календарь обучения",
            "Домашняя метеостанция",
            "Планировщик задач",
        ]
        skills = [
            Skill.objects.get_or_create(name=name)[0]
            for name in (
                "Python",
                "Django",
                "PostgreSQL",
                "JavaScript",
                "React",
                "HTML",
                "CSS",
                "Docker",
                "Git",
                "Figma",
                "TypeScript",
                "Redis",
            )
        ]
        password = make_password(options["password"])
        users = []
        for index, (name, surname) in enumerate(names, 1):
            user, _ = user_model.objects.get_or_create(
                email=f"demo{index}@example.com",
                defaults={
                    "name": name,
                    "surname": surname,
                    "phone": f"+7900000{index:04d}",
                    "about": "Разрабатываю проекты и ищу команду.",
                    "github_url": "https://github.com/octocat",
                    "password": password,
                },
            )
            users.append(user)
        admin, _ = user_model.objects.get_or_create(
            email="admin@example.com",
            defaults={
                "name": "Администратор",
                "surname": "TeamFinder",
                "is_staff": True,
                "is_superuser": True,
                "password": password,
            },
        )
        for index, user in enumerate([*users, admin]):
            project, _ = Project.objects.get_or_create(
                owner=user,
                name=titles[index % len(titles)],
                defaults={
                    "description": (
                        "Собираем команду для разработки сервиса. "
                        "Нужны разработчики и дизайнеры. "
                        "Обсудим задачи и поможем освоиться."
                    ),
                    "status": (
                        Project.Status.CLOSED
                        if index % 5 == 4
                        else Project.Status.OPEN
                    ),
                    "github_url": "https://github.com/octocat",
                },
            )
            project.participants.add(
                user,
                users[(index + 1) % len(users)],
            )
            project.skills.add(
                skills[index % len(skills)],
                skills[(index + 1) % len(skills)],
            )
        self.stdout.write(
            self.style.SUCCESS(
                "Данные готовы: 15 пользователей, "
                "15 проектов, 12 навыков."
            )
        )
