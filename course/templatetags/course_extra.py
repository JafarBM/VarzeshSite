from django import template

register = template.Library()


@register.filter(name='get_keys_list')
def get_keys_list(dictionary):
    return [*dictionary]


@register.filter(name='get_key')
def get_key(dictionary, key):
    return dictionary[key]
