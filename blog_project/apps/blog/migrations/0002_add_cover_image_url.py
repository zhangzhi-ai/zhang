# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='cover_image_url',
            field=models.CharField(blank=True, help_text='外部图片URL或上传后的完整URL', max_length=500, verbose_name='封面图片URL'),
        ),
    ]

