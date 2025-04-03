import string
from functools import cached_property

import requests
from lxml import etree
from tqdm import tqdm

from . import db
from .xpath import xpath, xpath_int, xpath_one, xpath_text

URL = "https://service.gdi-sh.de/SH_INSPIREDOWNLOAD_AI_AD"


class Member:
    def __init__(self, member):
        self.root = xpath_one(member, self.typename)

    @property
    def id(self):
        return xpath_text(self.root, "gml:identifier")


class Postcode(Member):
    typename = "ad:PostalDescriptor"
    alphabet = string.digits

    @property
    def code(self):
        return xpath_text(self.root, "ad:postCode")

    @property
    def city(self):
        return xpath_text(self.root, ".//gn:text")

    def to_db(self):
        return db.Postcode(id=self.id, code=self.code, city=self.city)


class Street(Member):
    typename = "ad:ThoroughfareName"
    alphabet = string.digits

    @property
    def name(self):
        return xpath_text(self.root, ".//gn:text")

    def to_db(self):
        return db.Street(id=self.id, name=self.name)


class Address(Member):
    typename = "ad:Address"
    alphabet = string.digits + string.ascii_letters

    @property
    def postcode(self):
        return xpath_text(
            self.root,
            "ad:component/@xlink:href[contains(., 'PostalDescriptor')]",
            optional=True,
        )

    @property
    def street(self):
        return xpath_text(
            self.root,
            "ad:component/@xlink:href[contains(., 'ThoroughfareName')]",
            optional=False,
        )

    @property
    def number(self):
        return xpath_int(
            self.root,
            ".//ad:designator"  #
            "[re:test(../ad:type/@xlink:href, 'addressNumber$')]",
            optional=False,
        )

    @property
    def extension(self):
        return xpath_text(
            self.root,
            ".//ad:designator"
            "[re:test(../ad:type/@xlink:href, 'addressNumberExtension$')]",
            optional=True,
        )

    @property
    def lat(self):
        point = xpath_text(self.root, ".//gml:pos")
        return float(point.split()[0])

    @property
    def lon(self):
        point = xpath_text(self.root, ".//gml:pos")
        return float(point.split()[1])

    def to_db(self):
        return db.Address(
            id=self.id,
            postcode=self.postcode,
            street=self.street,
            number=self.number,
            extension=self.extension,
            lat=self.lat,
            lon=self.lon,
        )


class Query:
    def __init__(self, cls, suffix):
        self.suffix = suffix
        self.cls = cls

    def split(self):
        for character in self.cls.alphabet:
            yield Query(self.cls, character + self.suffix)

    @cached_property
    def count(self):
        query = f"""
        <wfs:GetFeature
         service='WFS'
         version='2.0.0'
         resultType='hits'
         xmlns:fes='http://www.opengis.net/fes/2.0'
         xmlns:gml='http://www.opengis.net/gml/3.2'
         xmlns:wfs='http://www.opengis.net/wfs/2.0'
         xmlns:ad='http://inspire.ec.europa.eu/schemas/ad/4.0'>
            <wfs:Query typeNames='{self.cls.typename}' srsName='EPSG:4326'>
                <fes:Filter>
                    <fes:PropertyIsLike wildCard='%' singleChar='_' escapeChar='\\'>
                        <fes:ValueReference>gml:identifier</fes:ValueReference>
                        <fes:Literal>%{self.suffix}</fes:Literal>
                    </fes:PropertyIsLike>
                </fes:Filter>
            </wfs:Query>
        </wfs:GetFeature>"""

        response = requests.post(URL, query)
        root = etree.XML(response.content)

        return xpath_int(root, "@numberMatched")

    @cached_property
    def members(self):
        query = f"""
        <wfs:GetFeature
         service='WFS'
         version='2.0.0'
         xmlns:fes='http://www.opengis.net/fes/2.0'
         xmlns:gml='http://www.opengis.net/gml/3.2'
         xmlns:wfs='http://www.opengis.net/wfs/2.0'
         xmlns:ad='http://inspire.ec.europa.eu/schemas/ad/4.0'>
            <wfs:Query typeNames='{self.cls.typename}' srsName='EPSG:4326'>
                <fes:Filter>
                    <fes:PropertyIsLike wildCard='%' singleChar='_' escapeChar='\\'>
                        <fes:ValueReference>gml:identifier</fes:ValueReference>
                        <fes:Literal>%{self.suffix}</fes:Literal>
                    </fes:PropertyIsLike>
                </fes:Filter>
            </wfs:Query>
        </wfs:GetFeature>"""

        response = requests.post(URL, query)
        root = etree.XML(response.content)

        for member in xpath(root, "wfs:member"):
            if len(member) == 0:
                continue

            yield self.cls(member)


class Harvester:
    def __init__(self, cls, session):
        self.session = session
        self.cls = cls

        self.queries = []

    @cached_property
    def max_count(self):
        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetCapabilities",
        }

        response = requests.get(URL, params)
        root = etree.XML(response.content)

        return xpath_int(
            root,
            ".//ows:Constraint"  #
            "[@name='CountDefault']"
            "/ows:DefaultValue",
        )

    def find(self):
        query = Query(self.cls, "")
        queries = query.split()
        queries = list(queries)

        while queries:
            query = queries.pop()

            if query.count == 0:
                continue

            if query.count > self.max_count:
                queries.extend(query.split())
                continue

            self.queries.append(query)

    def run(self):
        for query in tqdm(self.queries):
            for member in query.members:
                self.session.add(member.to_db())

            self.session.commit()
