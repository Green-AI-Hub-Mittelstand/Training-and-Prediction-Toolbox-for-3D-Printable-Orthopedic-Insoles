from django.conf import settings

def pixel2mm(pixels):
    mm = pixels / settings.TARGET_DPI * 25.4
    return mm

def mm2pixel(mm):
    pixels = mm * settings.TARGET_DPI / 25.4
    return int(pixels)

def map(value, in_min, in_max, out_min, out_max):
    # Map the input value from the input range to the output range
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

