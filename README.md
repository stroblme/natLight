## Description

This small python script outputs an 'white' RGB value which varies depending on sunrise and sunset at your location as well on
your personal preferences regarding sleep and wake up times.

In my case it's used to modify the RGB value of my room light to a more eye-friendly, warmer light.
It's compareable to any blue-light filter for Displays but implemts only the color changes.

You can modify transition time as well as your personal color temperature limits.

## Requirements

Requires Python
	Requires matplotlib and colorsys:
		```
		$ pip install matplotlib
		$ pip install colorsys
		```

## Installation

Dowload Zip, extract and install via pip:

```
$ pip install .
```

Upgrade via pip:

$ pip install . --upgrade


## Usage

You can run the main method of the script (which displays Sunrise, Sunset, Time and RGB Value) via:

python natLight2RGB.py


In your python script, you can get the RGB value as Array:

```python
import natLight

print natLight.convert2RGB()
```

You can acces the values via:

```python
import natLight

rgb = natLight.convert2RGB()

red = rgb['r']
green = rgb['g']
blue = rgb['b']
```

## Contributing

Credits go to Carlos Platoni (2015) for the Sunset and Sunrise calculation (http://thorpesoftware.com/calculating-sunrise-and-sunset/)
as well as to ShawnF (2014) for the Color Temp to RGB Conversion (http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/)

## Licensing

This is intended to be used in custom environment and therefore can be modified, and used without any
restrictations.
There is absolutely no warrenty for any results when using this project.

## Documentation

Refer to this README