import math
from config import ALTO

def hex_a_pixel(q, r, radio):
    x = radio * (3/2 * q)
    y = radio * (math.sqrt(3)/2 * q + math.sqrt(3) * r)
    return (int(x + 450), int(y + ALTO/2))

def pixel_a_hex(x, y, radio):
    x, y = x - 450, y - ALTO/2
    q = (2/3 * x) / radio
    r = (-1/3 * x + math.sqrt(3)/3 * y) / radio
    return hex_round(q, r)

def hex_round(q, r):
    s = -q - r
    rq, rr, rs = round(q), round(r), round(s)
    dq, dr, ds = abs(rq - q), abs(rr - r), abs(rs - s)
    if dq > dr and dq > ds: rq = -rr - rs
    elif dr > ds: rr = -rq - rs
    return rq, rr
