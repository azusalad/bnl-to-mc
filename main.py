from block_mapping import block_mapping

from nbtlib import File, Compound, Int, ByteArray, String
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


  def translate_block_array(self, src_array, src_height, src_length, src_width, dest_height, dest_length, dest_width):
    # Initialize destination array
    dest_placeholder_id = 0  # Air
    dest_array = bytearray([dest_placeholder_id] * (src_height * src_length * src_width))

    # Iterate through all coordinates
    for x in range(src_length):
      for y in range(src_height):
        for z in range(src_width):
          # Calculate source index and destination index
          src_index = (src_width * (x * src_height + y) + z) * 4
          dest_index = src_width * (y * src_length + x) + z
          # Find corresponding Minecraft schematic id and replace in destination array
          bnl_block_id = int(src_array[src_index])
          dest_array[dest_index] = block_mapping[bnl_block_id]
  
    return dest_array


  def write_schematic(self, dest_path, block_array):
    src_length = self.mapdata["size"]["x"]
    src_height = self.mapdata["size"]["y"]
    src_width = self.mapdata["size"]["z"]
    # Create NBT schematic file
    root_tag = Compound({
      "Schematic": Compound({
        "Width": Int(src_width),
        "Length": Int(src_length),
        "Height": Int(src_height),
        "Blocks": ByteArray(block_array),
        "Data": ByteArray(bytearray([0] * len(block_array))),
        "Materials": String("Alpha")
      })
    })

    # Save the schematic file
    nbt_file = File(root_tag, gzipped=True)
    nbt_file.save(dest_path)



  def convert(self, dest_path):
    # Create destination block array
    src_length = self.mapdata["size"]["x"]
    src_height = self.mapdata["size"]["y"]
    src_width = self.mapdata["size"]["z"]
    dest_block_array = self.translate_block_array(self.mapdata["blocks_data"], src_height, src_length, src_width, src_height, src_length, src_width)
    # Write to schematic file
    self.write_schematic(dest_path, dest_block_array)


if __name__ == "__main__":
  converter = Converter("mapdata")
  converter.convert("mapdata.schematic")