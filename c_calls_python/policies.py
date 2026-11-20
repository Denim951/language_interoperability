def transform(x, mode):
    if mode == "square":
        return x * x

    elif mode == "absolute":
        return abs(x)

    elif mode == "reciprocal":
        if x == 0:
            raise ValueError("Cannot divide by zero")
        return 1 / x

    else:
        raise ValueError(f"Unknown mode: {mode}")