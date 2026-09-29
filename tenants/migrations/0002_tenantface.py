from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("tenants", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="TenantFace",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("photo", models.BinaryField()),
                ("embedding", models.JSONField()),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("tenant", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="face", to="tenants.tenant")),
            ],
        ),
    ]
