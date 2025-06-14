import importlib
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Seed database with random fake data"

    def handle(self, *args, **kwargs):
        modules_to_seed = {}
        for app in settings.INSTALLED_APPS:
            try:
                module_name = f"{app}.seed"
                if importlib.util.find_spec(module_name):
                    seed_module = importlib.import_module(module_name)
                    if not hasattr(seed_module, "run"):
                        continue
                    if hasattr(seed_module, "priority"):
                        priority = seed_module.priority
                    else:
                        priority = 0  # Default priority if not specified

                    if modules_to_seed.get(priority) is not None:
                        modules_to_seed[priority].append((app, seed_module))
                    else:
                        modules_to_seed[priority] = [(app, seed_module)]
            except ModuleNotFoundError:
                continue  # An app does not have a seed.py file

        if modules_to_seed:
            sorted_keys = sorted(modules_to_seed.keys(), key=int, reverse=True)
            for key in sorted_keys:
                self.stdout.write(f"\n🛠  Running seed files with priority {key}...")
                for app, seed_module in modules_to_seed[key]:
                    self.stdout.write(f"   Seeding APP: {app}...")
                    seed_module.run()

        self.stdout.write("\n✅  Seeding completed!")
