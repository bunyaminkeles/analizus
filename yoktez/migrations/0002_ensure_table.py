"""
Yoktez tablosunun gerçekten var olduğunu garanti eder.
0001_initial migration kaydı var ama tablo oluşmamış durumu için.
CREATE TABLE IF NOT EXISTS ile güvenli şekilde tablo oluşturur.
"""
from django.db import migrations


CREATE_SQL = """
CREATE TABLE IF NOT EXISTS yoktez_yoktezsearchjob (
    id uuid NOT NULL PRIMARY KEY,
    user_id bigint NOT NULL REFERENCES auth_user(id) DEFERRABLE INITIALLY DEFERRED,
    tez_ad varchar(300) NOT NULL DEFAULT '',
    yazar varchar(200) NOT NULL DEFAULT '',
    danisman varchar(200) NOT NULL DEFAULT '',
    universite varchar(200) NOT NULL DEFAULT '',
    tur varchar(10) NOT NULL DEFAULT '',
    yil_baslangic integer NULL,
    yil_bitis integer NULL,
    metin varchar(300) NOT NULL DEFAULT '',
    status varchar(20) NOT NULL DEFAULT 'pending',
    total_results integer NOT NULL DEFAULT 0,
    demo_results jsonb NOT NULL DEFAULT '[]',
    all_results_file_url varchar(500) NOT NULL DEFAULT '',
    demo_email_sent boolean NOT NULL DEFAULT false,
    error_message text NOT NULL DEFAULT '',
    created_at timestamptz NOT NULL,
    completed_at timestamptz NULL
);
CREATE INDEX IF NOT EXISTS yoktez_yoktezsearchjob_user_id
    ON yoktez_yoktezsearchjob (user_id);
CREATE INDEX IF NOT EXISTS yoktez_yoktezsearchjob_created_at
    ON yoktez_yoktezsearchjob (created_at DESC);
"""


class Migration(migrations.Migration):

    dependencies = [
        ('yoktez', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql=CREATE_SQL,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
