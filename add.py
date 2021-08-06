from typing import Callable
from math import sqrt, exp, pi


def transpose(data: list) -> list[list]:
    transposed_data = []
    for i in range(len(data[0])):
        transposed_data.append([row[i] for row in data])
    return transposed_data


def print_list(input_list: list[str], delimiter: str) -> str:
    output_str = ""
    for element in input_list:
        output_str = output_str + delimiter + '\'' + element.split(' ')[0] + '\''
    return output_str[len(delimiter):]
