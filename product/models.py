import os
from django.db import models
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.validators import MinValueValidator
import random
from django.urls import reverse
from django.db.models.signals import post_delete

# Create your models here.
class Category(models.Model):
    categoryName = models.CharField(max_length=150, verbose_name="Kategori Adı")
    categorySlug = models.SlugField(null=False, blank=True, unique=True, db_index=True, editable=False)

    def __str__(self):
        return self.categoryName
    
    def save(self, *args, **kwargs):
        self.categorySlug = slugify(self.categoryName)
        super().save(*args, **kwargs)

    def get_random_product_image_url(self):
        products = self.product_set.all()
        if products:
            random_product = random.choice(products)
            return random_product.productImage.url
        return None
    
    def get_absolute_url(self):
        return reverse('products_by_category', args=[str(self.categoryName)])

class Product(models.Model):
    productCode = models.CharField(max_length = 200, verbose_name = "Ürün Kodu", unique = True)
    productName = models.CharField(max_length = 200, verbose_name = "Ürün Adı")
    productPrice = models.DecimalField(max_digits = 10, decimal_places = 2)
    productStock = models.IntegerField(default = 1, validators=[MinValueValidator(1)])
    productImage = models.ImageField(upload_to = "products", verbose_name = "Ürün Resmi")
    productInfo = models.TextField(verbose_name = "Ürün Açıklaması")
    isActive = models.BooleanField(default = False, verbose_name = "Yayınla")
    isHome = models.BooleanField(default = False, verbose_name = "Anasayfada Göster")
    productSlug = models.SlugField(null = False, blank = True, unique = True, db_index = True, editable = False)
    productCategory = models.ManyToManyField(Category, verbose_name="Kategoriler")

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.productName
    
    def save(self, *args, **kwargs):
        self.productSlug = slugify(self.productName)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the main image first
        if self.productImage:
            try:
                os.remove(self.productImage.path)
            except FileNotFoundError:
                pass

        # Delete all images associated with the product
        for image in self.images.all():
            image.delete()

        super().delete(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_details', args=[str(self.productCategory.categoryName), str(self.productName)])
    
class Image(models.Model):
    product = models.ForeignKey(Product, verbose_name = "Ürün Kodu", on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to = "products")

@receiver(post_delete, sender=Image)
def delete_image_file(sender, instance, **kwargs):
    # Delete the associated image file from storage
    if instance.image:
        try:
            os.remove(instance.image.path)
        except FileNotFoundError:
            pass