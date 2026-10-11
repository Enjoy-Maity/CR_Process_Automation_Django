# Generated manually — widen NIAMActivityNameTable.activity_name for seed values

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0004_niamactivitynametable"),
    ]

    operations = [
        migrations.AlterField(
            model_name="niamactivitynametable",
            name="activity_name",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="Activity Name"),
        ),
    ]
