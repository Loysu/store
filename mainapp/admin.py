from django.contrib import admin
from django.forms import ModelForm, ValidationError
from django.utils.safestring import mark_safe
from PIL import Image

from .models import Cart, CartProduct, Category, Customer, Order, Product


class ProductAdminForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["image"].help_text = mark_safe(
            """<span style = "color : red; font-size : 14px;">Изображение должно быть больше чем {}x{}px, но меньше чем {}x{}px!</span>""".format(
                *Product.MIN_RESOLUTION, *Product.MAX_RESOLUTION
            )
        )

    def clean_image(self):
        image = self.cleaned_data["image"]
        img = Image.open(image)
        min_width, min_heigth = Product.MIN_RESOLUTION
        max_width, max_heigth = Product.MAX_RESOLUTION
        if image.size > Product.MAX_IMAGE_SIZE:
            raise ValidationError("Размер файла не должен превышать 3МБ")
        if img.size[0] < min_width or img.size[1] < min_heigth:
            raise ValidationError("Разрешение изображения меньше минимального!")
        if img.size[0] > max_width or img.size[1] > max_heigth:
            raise ValidationError("Разрешение изображения больше максимального!")
        return image


class ProductAdmin(admin.ModelAdmin):
    change_form_template = "custom_admin/change_form.html"
    # exclude = ('features',)


admin.site.register(Category)
admin.site.register(CartProduct)
admin.site.register(Cart)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Product, ProductAdmin)
