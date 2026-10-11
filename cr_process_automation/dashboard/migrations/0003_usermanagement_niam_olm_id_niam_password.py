# Generated manually for NIAM OLM ID / NIAM Password user fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0002_niamaccesstypetable_niamcircletable_niamdomainstable_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="usermanagement",
            name="niam_olm_id",
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name="NIAM OLM ID"),
        ),
        migrations.AddField(
            model_name="usermanagement",
            name="niam_password",
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name="NIAM Password"),
        ),
    ]
