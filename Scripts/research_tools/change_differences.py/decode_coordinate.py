import pandas as pd
from shapely import wkb

def decode_coordinates(wkb_string):
    try:
        point = wkb.loads(bytes.fromhex(wkb_string))
        return point.y, point.x
    except Exception as e:
        print(f"Failed to decode: {wkb_string}, Error: {e}")
        return None, None

print(decode_coordinates("0101000020E610000053F8E2A6E8F75440BBC45CF5496F3B40"))