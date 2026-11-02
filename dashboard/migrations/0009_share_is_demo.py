from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0008_pricehistory"),
    ]

    operations = [
        migrations.AddField(
            model_name="share",
            name="is_demo",
            field=models.BooleanField(default=False, verbose_name="Демо-инструмент"),
        ),
    ]
