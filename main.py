import csv
import matplotlib.pyplot as plt
from tabulate import tabulate
import logging as log

from add import print_list
from table import Table
import table_preparing as prep
from math import fabs

from gain_ratio import calculate_gain_ratio


INPUT_DATA = 'resources/ID_data_mass_18122012.csv'


log.basicConfig(filename='out.md', filemode='w', format='[%(levelname)s] %(message)s', level=log.INFO)


def plot_characteristic(column_names, values):
    fig, axes = plt.subplots()
    axes.barh(column_names, values)
    axes.set_facecolor('floralwhite')
    fig.set_figwidth(13)
    fig.set_figheight(10)
    fig.subplots_adjust(left=0.2)
    plt.show()


def figure_characteristic(column_names, values):
    plot_characteristic(column_names, values)
    print(tabulate([values], column_names, tablefmt="grid"))


def get_table(input_file) -> Table:
    reader = csv.reader(input_file, delimiter=';')
    input_list = list(reader)
    column_names = prep.numerate_elements(input_list[1][2:])
    data = prep.get_data(input_list)

    prep.merge_kgf(data, column_names)
    target_variables_count = 2
    prep.delete_insignificant_rows(data, target_variables_count, column_names)

    table = Table(data, column_names, target_variables_count)
    return table


def process_missing_values(table: Table, is_visually: bool):
    if is_visually:
        figure_characteristic(table.column_names, table.get_missing_rate())

    table.fill_missing_values()
    table.delete_half_empty_columns()
    table.delete_static_columns()

    if is_visually:
        figure_characteristic(table.column_names, table.get_missing_rate())


def get_correlation_map(table: Table, is_visually: bool):
    if is_visually:
        table.figure_plot_correlation()

    correlation_map = table.get_correlation_table()
    highly_correlated_columns: list[tuple[int, int, int]] = []
    for row_index in range(len(correlation_map) - 2):
        for column_index in range(row_index):
            correlation_rate = correlation_map[row_index][column_index]
            if correlation_rate > 0.85 and not is_components(row_index, column_index, correlation_map):
                highly_correlated_columns.append((row_index, column_index, correlation_rate))

    log.info("")
    names = table.get_column_names()

    deleted = []
    for column_tuple in highly_correlated_columns:
        log.info(f"Column {print_list([names[column_tuple[0]]], '')} correlated ({round(column_tuple[2], 3)}%) with {print_list([names[column_tuple[1]]], '')} ")
        deleted.append(delete_one(table, column_tuple[0], column_tuple[1]))

    log.info(f"Columns {print_list([str(val) for val in sorted(list(set(deleted)))], ', ')} can be deleted")


def delete_one(table: Table, first_column: int, second_column: int) -> int:
    gain_ratio = get_gain_ratio(table, is_visually=False)
    first_rate = gain_ratio[first_column]
    second_rate = gain_ratio[second_column]
    deleted_column_index = first_column if first_rate < second_rate else second_column
    return deleted_column_index


def is_components(first_column_index, second_column_index, correlation_map) -> bool:
    threshold = 0.3

    for i in range(len(correlation_map) - 2):
        if i == first_column_index or i == second_column_index:
            continue

        diff = fabs(correlation_map[first_column_index][i] - correlation_map[second_column_index][i])
        if diff > threshold:
            return True

    return False


def remove_outliers(table: Table, is_visually: bool):
    if is_visually:
        table.figure_histograms()
        figure_characteristic(table.column_names, table.get_upper_bound())
        figure_characteristic(table.column_names, table.get_lower_bound())

    dr = []
    dr.extend(table.filter_column("(3) Рзаб", lambda x: x > 198.269))
    dr.extend(table.filter_column("(4) Pлин", lambda x: 84.07 < x < 115.75))
    dr.extend(table.filter_column("(6) Рзаб", lambda x: x > 193.338))
    dr.extend(table.filter_column("(7) Рлин", lambda x: x > 60))
    dr.extend(table.filter_column("(8) Туст", lambda x: x > 29.75))
    dr.extend(table.filter_column("(9) Тна шлейфе", lambda x: x < 60))
    dr.extend(table.filter_column("(10) Тзаб", lambda x: x > 102.961))
    dr.extend(table.filter_column("(12) Дебит газа", lambda x: x < 792.25))
    dr.extend(table.filter_column("(13) Дебит ст. конд.", lambda x: x < 200))
    dr.extend(table.filter_column("(14) Дебит воды", lambda x: x < 6.95))
    dr.extend(table.filter_column("(15) Дебит смеси", lambda x: x < 813.265))
    dr.extend(table.filter_column("(17) Дебит кон нестабильный", lambda x: x < 287.8))
    dr.extend(table.filter_column("(18) Дебит воды", lambda x: x < 7.2))
    dr.extend(table.filter_column("(26) Ro_c", lambda x: x > 700))
    dr.extend(table.filter_column("(28) Удельная плотность газа ", lambda x: x > 0.63))
    dr.extend(table.filter_column("(30) КГФ", lambda x: x < 314))

    log.info(f"{len(dr)} outliers were deleted")
    return dr


def find_categorical_columns(table, is_visually: bool):
    if is_visually:
        figure_characteristic(table.get_column_names(), table.get_unique_elements_percentage())

    table.find_categorical_columns()


def get_gain_ratio(table: Table, is_visually: bool):
    # test_age = [0, 0, 50, 100, 100, 100, 50, 0, 0, 100, 0, 50, 50, 100]
    # test_income = [100, 100, 100, 50, 0, 0, 0, 50, 0, 50, 50, 50, 100, 50]
    # output = [(1, 0), (1, 0), (1, 100), (1, 100), (1, 100), (1, 0), (1, 100), (1, 0), (1, 100), (1, 100), (1, 100), (1, 100), (1, 100), (1, 0)]
    # print(calculate_gain_ratio(test_income, output))

    ratio = []
    for column in table.columns[:-2]:
        ratio.append(calculate_gain_ratio(column.data, table.get_target()))
    if is_visually:
        figure_characteristic(table.column_names[:-2], ratio)
    return ratio


def main() -> None:
    with open(INPUT_DATA, 'r') as input_file:
        table = get_table(input_file)

        find_categorical_columns(table, is_visually=False)
        process_missing_values(table, is_visually=False)
        remove_outliers(table, is_visually=False)
        get_gain_ratio(table, is_visually=False)
        get_correlation_map(table, is_visually=False)

        table.normalize()
        table.print_full_table()
        table.save_in_file('output')



if __name__ == '__main__':
    main()