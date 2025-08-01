import base64

class Converter():
  def __init__(self, mapdata_path):
    self.mapdata_path = mapdata_path

    # Mapdata files are base64 encoded
    with open(self.mapdata_path, 'r') as f:
      self.mapdata_b64 = f.read()

    self.mapdata_str = self.base64_decode(self.mapdata_str)

  def __str__(self):
    return f"mapdata_path = {self.mapdata_path}; mapdata_b64 = {self.mapdata_b64}; mapdata_str = {self.mapdata_str}"

  def base64_decode(self, text):
    # Avoid incorrect padding
    # https://stackoverflow.com/questions/2941995/python-ignore-incorrect-padding-error-when-base64-decoding
    text += "=="
    return base64.b64decode(text)

  def convert(self):
    pass


if __name__ == "__main__":
  converter = Converter("mapdata")
  converter.convert()