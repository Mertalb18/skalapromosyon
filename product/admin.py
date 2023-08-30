from django.contrib import admin
from .models import Category, Product
from django.utils.safestring import mark_safe

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

class CategoryAdmin(admin.ModelAdmin):
    list_display = ("categoryName", "categorySlug",)
    readonly_fields = ("categorySlug",)

# Register your models here.
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)