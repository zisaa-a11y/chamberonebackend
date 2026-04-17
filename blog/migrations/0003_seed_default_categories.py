from django.db import migrations
from django.utils.text import slugify


DEFAULT_LEGAL_CATEGORIES = [
    'Criminal Law',
    'Family Law',
    'Corporate Law',
    'Property Law',
    'Constitutional Law',
    'Others',
]


def seed_default_categories(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')
    for name in DEFAULT_LEGAL_CATEGORIES:
        slug = slugify(name)
        category, created = Category.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'is_active': True},
        )
        if not created:
            changed = False
            if category.name != name:
                category.name = name
                changed = True
            if not category.is_active:
                category.is_active = True
                changed = True
            if changed:
                category.save(update_fields=['name', 'is_active'])


def remove_default_categories(apps, schema_editor):
    Category = apps.get_model('blog', 'Category')
    Category.objects.filter(name__in=DEFAULT_LEGAL_CATEGORIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0002_blogpost_external_image_url'),
    ]

    operations = [
        migrations.RunPython(seed_default_categories, remove_default_categories),
    ]
