# Generated by Django 2.2.16 on 2023-02-19 18:53

from django.db import migrations, models
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0010_auto_20230219_2105'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, user=django.db.models.expressions.F('author')), name='user_and_author_different'),
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='unique_follow'),
        ),
    ]