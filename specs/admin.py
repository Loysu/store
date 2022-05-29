from django.contrib import admin

from .models import CategoryFeature, FeatureValidator, ProductFeature

admin.site.register(ProductFeature)
admin.site.register(CategoryFeature)
admin.site.register(FeatureValidator)
