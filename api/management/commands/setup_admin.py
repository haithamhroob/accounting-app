import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'ينشئ حساب مدير تلقائياً بناءً على متغيرات البيئة'

    def handle(self, *args, **options):
        # 1. قراءة البيانات من متغيرات البيئة (سيقوم المستخدم بضبطها في Render)
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')

        self.stdout.write(f'محاولة إنشاء مستخدم: {username}...')

        # 2. التحقق أو الإنشاء
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'المستخدم {username} موجود بالفعل. لن يتم تغييره.'))
        else:
            try:
                User.objects.create_superuser(username=username, email=email, password=password)
                self.stdout.write(self.style.SUCCESS(f'تمت العملية! المستخدم {username} جاهز للعمل.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'فشلت العملية: {str(e)}'))
