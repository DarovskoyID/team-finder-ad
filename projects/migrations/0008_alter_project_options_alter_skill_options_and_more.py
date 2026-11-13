import django.db.models.deletion
import team_finder.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "projectManager",
            (
                "0007_alter_project_github_url_alter_"
                "project_participants_and_more"
            ),
        ),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="project",
            options={
                "ordering": ("-created_at", "-pk"),
                "verbose_name": "Проект",
                "verbose_name_plural": "Проекты",
            },
        ),
        migrations.AlterModelOptions(
            name="skill",
            options={
                "ordering": ("name",),
                "verbose_name": "Навык",
                "verbose_name_plural": "Навыки",
            },
        ),
        migrations.AlterField(
            model_name="project",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Дата создания"
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="description",
            field=models.TextField(
                blank=True, null=True, verbose_name="Описание"
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="github_url",
            field=models.URLField(
                blank=True,
                null=True,
                validators=[
                    team_finder.validators.validate_github_url
                ],
                verbose_name="GitHub URL",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="id",
            field=models.AutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="name",
            field=models.CharField(
                max_length=200, verbose_name="Название великой идеи"
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="owner",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="owned_projects",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Автор",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="participants",
            field=models.ManyToManyField(
                blank=True,
                related_name="participated_projects",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Участники",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="skills",
            field=models.ManyToManyField(
                blank=True,
                related_name="projects",
                to="projectManager.skill",
                verbose_name="Навыки",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[("open", "Открыт"), ("closed", "Закрыт")],
                default="open",
                max_length=6,
                verbose_name="Статус проекта",
            ),
        ),
        migrations.AlterField(
            model_name="skill",
            name="id",
            field=models.AutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
        migrations.AlterField(
            model_name="skill",
            name="name",
            field=models.CharField(
                max_length=124, unique=True, verbose_name="Название"
            ),
        ),
    ]
