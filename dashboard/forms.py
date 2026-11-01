from django import forms

from .models import Position, Share


class ShareModelForm(forms.ModelForm):
    """Инструмент"""

    class Meta:
        model = Share
        fields = "__all__"


class PositionModelForm(forms.ModelForm):
    """Позиция"""

    class Meta:
        model = Position
        fields = ("share", "quantity", "purchase_price")
