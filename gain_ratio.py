from math import log, isnan


def get_classes(data: list[float]) -> dict[int, tuple[float, float]]:
    dictionary = {}

    unique_values = set([value for value in data if not isnan(value)])
    size = len(unique_values)
    class_count = 1 + int(log(size, 2))
    max_value = max(unique_values)
    min_value = min(unique_values)
    step = (max_value - min_value) / class_count

    previous_value = min_value
    for i in range(class_count):
        dictionary[i] = (previous_value, previous_value + step)
        if i == 0:
            dictionary[i] = (previous_value - 1, previous_value + step)
        if i == class_count - 1:
            dictionary[i] = (previous_value, previous_value + step + 1)
        previous_value += step

    return dictionary


def get_target_classes(data: list[tuple[float, float]]) -> dict[int, tuple[float, tuple[float, float]]]:
    dictionary = {}
    second_column_classes = get_classes([tuple_value[1] for tuple_value in data])
    first_column_unique_values = set([tuple_value[0] for tuple_value in data if not isnan(tuple_value[0])])

    index = 0
    for val in first_column_unique_values:
        for i in range(len(second_column_classes.values())):
            dictionary[index] = (val, second_column_classes[i])
            index += 1
    return dictionary


def calculate_freq(data: list[float], bounds: tuple[float, float]) -> int:
    freq = 0
    for value in data:
        if is_belong_to_class(value, bounds):
            freq += 1
    return freq


def part_of_i(freq: int, data_capacity: int) -> float:
    prop = freq / data_capacity
    return -1 * prop * log(prop, 2)


def calculate_target_info(target_columns: list[tuple[float, float]]) -> float:
    target_classes = get_target_classes(target_columns)
    result = 0

    for i in range(len(target_classes.values())):
        target_class_bounds = target_classes[i]
        total_count = 0
        current_freq = 0
        for row in target_columns:
            total_count += 1
            if is_belong_to_target_class(row, target_class_bounds):
                current_freq += 1
        if current_freq != 0:
            result += part_of_i(current_freq, total_count)
    return result


def calculate_column_info(column: list[float]) -> float:
    column_classes = get_classes(column)
    result = 0

    for i in range(len(column_classes.values())):
        target_class_bounds = column_classes[i]
        total_count = 0
        current_freq = 0
        for row in column:
            total_count += 1
            if is_belong_to_class(row, target_class_bounds):
                current_freq += 1
        if current_freq != 0:
            result += part_of_i(current_freq, total_count)
    return result


def calculate_info(input_column: list[float], input_class_bounds : tuple[float, float], target_columns: list[tuple[float, float]]) -> float:
    target_classes = get_target_classes(target_columns)
    result = 0
    for i in range(len(target_classes.values())):
        target_class_bounds = target_classes[i]

        current_class_freq = 0
        capacity = 0
        for j in range(len(input_column)):
            if is_belong_to_class(input_column[j], input_class_bounds):
                capacity += 1
                if is_belong_to_target_class(target_columns[j], target_class_bounds):
                    current_class_freq += 1
        if current_class_freq != 0:
            result += part_of_i(current_class_freq, capacity)
    return result


def is_belong_to_target_class(value: tuple[float, float], class_bounds: tuple[float, tuple[float, float]]):
    is_belong_to_first_column = value[0] == class_bounds[0]
    is_belong_to_second_column = class_bounds[1][0] < value[1] < class_bounds[1][1]
    return is_belong_to_first_column and is_belong_to_second_column


def is_belong_to_class(value: float, class_bounds: tuple[float, float]):
    return class_bounds[0] <= value < class_bounds[1]


def calculate_info_x(input_column: list[float], target_columns: list[tuple[float, float]]):
    input_column_classes = get_classes(input_column)

    result_sum = 0
    for i in range(len(input_column_classes.values())):
        class_range = input_column_classes[i]
        class_freq = calculate_freq(input_column, class_range)
        result_sum += (class_freq / len(input_column)) * calculate_info(input_column, class_range, target_columns)

    return result_sum


def calculate_gain_ratio(input_column: list[float], target_columns: list[tuple[float, float]]) -> float:
    info = calculate_target_info(target_columns)
    info_x = calculate_info_x(input_column, target_columns)
    split = calculate_column_info(input_column)
    return (info - info_x) / split



