import csv
import os

import requests

API_KEY = os.environ["GOOGLE_MAPS_API_KEY"]

FIELD_MASK = "places.displayName,places.formattedAddress,places.location,places.primaryType"


def search_text(text_query: str) -> dict:
    """Call the Places API (New) Text Search endpoint."""
    response = requests.post(
        "https://places.googleapis.com/v1/places:searchText",
        json={"textQuery": text_query},
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": API_KEY,
            "X-Goog-FieldMask": FIELD_MASK,
        },
    )
    response.raise_for_status()
    return response.json()


# Add your ~20 location search queries here.
QUERIES = [
    "Ngõ chợ Đồng Xuân, Hoàn Kiếm, Hà Nội",
    "Bún chả Hàng Quạt, Ngõ 74 Hàng Quạt, Hoàn Kiếm, Hà Nội",
    "Phở 10 Lý Quốc Sư, 10 Lý Quốc Sư, Hoàn Kiếm, Hà Nội",
    "Bún đậu mắm tôm Hàng Khay, Ngõ 31 Hàng Khay, Cửa Nam, Hà Nội",
    "Bún thang Bà Đức, 48 Cầu Gỗ, Hoàn Kiếm, Hà Nội",
    "Bò nướng Mã Mây, 47 Mã Mây, Hoàn Kiếm, Hà Nội",
    "Phở Bát Đàn, 49 Bát Đàn, Hoàn Kiếm, Hà Nội",
    "Chả cá Lã Vọng, 14 Chả Cá, Hoàn Kiếm, Hà Nội",
    "Chè 4 Mùa, 4 Hàng Cân, Hoàn Kiếm, Hà Nội",
    "Cafe trứng Giảng, 39 Nguyễn Hữu Huân, Hoàn Kiếm, Hà Nội",
    "Kem Tràng Tiền, 35 Tràng Tiền, Cửa Nam, Hà Nội",
    "Nộm bò khô, 23 Hồ Hoàn Kiếm, Hà Nội",
    "Bánh đậu đỏ, 22 Hàng Buồm, Hoàn Kiếm, Hà Nội",
    "Kem chanh bạc hà, 2 Phường Lê Thái Tổ, Hoàn Kiếm, Hà Nội",
    "Always Cafe (Bia Bơ), 8B Hàng Tre, Hoàn Kiếm, Hà Nội",
    "Bún riêu Hàng Bồ, 51 Hàng Bồ, Hoàn Kiếm, Hà Nội",
    "24 Hàng Bồ, Hoàn Kiếm, Hà Nội",
    "Phở Gánh Hàng Chiếu, Hoàn Kiếm, Hà Nội",
    "Xôi Yến, 35b Nguyễn Hữu Huân, Hoàn Kiếm, Hà Nội",
]


def build_location_table(queries: list[str]) -> list[dict]:
    """Query Places API for each entry and assemble the location table."""
    rows = []
    for query in queries:
        result = search_text(query)
        places = result.get("places", [])
        if not places:
            print(f"No result for query: {query!r}")
            continue
        place = places[0]
        location = place.get("location", {})
        rows.append(
            {
                "location_name": place.get("displayName", {}).get("text", query),
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "source_note": f"Google Places API Text Search - query: '{query}'",
            }
        )
    return rows


def write_csv(rows: list[dict], path: str = "locations.csv") -> None:
    fieldnames = ["location_name", "latitude", "longitude", "source_note"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    location_rows = build_location_table(QUERIES)
    write_csv(location_rows)
    print(f"Wrote {len(location_rows)} locations to locations.csv")
