from django.core.management.base import BaseCommand
from jobs.models import Category

class Command(BaseCommand):
    help = 'Seeds initial categories'

    def handle(self, *args, **options):
        categories = [
            ('Software Development', 'fa-laptop-code'),
            ('Data Science', 'fa-database'),
            ('Marketing', 'fa-bullhorn'),
            ('Design', 'fa-paint-brush'),
            ('Finance', 'fa-chart-line'),
            ('Business', 'fa-briefcase'),
        ]
        for name, icon in categories:
            cat, created = Category.objects.get_or_create(name=name, icon_class=icon)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created category "{name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Category "{name}" already exists'))
