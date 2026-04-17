from django.db import migrations, models


def populate_client_name(apps, schema_editor):
    Case = apps.get_model('cases', 'Case')
    for case in Case.objects.select_related('client').all():
        if case.client_name:
            continue
        first = (getattr(case.client, 'first_name', '') or '').strip()
        last = (getattr(case.client, 'last_name', '') or '').strip()
        full_name = (f"{first} {last}").strip() or getattr(case.client, 'email', '') or 'Unknown Client'
        case.client_name = full_name
        case.save(update_fields=['client_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0002_casedocument_original_name_alter_case_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='client_name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.RunPython(populate_client_name, migrations.RunPython.noop),
    ]
