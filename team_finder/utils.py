from django.core.paginator import Paginator

from team_finder.constants import PAGE_SIZE


def paginate(request, objects):
    return Paginator(objects, PAGE_SIZE).get_page(
        request.GET.get("page")
    )
