from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("violations", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="violation",
            name="recorded_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name="warning",
            name="issued_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
