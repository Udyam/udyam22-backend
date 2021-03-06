# Generated by Django 3.2.7 on 2021-11-15 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=60, unique=True, verbose_name='email')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=100)),
                ('college_name', models.CharField(max_length=200)),
                ('year', models.CharField(choices=[('ONE', '1st year'), ('TWO', '2nd year'), ('THREE', '3rd year'), ('FOUR', '4th year')], max_length=20)),
                ('user_referral_code', models.CharField(max_length=10)),
                ('referral_code', models.CharField(blank=True, max_length=10, null=True)),
                ('referral_count', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
