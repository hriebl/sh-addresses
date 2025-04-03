NAMESPACES = {
    "re": "http://exslt.org/regular-expressions",
    "ad": "http://inspire.ec.europa.eu/schemas/ad/4.0",
    "gn": "http://inspire.ec.europa.eu/schemas/gn/4.0",
    "gml": "http://www.opengis.net/gml/3.2",
    "ows": "http://www.opengis.net/ows/1.1",
    "wfs": "http://www.opengis.net/wfs/2.0",
    "xlink": "http://www.w3.org/1999/xlink",
}


def xpath(x, path):
    return x.xpath(path, namespaces=NAMESPACES)


def xpath_one(x, path, optional=False):
    results = xpath(x, path)

    if len(results) == 1:
        return results[0]

    if len(results) == 0 and optional:
        return None

    raise ValueError


def xpath_text(x, path, optional=False):
    result = xpath_one(x, path, optional)

    if isinstance(result, str):
        return result

    if result is None:
        return None

    return result.text


def xpath_int(x, path, optional=False):
    result = xpath_text(x, path, optional)

    if result is None:
        return None

    return int(result)
