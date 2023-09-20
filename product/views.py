import os, io
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category, ProductImages
from product.cart import Cart
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db.models import Q
from .forms import OrderForm
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from email.mime.image import MIMEImage

# Create your views here.
def home(request):
    categories = Category.objects.all()
    products = Product.objects.filter(isActive = True, isHome = True)

    context = {
        "categories": categories,
        "products": products,
    }

    return render(request, "product/index.html", context)

def products_by_category(request, c_slug):
    categories = Category.objects.all()
    products = Category.objects.get(categorySlug = c_slug).product_set.filter(isActive = True)

    sort_option = request.GET.get('sort', 'stock_asc')

    if sort_option == 'stock_asc':
        products = products.order_by('productStock')
    elif sort_option == 'stock_desc':
        products = products.order_by('-productStock')
    elif sort_option == 'price_asc':
        products = products.order_by('productPrice')
    elif sort_option == 'price_desc':
        products = products.order_by('-productPrice')

    context = {
        "categories": categories,
        "products": products,
        "selected_category": c_slug,
        "selected_sort_option": sort_option,
    }

    return render(request, "product/products.html", context)

def product_details(request, c_slug, p_slug):
    categories = Category.objects.all()
    product = Product.objects.get(productSlug = p_slug)
    images = ProductImages.objects.filter(product = product)

    context = {
        "categories": categories,
        "product": product,
        'images': images,
        "selected_category": c_slug,
    }

    return render(request, "product/product-details.html", context)

def search(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    search = request.GET.get("search")

    if search:
        products = Product.objects.filter(
            Q(productName__icontains=search) | 
            Q(productCode__icontains=search) | 
            Q(productCategory__categoryName__icontains = search)
        )[:1]
        if len(products) == 0:
            messages.error(request, "Ürün bulunamadı.")

    context = {
        "categories": categories,
        "products": products,
        "search": search,
    }

    return render(request, "product/search.html", context)

def cart_add(request, id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=id)
    quantity = int(request.POST["quantity"])
    selected_image_url = request.POST.get('selected_image_url')  # Get the selected image URL

    try:  
        cart.add(product=product,
                quantity=quantity,
                selected_image_url=selected_image_url,
                override_quantity=False
                )
        messages.success(request, "Ürün başarı ile eklendi.")

    except Exception as e:
        messages.error(request, "Ürün eklenirken bir hata oluştu. Lütfen tekrar deneyin.")

    return redirect("mail_order")

def cart_remove(request, id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=id)
        cart.remove(product)
        messages.success(request, "Ürün başarı ile silindi.")

    except Exception as e:
        messages.error(request, "Ürün silinirken bir hata oluştu. Lütfen tekrar deneyin.")

    return redirect("mail_order")

def cart_clear(request):
    try:
        cart = Cart(request)
        cart.clear()
        messages.success(request, "Sepet temizlendi.")

    except:
        messages.error(request, "Sepet temizlenirken bir hata oluştu. Lütfen tekrar deneyin.")

    return redirect("mail_order")

def mail_order(request):
    categories = Category.objects.all()

    context = {
        "categories": categories,
    }
    
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            personName = form.cleaned_data["kullanici_adi"]
            personSurname = form.cleaned_data["kullanici_soyadi"]
            personPhone = form.cleaned_data["kullanici_tel"]
            personMail = form.cleaned_data["kullanici_mail"]
            cart = Cart(request)

            if len(cart) > 0:
                subject = "Ürün Sipariş Bilgileri"
                plaintext_message = f"""
                Adı: {personName}<br>
                Soyadı: {personSurname}<br>
                Telefon No: {personPhone}<br>
                E-mail: {personMail}<br>

                Ürün Sipariş Detayları:<br><br>
                """

                email = EmailMultiAlternatives(
                subject,
                strip_tags(plaintext_message),
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_SEND_USER],
                )

                html_message = mark_safe(plaintext_message)
                for counter, item in enumerate(cart, start=1):
                    productCode = item["code"]
                    productName = item["name"]
                    productQuantity = item["quantity"]
                    
                    # Split the image URL by "/"
                    image_parts = item["image"].split("/")
                    del image_parts[0:2]

                    # Join the parts back together with "/"
                    modified_image_url = "/".join(image_parts)

                    # Construct the image URL using os.path.join and the MEDIA_URL setting
                    productImage = os.path.join(settings.MEDIA_ROOT, modified_image_url)

                    # Attach the image to the email using a CID (Content-ID)
                    with open(productImage, "rb") as image_file:
                        image_content = image_file.read()
                        image = MIMEImage(image_content)
                        image.add_header('Content-ID', f'<image_{counter}>')
                        image.add_header('Content-Disposition', 'inline')
                        email.attach(image)

                    html_message += f"""
                    No: {counter}<br>
                    Ürün Resmi: <img src="cid:image_{counter}" alt="{productName}" style="max-width: 100px; height: auto;"><br>
                    Ürün Kodu: {productCode}<br>
                    Ürün Adı: {productName}<br>
                    Miktar: {productQuantity}<br><br>
                    """

                try:
                    # Attach the HTML content with image references to the email
                    email.attach_alternative(html_message, "text/html")
                    email.send()
                    messages.success(request, "Siparişiniz başarıyla oluşturuldu. Teşekkür ederiz!")
                    cart.clear()

                except Exception as e:
                    messages.error(request, "Sipariş oluşturulurken bir hata oluştu. Lütfen tekrar deneyin.")

                return redirect("mail_order")
            
            else:
                messages.error(request, "Sepete ürün eklemediniz.")
        
        else:
            messages.error(request, "Form alanları boş bırakılamaz!")
            form = OrderForm()

    return render(request, "product/mail-order.html", context)
