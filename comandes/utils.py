def flatten(xss):
    return [x for xs in xss for x in xs]

def unique(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]

def get_request_type(request):
    http_accept = request.META.get("HTTP_ACCEPT", "")
    parts = [s.strip() for s in http_accept.split(";")]
    if 'application/json' in parts:
        return "json"
    else:
        return "html"
