from django import forms
from accounts.models import Account
from category.models import Category
from store.models import Product

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control mb-3 mt-1 validate',}), max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control mt-1  validate',}), label="Password")




class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'is_admin', 'is_staff', 'is_superadmin','is_active']
        
    def __init__(self, *args, **kwargs):
        super(UserForm,self).__init__(*args, **kwargs)
        self.fields['phone_number'].widget.attrs['maxlength'] = 10
        
        for field  in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['is_admin'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_staff'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_superadmin'].widget.attrs['class'] = 'form-check-input'
        self.fields['is_admin'].widget.attrs['type'] = 'checkbox'
        self.fields['is_active'].widget.attrs['type'] = 'checkbox'
        self.fields['is_staff'].widget.attrs['type'] = 'checkbox'
        self.fields['is_superadmin'].widget.attrs['type'] = 'checkbox'    


class CategoryForm(forms.ModelForm):
    class Meta:
         model = Category
         fields = ['category_name', 'slug','description', 'cat_image',]
        
    def __init__(self, *args, **kwargs):
        super(CategoryForm,self).__init__(*args, **kwargs)
        for field  in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class ProductForm(forms.ModelForm):
    class Meta:
         model = Product
         fields = ['product_name', 'slug', 'description', 'price', 'stock', 'images','is_available', 'category']            