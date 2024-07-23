from .models import *
from django import forms
from django.utils.translation import gettext_lazy as _
from bootstrap5.widgets import RadioSelectButtonGroup

from django.forms.widgets import TextInput
from django.utils.html import format_html
from django.utils.safestring import mark_safe


class CustomButtonTextInput(TextInput):
    
    def __init__(self, button_action, button_text='Custom Button', button_class="data-copy-button", *args, **kwargs):
        self.button_text = button_text
        self.button_class = button_class
        self.button_action = button_action
        
        super().__init__(*args, **kwargs)
        
    
    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs)

        button_html = '''
            <button type="button" data-action="{3}" class="btn btn-sm btn-secondary {2}" data-input-id="{0}">
                {1} 
            </button>
        '''.format(attrs['id'], self.button_text, self.button_class, self.button_action)
        
        try:
            help_text = self.attrs.get('help_text', '')
        except:
            help_text="-"
            
        if help_text:
            help_html = '<span class="helptext">{}</span>'.format(help_text)
        else:
            help_html = ''

        return mark_safe('{}{}{}'.format(button_html, input_html, help_text))


class InsoleParameterForm(forms.ModelForm):
    
    laenge_der_einlage = forms.IntegerField(
        
        widget=CustomButtonTextInput("length","Länge übernehmen (Punkt Distanz, ohne 10mm)")        
    )
    
    breit_der_einlage_im_vorfussbereich = forms.IntegerField(
        
        widget=CustomButtonTextInput("front-width","Breite übernehmen")        
    )
    
    breite_der_einlage_im_rueckfussbereich = forms.IntegerField(
        
        widget=CustomButtonTextInput("back-width","Breite übernehmen")        
    )
    
    pass
        
   
    
class InsoleParameterFormLeft(InsoleParameterForm):
    class Meta:
        model = InsoleParameterLeft
        fields = "__all__"
        exclude = ('participant',)

class InsoleParameterFormRight(InsoleParameterForm):
    class Meta:
        model = InsoleParameterRight
        fields = "__all__"
        exclude = ('participant',)
    