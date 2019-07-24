from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _


class CrudModelMixin(models.Model):
    name = models.CharField(max_length=100, unique=True)
    order = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class CrudGroupView(CrudModelMixin):
    pictogram = models.ImageField(upload_to='crud/groups/pictograms', null=True, blank=True)

    class Meta:
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
        ordering = ('order', )


class CrudView(CrudModelMixin):
    group = models.ForeignKey(CrudGroupView, on_delete=models.PROTECT, related_name='crud_views')
    layer = models.OneToOneField('terra.Layer', on_delete=models.CASCADE, related_name='crud_view')
    # TODO : wait for terra MR that set group in instance
    # tile_group = models.ForeignKey('terra.VTGroup', on_delete=models.CASCADE, related_name='crud_views')
    pictogram = models.ImageField(upload_to='crud/views/pictograms', null=True, blank=True)
    map_style = JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = _("View")
        verbose_name_plural = _("Views")
        ordering = ('order',)
