from django import template

register = template.Library()


@register.filter
def addclass(field, css):
    """Фильтр для добавления класса (для форм) в заголовок в HTML шаблоне"""
    return field.as_widget(attrs={'class': css})
