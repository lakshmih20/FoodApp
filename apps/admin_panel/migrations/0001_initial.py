from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0006_remove_cookprofile_fssai_ocr_confidence_and_more'),
        ('buyers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('food_quality_issue', 'Food quality issue'), ('cook_did_not_prepare', 'Cook did not prepare order'), ('cook_not_responding', 'Cook not responding'), ('other', 'Other')], max_length=50)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('open', 'Open'), ('resolved', 'Resolved')], default='open', max_length=20)),
                ('admin_note', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_made', to='accounts.user')),
                ('cook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_received', to='accounts.cookprofile')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='buyers.buyerorder')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
