from django.forms import RadioSelect


class ColorRadioSelect(RadioSelect):
    template_name = 'widgets/radio.html'
    option_template_name = 'widgets/radio_option.html'
