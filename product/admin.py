from django.contrib import admin
from .models import Category, Product, Image
from django.utils.safestring import mark_safe

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("productCode", "productName", "productSlug", "isActive", "isHome", "selected_categories",)
    list_editable = ("isActive", "isHome",)
    readonly_fields = ("productSlug",)
    list_filter = ("productCategory", "isActive", "isHome",)

    def selected_categories(self, obj):  # Many to Many ilişkisi
        html = "<ul>"

        for category in obj.productCategory.all():
            html += "<li>" + category.categoryName + "</li>"

        html += "</ul>"
        return mark_safe(html)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("categoryName", "categorySlug",)
    readonly_fields = ("categorySlug",)

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("product",)