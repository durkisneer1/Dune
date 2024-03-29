from math import cos, pi, sin, sqrt


def ease_in_sine(x: float | int) -> float | int:
    return 1 - cos((x * pi) / 2)


def ease_out_sine(x: float | int) -> float | int:
    return sin((x * pi) / 2)


def ease_in_out_sine(x: float | int) -> float | int:
    return -1 * (cos(pi * x) - 1) / 2


def ease_in_quad(x: float | int) -> float | int:
    return x * x


def ease_out_quad(x: float | int) -> float | int:
    return 1 - (1 - x) * (1 - x)


def ease_in_out_quad(x: float | int) -> float | int:
    if x < 0.5:
        return 2 * x * x
    else:
        return 1 - pow(-2 * x + 2, 2) / 2


def ease_in_cubic(x: float | int) -> float | int:
    return x * x * x


def ease_out_cubic(x: float | int) -> float | int:
    return 1 - pow(1 - x, 3)


def ease_in_out_cubic(x: float | int) -> float | int:
    if x < 0.5:
        return 4 * x * x * x
    else:
        return 1 - pow(-2 * x + 2, 3) / 2


def ease_in_quart(x: float | int) -> float | int:
    return x * x * x * x


def ease_out_quart(x: float | int) -> float | int:
    return 1 - pow(1 - x, 4)


def ease_in_out_quart(x: float | int) -> float | int:
    if x < 0.5:
        return 8 * x * x * x * x
    else:
        return 1 - pow(-2 * x + 2, 4) / 2


def ease_in_quint(x: float | int) -> float | int:
    return x * x * x * x * x


def ease_out_quint(x: float | int) -> float | int:
    return 1 - pow(1 - x, 5)


def ease_in_out_quint(x: float | int) -> float | int:
    if x < 0.5:
        return 16 * x * x * x * x * x
    else:
        return 1 - pow(-2 * x + 2, 5) / 2


def ease_in_expo(x: float | int) -> float | int:
    return 0 if x == 0 else pow(2, 10 * x - 10)


def ease_out_expo(x: float | int) -> float | int:
    return 1 if x == 1 else 1 - pow(2, -10 * x)


def ease_in_out_expo(x: float | int) -> float | int:
    if x == 0:
        return 0
    if x == 1:
        return 1
    if x < 0.5:
        return pow(2, 20 * x - 10) / 2
    else:
        return (2 - pow(2, -20 * x + 10)) / 2


def ease_in_circ(x: float | int) -> float | int:
    return 1 - sqrt(1 - pow(x, 2))


def ease_out_circ(x: float | int) -> float | int:
    return sqrt(1 - pow(x - 1, 2))


def ease_in_out_circ(x: float | int) -> float | int:
    if x < 0.5:
        return (1 - sqrt(1 - pow(2 * x, 2))) / 2
    else:
        return (sqrt(1 - pow(-2 * x + 2, 2)) + 1) / 2


def ease_in_back(x: float | int) -> float | int:
    c1 = 1.70158
    c2 = c1 + 1
    x2 = x * x
    return c2 * x2 * x - c1 * x2


def ease_out_back(x: float | int) -> float | int:
    c1 = 1.70158
    c2 = c1 + 1
    px1 = pow(x - 1, 2)
    return 1 + c2 * px1 * (x - 1) + c1 * px1


def ease_in_out_back(x: float | int) -> float | int:
    c1 = 1.70158
    c2 = c1 * 1.525

    return (
        (pow(2 * x, 2) * ((c2 + 1) * 2 * x - c2)) / 2
        if x < 0.5
        else (pow(2 * x - 2, 2) * ((c2 + 1) * (x * 2 - 2) + c2) + 2) / 2
    )


def ease_in_elastic(x: float | int) -> float | int:
    c1 = (2 * pi) / 3
    if x == 0:
        return 0
    if x == 1:
        return 1
    else:
        return pow(2, 10 * x - 10) * sin((x * 10 - 0.75) * c1)


def ease_out_elastic(x: float | int) -> float | int:
    c1 = (2 * pi) / 3
    if x == 0:
        return 0
    if x == 1:
        return 1
    else:
        return pow(2, -10 * x) * sin((x * 10 - 0.75) * c1) + 1
