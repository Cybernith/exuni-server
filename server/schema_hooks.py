def filter_store_endpoints(endpoints):
    return [
        (path, path_regex, method, callback)
        for (path, path_regex, method, callback) in endpoints
        if path.startswith('/login') or path.startswith('/users/')
    ]
