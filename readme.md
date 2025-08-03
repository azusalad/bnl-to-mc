# Block n' Load to Minecraft Schematic

Convert Block n' Load (bnl) mapdata files to Minecraft schematic files.  Colored blocks are currently not supported.

## Requirements

Python, nbtlib

```
pip install -r requirements.txt
```

## Usage

Run `main.py` with the bnl mapdata file you wish to convert.  These files can be found in `SteamLibrary/steamapps/workshop/content/299360/`.

You can optionally add a name to the destination file.  By default, the input filename will be used with the `.schematic` file extension.

If you do not want to add the lava or water plane to the converted file, use the `--no-plane` argument.

```
usage: main.py [-h] [--no-plane] input_file [output_file]

Convert bnl maps to Minecraft schematics.

positional arguments:
  input_file   Path to bnl mapdata file to convert.
  output_file  Path to Minecraft schematic to save converted data. Defaults to the input file with the .schematic extension.

options:
  -h, --help   show this help message and exit
  --no-plane   Disable adding lava/water plane to converted map.
```

### Example Usage

```
python3 main.py mapdata
```

Converts the bnl file `mapdata` in the current directory and outputs `mapdata.schematic` in the current directory.