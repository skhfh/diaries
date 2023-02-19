from django.core.paginator import Paginator


def paginator(request, some_list, number_of_elements):
    pagination = Paginator(some_list, number_of_elements)
    page_number = request.GET.get('page')
    page_obj = pagination.get_page(page_number)
    return page_obj
