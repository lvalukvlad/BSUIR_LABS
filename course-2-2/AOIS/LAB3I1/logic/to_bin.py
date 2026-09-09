import math

def to_bin(num, length):

    direct = []
    while num != 0:
        direct.insert(0, num % 2)
        num = math.trunc(num / 2)
    while len(direct) < length:
        direct.insert(0, 0)

    return direct