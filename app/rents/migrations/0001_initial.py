import django.db.models.deletion

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('model', models.CharField()),
                ('brand', models.CharField()),
                ('price_per_hour', models.FloatField()),
                ('is_rent', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Rent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_at', models.DateTimeField()),
                ('finish_at', models.DateTimeField(blank=True, null=True)),
                ('price', models.FloatField(null=True)),
                ('paid', models.BooleanField(default=False)),
                ('bike', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='rents.bike')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
