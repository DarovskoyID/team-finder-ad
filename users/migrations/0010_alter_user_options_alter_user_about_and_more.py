import team_finder.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "userManager",
            "0009_alter_user_github_url_alter_user_phone",
        ),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={
                "ordering": ("-date_joined", "-pk"),
                "verbose_name": "Пользователь",
                "verbose_name_plural": "Пользователи",
            },
        ),
        migrations.AlterField(
            model_name="user",
            name="about",
            field=models.TextField(
                blank=True,
                max_length=256,
                null=True,
                verbose_name="О себе",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="avatar",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="avatars/",
                verbose_name="Аватар",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="date_joined",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Дата регистрации"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=254, unique=True, verbose_name="Email"
            ),
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
                verbose_name="GitHub",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="id",
            field=models.AutoField(
                auto_created=True,
                primary_key=True,
                serialize=False,
                verbose_name="ID",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(
                default=True, verbose_name="Активен"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="is_staff",
            field=models.BooleanField(
                default=False, verbose_name="Доступ в админку"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="name",
            field=models.CharField(
                max_length=124, verbose_name="Имя"
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
                verbose_name="Телефон",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="surname",
            field=models.CharField(
                max_length=124, verbose_name="Фамилия"
            ),
        ),
    ]
