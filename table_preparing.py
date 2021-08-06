from math import isnan
import logging as log
from add import print_list


def get_data(table: list[list]) -> list:
    for i in range(3):
        table.pop(0)
    data = [value[2:] for value in table]
    return process_data(data)


def has_value(cell: str) -> bool:
    return cell not in {'-', '#VALUE!', 'NaN', '', 'не спускался'}


def process_cell(cell: str) -> float:
    if has_value(cell):
        return float(cell.replace(',', '.'))
    else:
        return float('nan')


def process_data(data: list[list[str]]) -> list:
    prepared_data = []
    for row in data:
        prepared_data.append([process_cell(element) for element in row])
    return prepared_data


def merge_kgf(table: list[list], column_names: list[str]):
    first_kgf_index = len(table[0]) - 2
    second_kgf_index = len(table[0]) - 1
    merged_columns_names = [column_names[first_kgf_index], column_names[second_kgf_index]]
    log.info(f"Target columns {print_list(merged_columns_names, ' and ')} was merged")

    for row in table:
        if isnan(row[first_kgf_index]) and not isnan(row[second_kgf_index]):
            row[first_kgf_index] = 1000 * row[second_kgf_index]
    column_names.pop()
    for row in table:
        row.pop()


def is_significant_rows(row: list, target_variables_count: int) -> bool:
    for element in row[-1 * target_variables_count:]:
        if not isnan(element):
            return True
    return False


def filter_rows(table: list[list], predicate) -> list:
    deleted_rows = []
    i = 0
    while i < len(table):
        if predicate(table[i]):
            deleted_rows.append(table[i])
            del table[i]
        else:
            i += 1
    return deleted_rows


def delete_insignificant_rows(table: list[list], target_variables_count: int, column_names: list[str]) -> list[list]:
    deleted_rows = filter_rows(table, lambda x: not is_significant_rows(x, target_variables_count))
    log.info(f"{len(deleted_rows)} insignificant rows was deleted "
             f"(where values of {print_list(column_names[-1 * target_variables_count:], ' and ')} is a nan)")
    return deleted_rows


def numerate_elements(input_list: list[str]) -> list[str]:
    index = 0
    numerated_list = []
    for element in input_list:
        numerated_list.append(f"({str(index)}) {element}")
        index += 1
    return numerated_list
