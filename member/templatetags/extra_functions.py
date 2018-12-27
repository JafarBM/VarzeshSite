from django import template

register = template.Library()


@register.simple_tag
def set_class(element, clas):
    return element.as_widget(attrs={'class': clas})
