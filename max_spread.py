from itertools import combinations
import math

coords = [
    (48.26681841361227, 11.671545974856464),
    (48.266778405714795, 11.671365667832644),
    (48.26664565201248, 11.671715354181872),
    (48.266722030897014, 11.671912052753312)
]

def find_max_spread(points):
    max_spread = 0
    for p1, p2 in combinations(points, 2):
        spread = math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        if spread > max_spread:
            max_spread = spread
    return max_spread

if __name__ == "__main__":
    print(f"Max spread: {find_max_spread(coords):.9f} degrees")