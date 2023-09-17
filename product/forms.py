from django import forms

class OrderForm(forms.Form):
    kullanici_adi = forms.CharField(max_length=100, label='Adı')
    kullanici_soyadi = forms.CharField(max_length=100, label='Soyadı')
    kullanici_tel = forms.CharField(max_length=15, label='Telefon')
    kullanici_mail = forms.EmailField(label='E-mail')