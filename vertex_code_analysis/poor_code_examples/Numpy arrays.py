import numpy as np


def calculate_sum(array) -> int:
    sum = 0
    for i in array:
        sum += i
    return sum


def sum_product_with_for_loop(array1, array2) -> int:
    sum = 0
    for i, j in zip(array1, array2):
        sum += i * j
    return sum


if __name__ == "__main__":
    array1 = np.random.randint(0, 100, 1000000)
    array2 = np.random.randint(0, 100, 1000000)
    print(sum_product_with_for_loop(array1, array2))
