from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_pptslide'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='api_universalcontent' AND column_name='vector') THEN
                    ALTER TABLE api_universalcontent ADD COLUMN vector vector;
                END IF;
            END
            $$;
            """,
            reverse_sql="""
            ALTER TABLE api_universalcontent DROP COLUMN IF EXISTS vector;
            """
        ),
    ]