import math


IMPACT_THRESHOLD = 1000 #change when needed

def magnitude(x, y, z):
    '''
    the magnitude of the acceleration
    '''

    return (math.sqrt(x**2 + y**2 + z**2))
