import math

def curve(R0, S, days):
    c = []
    r = R0; s = S; last = 0
    for d in range(31):
        R = r * math.exp(-(d - last) / s)
        if d in days:
            R = min(1, R + (1 - R) * 0.6)
            r = R; s = s * 1.6; last = d
        c.append(R)
    return c

def pct(v):
    return str(round(v * 100)) + '%'

strategies = [('无复习', []), ('突击复习', [1]), ('间隔复习', [1, 3, 7, 14])]

for S in (2, 8):
    R0 = 0.9
    print('=== S =', S, 'R0 = 0.9 ===')
    for name, days in strategies:
        c = curve(R0, S, days)
        print(name, '| 1d:', pct(c[1]), '| 7d:', pct(c[7]), '| 14d:', pct(c[14]), '| 30d:', pct(c[30]), '| avg:', pct(sum(c) / 31))
    cram = curve(R0, S, [1])[30]
    spaced = curve(R0, S, [1, 3, 7, 14])[30]
    print('X (间隔-突击, 第30天百分点) =', round((spaced - cram) * 100))
