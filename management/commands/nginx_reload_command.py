import subprocess
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Run a command with sudo'

    def handle(self, *args, **options):
        try:
            # Execute your sudo command here
            subprocess.run(["sudo", "nginx", "-s", "reload"])
            self.stdout.write(self.style.SUCCESS('Command executed with sudo'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
