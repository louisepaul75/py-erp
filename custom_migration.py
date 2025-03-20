Loading environment from /Users/joan/VSProjects/pyERP/config/env/.env.dev
Database settings: NAME=pyerp_testing, HOST=192.168.73.65, USER=postgres
Database password is set
class Migration(migrations.Migration):
    dependencies = [("products", "0001_initial")]
    operations = [migrations.RunSQL("ALTER TABLE products_parentproduct ALTER COLUMN dimensions DROP NOT NULL;"),]
