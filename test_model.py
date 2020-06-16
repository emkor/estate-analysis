from datetime import datetime

from model import ParcelOffer

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
