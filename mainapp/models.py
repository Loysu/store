from PIL import Image

from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone


User = get_user_model()


class Category(models.Model):

    name = models.CharField(verbose_name = 'Имя категории', max_length = 250)
    slug = models.SlugField(unique = True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category_detail', kwargs = {'slug' : self.slug})

    def get_fields_for_filter_in_template(self):
        return ProductFeatures.objects.filter(
            category = self, use_in_filter = True
            ).prefetch_related('category').values('feature_key', 'feature_measure', 'feature_name', 'filter_type')


class Product(models.Model):

    MIN_RESOLUTION = (400, 300)
    MAX_RESOLUTION = (1400, 1000)
    MAX_IMAGE_SIZE = 3145728

    category = models.ForeignKey(Category, verbose_name = 'Категория', on_delete = models.CASCADE)
    title = models.CharField(verbose_name = 'Наименование', max_length = 250)
    slug = models.SlugField(unique = True)
    image = models.ImageField(verbose_name = 'Изображение')
    description = models.TextField(verbose_name = 'Описание', null = True)
    price = models.DecimalField(max_digits = 9, decimal_places = 2, verbose_name = 'Цена')
    features = models.ManyToManyField("specs.ProductFeature", blank=True, related_name='features_for_product')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        image = self.image
        img = Image.open(image)
        min_width, min_heigth = self.MIN_RESOLUTION
        max_width, max_heigth = self.MAX_RESOLUTION
        if image.size > self.MAX_IMAGE_SIZE:
            raise ValidationError('Размер файла не должен превышать 3МБ')
        if img.size[0] < min_width or img.size[1] < min_heigth:
            raise ValidationError('Разрешение изображения меньше минимального!')
        if img.size[0] > max_width or img.size[1] > max_heigth:
            raise ValidationError('Разрешение изображения больше максимального!')
    
        super().save(*args, **kwargs)
         
    def get_model_name(self):
        return self.__class__.__name__.lower()

    def get_absolute_url(self):
        return reverse('product_detail', kwargs = {'slug' : self.slug})

    def get_features(self):
        return {f.feature.feature_name: ' '.join([f.value, f.feature.unit or ""]) for f in self.features.all()}


class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name = 'Покупатель', on_delete = models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name = 'Корзина', on_delete = models.CASCADE, related_name = 'related_products')
    product = models.ForeignKey(Product, verbose_name = 'Товар', on_delete = models.CASCADE)
    qty = models.PositiveIntegerField(default = 1)
    final_price = models.DecimalField(max_digits = 9, decimal_places = 2, verbose_name = 'Общая цена')
    
    def __str__(self):
        return "Продукт {} (для корзины)".format(self.product.title)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.product.price
        super().save(*args, **kwargs)



class Cart(models.Model):

    owner = models.ForeignKey('Customer', null = True, verbose_name = 'Владелец', on_delete = models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank = True, related_name = 'related_cart')
    total_products = models.PositiveIntegerField(default = 0)
    final_price = models.DecimalField(max_digits = 9, default = 0, decimal_places = 2, verbose_name = 'Общая цена')
    in_order = models.BooleanField(default = False)
    for_anonymous_user = models.BooleanField(default = False)

    def __str__(self):
        return str(self.id)    


class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name = 'Пользователь', on_delete = models.CASCADE)
    phone = models.CharField(verbose_name = 'Номер телефона', max_length = 20, null = True, blank = True)
    address = models.CharField(verbose_name = 'Адресс', max_length = 255, null = True, blank = True)
    orders = models.ManyToManyField('Order', blank = True,verbose_name = 'Заказы покупателя', related_name = 'related_customer')

    def __str__(self):
        return 'Покупатель: {} {}'.format(self.user.first_name, self.user.last_name)


class Order(models.Model):

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'
    STATUS_PAYED = 'payed'

    BUYING_TYPE_SELF = 'self' # Самовывоз
    BUYING_TYPE_DELIVERY = 'delivery' # Доставка

    STATUS_CHOICES = (
        (STATUS_PAYED, 'Заказ оплачены'),
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов к получению'),
        (STATUS_COMPLETED, 'Заказ получен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')
    )

    customer = models.ForeignKey(Customer, verbose_name = 'Покупатель', related_name = 'related_orders' ,on_delete = models.CASCADE)
    first_name = models.CharField(verbose_name = 'Имя', max_length = 255)
    last_name = models.CharField(verbose_name = 'Фамилия', max_length = 255)
    phone = models.CharField(verbose_name = 'Номер телефона', max_length = 20)
    cart = models.ForeignKey(Cart, verbose_name = 'Корзина', on_delete = models.CASCADE, null = True, blank = True)
    address = models.CharField(verbose_name = 'Адресс доставки', max_length = 1024, null = True, blank = True)
    comment = models.TextField(verbose_name = 'Комментарий к заказу', null = True, blank = True)
    status = models.CharField(
        max_length = 100, 
        verbose_name = 'Статус заказа', 
        choices = STATUS_CHOICES, 
        default = STATUS_NEW
        )
    buying_type = models.CharField(
        verbose_name = 'Тип заказа',
        max_length = 100,
        choices = BUYING_TYPE_CHOICES,
        default = BUYING_TYPE_SELF
    )
    created_at = models.DateTimeField(auto_now = True, verbose_name = 'Дата создание заказа')
    order_date = models.DateField(verbose_name = 'Дата получения заказа', default = timezone.now)

    def __str__(self):
        return str(self.id)

