def find_max(list_of_numbers):
    max_number = list_of_numbers[0]
    for num in list_of_numbers:
        if num > max_number:
            max_number = num
    return max_number

print(find_max([1, 2, 3, 4, 5]))
