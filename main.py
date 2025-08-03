from mappings import block_mapping, plane_mapping

from nbtlib import File, Compound, Int, ByteArray, String
from pathlib import Path
import argparse
import base64
import json
import zlib


class Converter():
  def __init__(self, mapdata_path, plane):
    """
    Initialize Converter object.

    Args:
        mapdata_path (str): Path to bnl mapdata file.
        plane (bool): Whether to add the water/lava plane or not.
    """    
    self.mapdata_path = mapdata_path
    self.plane = plane
    self.mapdata = self.get_mapdata()
    self.length = self.mapdata["size"]["x"]
    self.height = self.mapdata["size"]["y"]
    self.width = self.mapdata["size"]["z"]


  def __str__(self):
    return f"mapdata_path = {self.mapdata_path}; mapdata = {self.mapdata}"


  def get_mapdata(self):
    """
    Bnl mapdata files are base64 encoded json.
    Get the json of the file and decode/inflate blocks_data/colors_data.

    Returns:
        dictionary: JSON of the bnl mapdata file.
    """    
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


  def translate_block_array(self):
    """
    Convert bnl block array to Minecraft schematic block array.

    Returns:
        bytearray: Block array for Minecraft schematic.
    """
    schema = self.mapdata["schema"]
    plane = self.mapdata["properties"]["plane"]
    plane_position = int(self.mapdata["properties"]["plane_position"]) + 1
    src_array = self.mapdata["blocks_data"]
    # Initialize destination array
    dest_placeholder_id = 0  # Air
    dest_array = bytearray([dest_placeholder_id] * (self.height * self.length * self.width))
    bytes_per_block = 4 if schema == 4 else 6
    if schema not in [4,5,6]:
      print("Warning: Schema is {schema}.  Conversion might fail.")

    # Iterate through all coordinates
    for x in range(self.length):
      for y in range(self.height):
        for z in range(self.width):
          # Calculate source index and destination index
          src_index = (self.width * (x * self.height + y) + z) * bytes_per_block
          dest_index = self.width * (y * self.length + x) + z
          # Find corresponding Minecraft schematic id and replace in destination array
          bnl_block_id = int(src_array[src_index])
          dest_array[dest_index] = block_mapping[bnl_block_id] if bnl_block_id in block_mapping else dest_placeholder_id

    # Add plane
    if self.plane:
      for x in range(self.length):
        for y in range(plane_position):
          for z in range(self.width):
            dest_index = self.width * (y * self.length + x) + z
            if dest_array[dest_index] == dest_placeholder_id:
              dest_array[dest_index] = plane_mapping[plane]
  
    return dest_array
      


  def write_schematic(self, dest_path, block_array):
    """
    Write Minecraft schematic to file.

    Args:
        dest_path (_type_): Destination filepath.
        block_array (bytearray): Block array for schematic.
    """    
    # Create NBT schematic file
    root_tag = Compound({
      "Schematic": Compound({
        "Width": Int(self.width),
        "Length": Int(self.length),
        "Height": Int(self.height),
        "Blocks": ByteArray(block_array),
        "Data": ByteArray(bytearray([0] * len(block_array))),
        "Materials": String("Alpha")
      })
    })

    # Save the schematic file
    nbt_file = File(root_tag, gzipped=True)
    nbt_file.save(dest_path)


  def convert(self, dest_path):
    """
    Convert bnl map to Minecraft schematic and write to file.

    Args:
        dest_path (_type_): Destination filepath.
    """    
    # Create destination block array
    dest_block_array = self.translate_block_array()
    # Write to schematic file
    self.write_schematic(dest_path, dest_block_array)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Convert bnl maps to Minecraft schematics."
  )
  parser.add_argument("input_file", type=str, help="Path to bnl mapdata file to convert.")
  parser.add_argument("output_file", type=str, nargs="?", help="Path to Minecraft schematic to save converted data.  Defaults to the input file with the .schematic extension.")
  parser.add_argument("--no-plane", action="store_true", help="Disable adding lava/water plane to converted map.")
  args = parser.parse_args()
  input_file = args.input_file
  output_file = args.output_file if args.output_file else Path(input_file).stem + '.schematic'
  plane = not args.no_plane

  converter = Converter(input_file, plane)
  converter.convert(output_file)