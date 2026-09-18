from django.db import transaction
from django.db.models import F, Max, BigIntegerField
from django.db.models.functions import Cast, Substr
from django.utils import timezone


def next_reference(model, prefix):
    from accounts.models import ReferenceSequence

    year = timezone.localdate().year
    stem = f"{prefix}-{year}-"
    key = f"{model._meta.label_lower}:{stem}"
    counter, _ = ReferenceSequence.objects.get_or_create(key=key)
    with transaction.atomic():
        # Write first so SQLite serializes writers before reading the sequence.
        ReferenceSequence.objects.filter(pk=counter.pk).update(value=F("value") + 1)
        counter.refresh_from_db()
        highest = model.objects.filter(reference__startswith=stem).aggregate(
            value=Max(Cast(Substr("reference", len(stem) + 1), BigIntegerField()))
        )["value"] or 0
        sequence = max(counter.value, highest + 1)
        if sequence != counter.value:
            ReferenceSequence.objects.filter(pk=counter.pk).update(value=sequence)
    return f"{stem}{sequence:04d}"
