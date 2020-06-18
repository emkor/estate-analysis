from datetime import datetime

from model import ParcelOffer
from place_resolver import build_resolve_name

OFFER_CSV_ROW = ["2020-04-16", "18:43:48", "www.olx.pl", "597681409", 1000, 169000,
                 "Gajków, wrocławski, Dolnośląskie",
                 "https://www.olx.pl/oferta/gajkow-dzialka-gotowa-do-budowy-super-miejsce-i-sasiedzi-CID3-IDErOeJ.html",
                 "Gajków działka gotowa do budowy,super miejsce i sąsiedzi"]
OFFER_MODEL = ParcelOffer(timestamp=datetime(2020, 4, 16, 18, 43, 48), ident="597681409",
                          url="https://www.olx.pl/oferta/gajkow-dzialka-gotowa-do-budowy-super-miejsce-i-sasiedzi-CID3-IDErOeJ.html",
                          location="Gajków, wrocławski, Dolnośląskie", area_m2=1000, price_pln=169000,
                          title="Gajków działka gotowa do budowy,super miejsce i sąsiedzi")


def test_should_parse_csv_row_into_model():
    offer = ParcelOffer.from_csv_row(OFFER_CSV_ROW)
    assert OFFER_MODEL == offer


def test_should_fmt_as_csv_row():
    csv_row = OFFER_MODEL.to_csv_row()
    assert OFFER_CSV_ROW == csv_row


def test_should_serialize_to_json_and_back():
    json_model = OFFER_MODEL.to_json()
    back_to_obj = ParcelOffer.from_json(json_model)

    assert OFFER_MODEL == back_to_obj


def test_should_dump_to_sql_row_and_back():
    sql_row = OFFER_MODEL.to_sql_row()
    parcel_offer = ParcelOffer.from_sql_row(sql_row)
    assert OFFER_MODEL == parcel_offer


def test_resolving_addresses():
    args = [("www.olx.pl", "Oleśnica, oleśnicki, Dolnośląskie, Oleśnica", "Oleśnica, oleśnicki"),
            ("www.olx.pl", "Milicz, milicki, Dolnośląskie", "Milicz, Dolnośląskie"),
            ("www.olx.pl", "Świerzów, trzebnicki, dolnośląskie", "Świerzów, trzebnicki"),
            ("www.otodom.pl", "ul. Wiśniowa, Wilkszyn, średzki, dolnośląskie", "Wilkszyn, średzki"),
            ("www.otodom.pl", "Kalinowa 7-9, Jary, trzebnicki, dolnośląskie", "Jary, trzebnicki"),
            ("www.olx.pl", "Nowosiedlice, gm. Dobroszyce, oleśnicki, Dolnośląskie", "Nowosiedlice, oleśnicki"),
            ("www.olx.pl", "Trzebnica, trzebnicki, Dolnośląskie", "Trzebnica, trzebnicki"),
            ("www.morizon.pl", "Oborniki Śląskie, Oborniki Śląskie, dolnośląskie", "Oborniki Śląskie, dolnośląskie"),
            ("www.morizon.pl", "Główna, Miękinia Zakrzyce, Miękinia, dolnośląskie", "Zakrzyce, Miękinia"),
            ("www.morizon.pl", "Świerkowa, miasto Kostomłoty, Kostomłoty, dolnośląskie", "Kostomłoty"),
            ("www.morizon.pl", "Jana III Sobieskiego, wrocławski, Żórawina, dolnośląskie", "Żórawina, wrocławski"),
            ]
    for domain, location, expected in args:
        actual = build_resolve_name(domain, location)
        assert actual.lower() == expected.lower(), f"{location} should be '{expected.lower()}', but was '{actual.lower()}'"
