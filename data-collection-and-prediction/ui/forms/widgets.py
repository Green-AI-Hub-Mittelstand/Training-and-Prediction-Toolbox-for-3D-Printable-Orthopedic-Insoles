from django import forms
from django.forms.widgets import TextInput

class CoordinateInput(TextInput):
    template_name = 'coordinate_widget.html'  # Create this template later

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        # Add any additional context variables needed for rendering the template
        return context