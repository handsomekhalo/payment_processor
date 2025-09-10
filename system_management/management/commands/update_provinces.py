from django.core.management.base import BaseCommand
from system_management.models import Province

class Command(BaseCommand):
    help = 'Update province names'

    def handle(self, *args, **kwargs):
        provinces = {
            'Gauteng': 'Gauteng',
            'Northen cape': 'Northern Cape',
            'Western cape': 'Western Cape',
            'Eastern cape': 'Eastern Cape',
            'Limpopo': 'Limpopo',
            'Mpumalanga': 'Mpumalanga',
            'Free state': 'Free State',
            'North west': 'North West',
            'Kwazulu natal': 'KwaZulu-Natal'
        }

        for old_name, new_name in provinces.items():
            _, created = Province.objects.update_or_create(name=old_name, defaults={'name': new_name})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created new province: {new_name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Updated province: {old_name} to {new_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully updated province names'))