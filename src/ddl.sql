CREATE TABLE IF NOT EXISTS place
(
    location VARCHAR PRIMARY KEY,
    city     VARCHAR,
    postcode VARCHAR,
    lat      FLOAT,
    lon      FLOAT
);

CREATE TABLE IF NOT EXISTS parcel_offer
(
    ident     VARCHAR                             NOT NULL,
    timestamp TIMESTAMP WITHOUT TIME ZONE         NOT NULL,
    url       VARCHAR(2000)                       NOT NULL,
    title     VARCHAR(1000)                       NOT NULL,
    location  VARCHAR REFERENCES place (location) NOT NULL,
    area_m2   INT                                 NOT NULL,
    price_pln FLOAT                               NOT NULL,
    CONSTRAINT parcel_offer_pk PRIMARY KEY (ident, timestamp)
);

CREATE INDEX IF NOT EXISTS title_ix ON parcel_offer (title);
CREATE INDEX IF NOT EXISTS area_ix ON parcel_offer (area_m2);
CREATE INDEX IF NOT EXISTS price_ix ON parcel_offer (price_pln);
CREATE INDEX IF NOT EXISTS timestamp_ix ON parcel_offer (timestamp);
CREATE INDEX IF NOT EXISTS city_ix ON place (city);
CREATE INDEX IF NOT EXISTS postcode_ix ON place (postcode);

CREATE VIEW IF NOT EXISTS daily_price_avg AS
SELECT date(timestamp), round(avg(price_pln / area_m2)), count(DISTINCT ident)
FROM parcel_offer
GROUP BY date(timestamp)
ORDER BY date(timestamp);

CREATE VIEW IF NOT EXISTS latest_offers AS
SELECT date_part('day', age(max(o.timestamp), min(OfferHistory."FirstOffer")))      AS "Age",
       min(p.city) AS "City",
       min(o.location) AS "Location",
       round(min(o.price_pln) / min(o.area_m2))                                     AS "PricePerSqM",
       round(min(o.area_m2) / 100)                                                  AS "Area",
       max(CityAvgPrice."AvgPricePerM2") - round(min(o.price_pln) / min(o.area_m2)) AS "CheaperThanCityAvg",
       round(max(OfferHistory."HighestPrice") - min(o.price_pln))                   AS "PriceDrop",
       min(o.ident) AS "ID",
       o.url AS "URL",
       min(p.lat) AS "Lat",
       min(p.lon) AS "Lon"
FROM parcel_offer AS o
         LEFT JOIN place p on o.location = p.location
         LEFT JOIN (SELECT city,
                           round(avg(price_pln / area_m2)) AS "AvgPricePerM2"
                    FROM parcel_offer
                             LEFT JOIN place ON parcel_offer.location = place.location
                    WHERE price_pln / area_m2 < 1000
                      AND price_pln / area_m2 > 10
                    GROUP BY city
                    HAVING count(DISTINCT ident) >= 2
                    ORDER BY round(avg(price_pln / area_m2)) DESC) AS CityAvgPrice ON p.city = CityAvgPrice.city
         LEFT JOIN (SELECT ident,
                           MIN(url),
                           MIN(timestamp) AS "FirstOffer",
                           MAX(timestamp) AS "LastOffer",
                           MAX(price_pln) AS "HighestPrice",
                           MIN(price_pln) AS "LowestPrice",
                           MIN(area_m2)   AS "Area"
                    FROM parcel_offer
                    GROUP BY ident) AS OfferHistory ON o.ident = OfferHistory.ident
WHERE date(o.timestamp) = date(now())
GROUP BY o.url
ORDER BY min(p.city), round(min(o.price_pln) / min(o.area_m2)), date_part('day', age(max(o.timestamp), min(OfferHistory."FirstOffer")));

CREATE VIEW IF NOT EXISTS "avg_city_price" AS
SELECT city,
       round(avg(price_pln / area_m2)) AS "AvgPricePerM2",
       min(lat)                        AS "lat",
       min(lon)                        AS "lon",
       count(url)                      AS "count"
FROM (SELECT url,
             min(ident)     "ident",
             max(timestamp) "timestamp",
             min(price_pln) "price_pln",
             min(area_m2)   "area_m2",
             min(location)  "location"
      FROM parcel_offer
      GROUP BY url) AS offer
         LEFT JOIN place ON offer.location = place.location
WHERE offer.price_pln / offer.area_m2 < 1000
  AND offer.price_pln / offer.area_m2 > 5
GROUP BY city
HAVING count(DISTINCT ident) >= 2
ORDER BY city;