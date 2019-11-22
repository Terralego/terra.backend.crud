import mimetypes
from copy import deepcopy
from pathlib import Path
from json import dumps, loads

import reversion
from django.conf import settings
from django.contrib.gis.geos import GeometryCollection
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.encoding import smart_text
from django.utils.translation import gettext as _
from django.views.generic.detail import DetailView
from geostore.models import Feature
from geostore.views import FeatureViewSet, LayerViewSet
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from . import models, serializers, settings as app_settings


def set_reversion_user(reversion, user):
    if not user.is_anonymous:
        reversion.set_user(user)


class ReversionMixin:
    def perform_create(self, serializer):
        with transaction.atomic(), reversion.create_revision():
            response = super().perform_create(serializer)
            set_reversion_user(reversion, self.request.user)
            return response

    def perform_update(self, serializer):
        with transaction.atomic(), reversion.create_revision():
            response = super().perform_update(serializer)
            set_reversion_user(reversion, self.request.user)
            return response


class CrudGroupViewSet(ReversionMixin, viewsets.ModelViewSet):
    queryset = models.CrudGroupView.objects.prefetch_related('crud_views__layer')
    serializer_class = serializers.CrudGroupSerializer


class CrudViewViewSet(ReversionMixin, viewsets.ModelViewSet):
    queryset = models.CrudView.objects.all()
    serializer_class = serializers.CrudViewSerializer


class CrudSettingsApiView(APIView):
    def get_menu_section(self):
        groups = models.CrudGroupView.objects.prefetch_related('crud_views__layer',
                                                               'crud_views__feature_display_groups')
        group_serializer = CrudGroupViewSet.serializer_class(groups, many=True)
        data = group_serializer.data

        # add non grouped views
        ungrouped_views = models.CrudView.objects.filter(group__isnull=True,
                                                         visible=True)\
            .select_related('layer')\
            .prefetch_related('feature_display_groups')
        views_serializer = CrudViewViewSet.serializer_class(ungrouped_views, many=True)
        data.append({
            "id": None,
            "name": _("Unclassified"),
            "order": None,
            "pictogram": None,
            "crud_views": views_serializer.data
        })
        return data

    def get(self, request, *args, **kwargs):
        default_config = deepcopy(app_settings.TERRA_GEOCRUD)
        default_config.update(getattr(settings, 'TERRA_GEOCRUD', {}))

        data = {
            "menu": self.get_menu_section(),
            "config": {
                "default": default_config,
                "attachment_categories": reverse('attachmentcategory-list'),
            }
        }
        return Response(data)


class CrudRenderTemplateDetailView(DetailView):
    model = Feature
    pk_template_field = 'pk'
    pk_template_kwargs = 'template_pk'

    def get_template_names(self):
        return self.template.template_file.name

    def get_template_object(self):
        return get_object_or_404(self.get_object().layer.crud_view.templates,
                                 **{self.pk_template_field:
                                    self.kwargs.get(self.pk_template_kwargs)})

    def render_to_response(self, context, **response_kwargs):
        self.template = self.get_template_object()
        self.content_type, _encoding = mimetypes.guess_type(self.get_template_names())
        response = super().render_to_response(context, **response_kwargs)
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_text(
            Path(self.template.template_file.name).name
        )
        return response

    def get_style(self, feature):
        style_map = feature.layer.crud_view.mblg_renderer_style
        geojson_id = 'primary'
        view = feature.layer.crud_view
        primary_layer = view.map_style_with_default
        primary_layer['id'] = geojson_id
        primary_layer['source'] = geojson_id
        style_map['sources'].update({geojson_id: {'type': 'geojson', 'data': loads(feature.geom.geojson)}})

        for i, extra_feature in enumerate(feature.extra_geometries.all()):
            layer_extra_geom = extra_feature.layer_extra_geom
            extra_style = extra_feature.layer_extra_geom.style.filter(crud_view=view)
            if extra_style and extra_style.first().map_style:
                extra_layer = extra_style.first().map_style
            else:
                extra_layer = models.get_default_style(layer_extra_geom)
            extra_id = extra_feature.layer_extra_geom.name
            extra_layer['id'] = extra_id
            extra_layer['source'] = extra_id
            style_map['sources'].update({extra_id: {'type': 'geojson', 'data': loads(extra_feature.geom.geojson)}})

            style_map['layers'].append(extra_layer)

        style_map['layers'].append(primary_layer)

        return style_map

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        feature = self.get_object()
        style = self.get_style(feature)
        token = app_settings.TERRA_GEOCRUD.get('TMP_MBGL_BASEMAP', {}).get('mapbox_access_token')
        context['style'] = {
            'style': dumps(style),
            'width': 1024,
            'height': 512,
            'token': token
        }

        if feature.layer.is_point and not feature.extra_geometries.exists():
            context['style']['zoom'] = app_settings.TERRA_GEOCRUD.get('MAX_ZOOM', 22)
            context['style']['center'] = list(feature.geom.centroid)
        else:
            geoms = feature.extra_geometries.values_list('geom', flat=True)
            collections = GeometryCollection(feature.geom, *geoms)
            context['style']['bounds'] = ','.join(str(v) for v in collections.extent)
        return context


class CrudLayerViewSet(LayerViewSet):
    permission_classes = []


class CrudFeatureViewSet(ReversionMixin, FeatureViewSet):
    permission_classes = []

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related('layer__crud_view__templates')

    def get_serializer_class(self):
        if self.action in ('retrieve', 'update', 'partial_update', 'create'):
            return serializers.CrudFeatureDetailSerializer
        return serializers.CrudFeatureListSerializer


class CrudAttachmentCategoryViewSet(ReversionMixin, viewsets.ModelViewSet):
    queryset = models.AttachmentCategory.objects.all()
    serializer_class = serializers.AttachmentCategorySerializer


class BehindFeatureMixin:
    """ Helper for Feature's related viewsets """
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ('legend', 'image')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.feature = None

    def get_feature(self):
        uuid = self.kwargs.get('identifier')
        if not self.feature and uuid:
            self.feature = get_object_or_404(Feature, identifier=uuid) if uuid else self.feature
        return self.feature

    def perform_create(self, serializer):
        serializer.save(feature=self.get_feature())


class CrudFeaturePictureViewSet(ReversionMixin, BehindFeatureMixin, viewsets.ModelViewSet):
    serializer_class = serializers.FeaturePictureSerializer

    def get_queryset(self):
        return self.get_feature().pictures.all()


class CrudFeatureAttachmentViewSet(ReversionMixin, BehindFeatureMixin, viewsets.ModelViewSet):
    serializer_class = serializers.FeatureAttachmentSerializer

    def get_queryset(self):
        return self.get_feature().attachments.all()
