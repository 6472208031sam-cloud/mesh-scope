#!/usr/bin/env python3
"""Fetch Meshtastic nodes from the public map API, keep the GTA ones.

Data: https://meshtastic.liamcottle.net (public, no key). Coordinates are
integers scaled by 1e7. Only nodes with map reporting enabled appear at all.
"""
import json, urllib.request, datetime, os

API = "https://meshtastic.liamcottle.net/api/v1/nodes"
# GTA bbox: 43.3-44.0 N, 80.2-78.9 W (scaled x1e7)
LAT_MIN, LAT_MAX = 433_000_000, 440_000_000
LNG_MIN, LNG_MAX = -802_000_000, -789_000_000
HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    req = urllib.request.Request(API, headers={"User-Agent": "mesh-scope/1.0"})
    with urllib.request.urlopen(req, timeout=90) as r:
        data = json.load(r)
    nodes = data.get("nodes", [])
    gta = []
    for n in nodes:
        lat, lng = n.get("latitude"), n.get("longitude")
        if lat is None or lng is None:
            continue
        if not (LAT_MIN <= lat <= LAT_MAX and LNG_MIN <= lng <= LNG_MAX):
            continue
        gta.append({
            "id": n.get("node_id"),
            "name": n.get("long_name") or n.get("short_name") or "unknown",
            "short": n.get("short_name"),
            "lat": round(lat / 1e7, 6),
            "lng": round(lng / 1e7, 6),
            "updated": n.get("position_updated_at"),
            "hw": n.get("hardware_model"),
            "role": n.get("role"),
        })
    gta.sort(key=lambda n: n["name"].lower())
    out = {
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_nodes_worldwide": len(nodes),
        "gta_count": len(gta),
        "bbox": {"lat_min": 43.3, "lat_max": 44.0, "lng_min": -80.2, "lng_max": -78.9},
        "nodes": gta,
    }
    with open(os.path.join(HERE, "nodes.json"), "w") as f:
        json.dump(out, f)
    print(f"worldwide={len(nodes)} gta={len(gta)}")

if __name__ == "__main__":
    main()
