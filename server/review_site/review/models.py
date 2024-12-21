from django.db import models


class QualityIndex(models.Model):
    id_index = models.AutoField(primary_key=True)
    quality_index = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateTimeField()

    class Meta:
        db_table = 'quality_index'


class Review(models.Model):
    id_review = models.AutoField(primary_key=True)
    text = models.CharField(max_length=10000)
    data_time = models.DateTimeField()
    class_field = models.CharField(db_column='class', max_length=50, blank=True, null=True)  # Field renamed because it was a Python reserved word.

    class Meta:
        db_table = 'review'
