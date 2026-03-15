from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_cookprofile_fssai_ocr_confidence_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cookprofile',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
