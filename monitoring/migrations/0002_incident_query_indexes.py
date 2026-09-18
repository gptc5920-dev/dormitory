from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("monitoring", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="incident",
            name="occurred_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name="incident",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "New"),
                    ("reviewed", "Reviewed"),
                    ("verified", "Verified"),
                    ("dismissed", "Dismissed"),
                    ("assigned", "Assigned"),
                ],
                db_index=True,
                default="new",
                max_length=20,
            ),
        ),
    ]
