import team_finder.validators
from django.db import migrations, models


def normalize_existing_phones(apps, schema_editor):
    users = apps.get_model("userManager", "User")
    seen = set()
    for user in users.objects.using(
        schema_editor.connection.alias
    ).all():
        phone = user.phone
        if phone:
            phone = team_finder.validators.normalize_phone(phone)
            if phone in seen:
                raise ValueError("Обнаружены повторяющиеся телефоны.")
            seen.add(phone)
        user.phone = phone or None
        user.save(update_fields=["phone"])


class Migration(migrations.Migration):

    dependencies = [
        ("userManager", "0008_rename_github_user_github_url"),
    ]

    operations = [
        migrations.RunPython(
            normalize_existing_phones,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="user",
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
            model_name="user",
            name="phone",
            field=models.CharField(
                blank=True,
                max_length=12,
                null=True,
                unique=True,
                validators=[team_finder.validators.validate_phone],
            ),
        ),
    ]
