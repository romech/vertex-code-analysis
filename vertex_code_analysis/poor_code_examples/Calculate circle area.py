from math import *

def calculate_area(diameter: str) -> int:
    radius = diameter / 2
    area = 3.141592653589793 * radius ** 2
    return area
