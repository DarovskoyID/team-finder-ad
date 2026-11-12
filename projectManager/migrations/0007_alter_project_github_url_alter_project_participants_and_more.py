import team_finder.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projectManager", "0006_alter_skill_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="project",
            name="github_url",
            field=models.URLField(
                blank=True,
                null=True,
                validators=[
                    team_finder.validators.validate_github_url
                ],
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="participants",
            field=models.ManyToManyField(
                blank=True,
                related_name="participated_projects",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="skills",
            field=models.ManyToManyField(
                blank=True,
                related_name="projects",
                to="projectManager.skill",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="status",
            field=models.CharField(
                choices=[("open", "Открыт"), ("closed", "Закрыт")],
                max_length=6,
            ),
        ),
        migrations.AlterField(
            model_name="skill",
            name="name",
            field=models.CharField(max_length=124, unique=True),
        ),
    ]
