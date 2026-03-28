from jobs.models import Category
categories = [
    ('Software Development', 'fa-laptop-code'),
    ('Data Science', 'fa-database'),
    ('Marketing', 'fa-bullhorn'),
    ('Design', 'fa-paint-brush'),
    ('Finance', 'fa-chart-line'),
    ('Business', 'fa-briefcase'),
]
for name, icon in categories:
    Category.objects.get_or_create(name=name, icon_class=icon)
print("Categories seeded successfully")
