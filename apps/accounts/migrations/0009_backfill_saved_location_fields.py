from django.db import migrations


def backfill_saved_location(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    for profile in UserProfile.objects.all().iterator():
        changed = False
        if profile.saved_lat is None and profile.latitude is not None:
            profile.saved_lat = profile.latitude
            changed = True
        if profile.saved_lng is None and profile.longitude is not None:
            profile.saved_lng = profile.longitude
            changed = True
        if not profile.saved_location_name and profile.city:
            profile.saved_location_name = profile.city
            changed = True
        if not profile.saved_pincode and profile.pincode:
            profile.saved_pincode = profile.pincode
            changed = True
        if changed:
            profile.save(update_fields=['saved_lat', 'saved_lng', 'saved_location_name', 'saved_pincode'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_userprofile_recent_locations_userprofile_saved_lat_and_more'),
    ]

    operations = [
        migrations.RunPython(backfill_saved_location, noop_reverse),
    ]
