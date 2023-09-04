from django import template
from django.urls import reverse
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def breadcrumbs(request):
    breadcrumbs = []
    url = ''
    for part in request.path.split('/'):
        if part:
            url += f'/{part}'
            breadcrumbs.append((part, url))

    # Convert to HTML
    html = []
    for label, url in breadcrumbs:
        html.append(
            f'<li class="breadcrumb-item"><a href="{url}" class="text-decoration-none text-warning fw-normal">{conditional_escape(label)}</a></li>'
        )
    return mark_safe('\n'.join(html))
