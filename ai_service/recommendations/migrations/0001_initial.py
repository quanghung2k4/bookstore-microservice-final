from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserBehaviorEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user_id", models.CharField(db_index=True, max_length=128)),
                ("product_id", models.CharField(db_index=True, max_length=128)),
                ("action", models.CharField(max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="userbehaviorevent",
            index=models.Index(fields=["user_id", "created_at"], name="recommendat_user_id_8e0d6b_idx"),
        ),
        migrations.AddIndex(
            model_name="userbehaviorevent",
            index=models.Index(fields=["user_id", "product_id"], name="recommendat_user_id_7c6134_idx"),
        ),
    ]
