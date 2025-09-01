from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='dice_preset',
            field=models.CharField(choices=[('amethyst', 'Amethyst'), ('emerald', 'Emerald'), ('ruby', 'Ruby'), ('sapphire', 'Sapphire'), ('obsidian', 'Obsidian'), ('ivory', 'Ivory'), ('gold', 'Gold'), ('pumpkin', 'Pumpkin')], default='amethyst', max_length=24),
        ),
        migrations.AddField(
            model_name='user',
            name='dice_finish',
            field=models.CharField(choices=[('matte', 'Matte'), ('glossy', 'Glossy'), ('pearl', 'Pearl')], default='glossy', max_length=16),
        ),
        migrations.AddField(
            model_name='user',
            name='dice_external_theme_url',
            field=models.URLField(blank=True, default=''),
        ),
    ]

