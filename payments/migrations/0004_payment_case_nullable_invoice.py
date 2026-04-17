import django.db.models.deletion
from django.db import migrations, models


def populate_payment_case(apps, schema_editor):
    Payment = apps.get_model('payments', 'Payment')
    for payment in Payment.objects.select_related('invoice', 'invoice__case').all():
        if payment.case_id:
            continue
        invoice = payment.invoice
        if invoice and invoice.case_id:
            payment.case_id = invoice.case_id
            payment.save(update_fields=['case'])


class Migration(migrations.Migration):

    dependencies = [
        ('cases', '0003_case_client_name'),
        ('payments', '0003_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='invoice',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payments',
                to='payments.invoice',
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='case',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='payments',
                to='cases.case',
            ),
        ),
        migrations.RunPython(populate_payment_case, migrations.RunPython.noop),
    ]
