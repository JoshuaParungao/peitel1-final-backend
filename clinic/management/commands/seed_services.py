from django.core.management.base import BaseCommand
from clinic.models import Service

class Command(BaseCommand):
    help = 'Seed default services into the database using Service.DEFAULT_PRICES and DENTAL_CATEGORIES'

    def handle(self, *args, **options):
        # Build a mapping from category key to verbose name
        cat_map = {key: label for key, label in Service.DENTAL_CATEGORIES}
        created = 0
        updated = 0
        for key, price in Service.DEFAULT_PRICES.items():
            name = cat_map.get(key, key.replace('_', ' ').title())
            # Use get_or_create by category and name to avoid duplicates
            obj, was_created = Service.objects.get_or_create(
                category=key,
                defaults={
                    'name': name,
                    'price': price,
                    'active': True,
                }
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created service: {obj.name} ({key}) - ₱{price:.2f}'))
            else:
                # If exists but price differs, update price
                if float(obj.price) != float(price):
                    obj.price = price
                    obj.active = True
                    obj.name = name
                    obj.save()
                    updated += 1
                    self.stdout.write(self.style.WARNING(f'Updated service price/name: {obj.name} ({key}) -> ₱{price:.2f}'))
        self.stdout.write(self.style.SUCCESS(f'Done. Created: {created}, Updated: {updated}'))
