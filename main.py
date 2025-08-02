import base64
import zlib
import json

class Converter():
  def __init__(self, mapdata_path):
    # mapdata_path: Path to bnl map file
    # mapdata: json of the map content
    self.mapdata_path = mapdata_path
    self.mapdata = self.get_mapdata()

  def __str__(self):
    return f"mapdata_path = {self.mapdata_path}; mapdata = {self.mapdata}"

  def get_mapdata(self):
    # Mapdata files are base64 encoded json
    # Get json
    with open(self.mapdata_path, 'rb') as f:
      base64_encoded_data = f.read()
    # Remove alg and "block binary"
    base64_encoded_data = base64_encoded_data.split(b".")[1]
    # Pad data
    #base64_encoded_data += b"=" * (len(base64_encoded_data) + (4 - len(base64_encoded_data) % 4) % 4)
    base64_encoded_data += b"=="
    # Decode base64 string and convert to dictionary
    json_string = base64.b64decode(base64_encoded_data)
    mapdata = json.loads(json_string)

    # Decode and inflate block_data and colors_data
    mapdata["blocks_data"] = zlib.decompress(base64.b64decode(mapdata["blocks_data"]))
    mapdata["colors_data"] = zlib.decompress(base64.b64decode(mapdata["colors_data"]))  # this is unused

    return mapdata

  def convert(self):
    pass


if __name__ == "__main__":
  converter = Converter("mapdata")
  converter.convert()