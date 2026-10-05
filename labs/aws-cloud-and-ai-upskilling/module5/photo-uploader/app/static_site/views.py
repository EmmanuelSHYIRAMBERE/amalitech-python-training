from django.conf import settings
from django.http import HttpResponse

_INDEX_HTML_PATH = settings.BASE_DIR / "public" / "index.html"


def index_view(request):
    html = _INDEX_HTML_PATH.read_text(encoding="utf-8")
    return HttpResponse(html, content_type="text/html")
