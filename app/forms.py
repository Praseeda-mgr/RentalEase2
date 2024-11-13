from django import forms
from .models import Property

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ('title', 'description', 'price', 'location', 'is_available', 'image')
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input bg-gray-100 border-2 border-gray-300 rounded-lg p-2 w-3/4 text-blue-600',
                'placeholder': 'Enter title here...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea bg-gray-100 border-2 border-gray-300 rounded-lg p-2 w-3/4 text-blue-600',
                'placeholder': 'Enter description here...',
                'rows': 4
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-input bg-gray-100 border-2 border-gray-300 rounded-lg p-2 w-3/4 text-blue-600',
                'placeholder': 'Enter price...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-input bg-gray-100 border-2 border-gray-300 rounded-lg p-2 w-3/4 text-blue-600',
                'placeholder': 'Enter location...'
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-checkbox rounded text-green-600',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-input bg-gray-100 border-2 border-gray-300 rounded-lg p-2 w-3/4',
            }),
        }