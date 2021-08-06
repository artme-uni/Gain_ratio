import csv

from add import transpose
from tabulate import tabulate
from column import Column
import pandas as pd
import matplotlib.pyplot as plt
import logging
from math import isnan

from add import print_list


class Table:
    columns = []
    target_variables_count: int
    column_names: list[str]

    def __init__(self, data: list[list[float]], column_names: list[str], target_variables_count: int):
        self.column_names = column_names
        self.target_variables_count = target_variables_count
        transposed_data = transpose(data)
        self.init_columns(transposed_data, column_names);

    def init_columns(self, transposed_data, column_names):
        self.columns.clear()
        for i in range(len(transposed_data)):
            current_column = Column(transposed_data[i], column_names[i])
            self.columns.append(current_column)

    def filter_column(self, column_name: str, predicate) -> list[list]:
        column_index = self.column_names.index(column_name)
        data = self.get_data()
        rows = transpose(data)

        deleted_rows = []
        index = 0
        while index < len(rows):
            row = rows[index]
            if isnan(row[-2]) and not predicate(row[column_index]):
                deleted_rows.append(row)
                rows.pop(index)
                continue
            index += 1
        self.init_columns(transpose(rows), self.column_names)
        return deleted_rows

    def get_column_index(self, column_name : str):
        for i in range(len(self.columns)):
            column = self.columns[i]
            if column_name == column.get_name():
                return i

    def __get_dictionary(self) -> dict:
        names = self.get_column_names()
        data = self.get_data()
        dictionary = {names[i]: data[i] for i in range(len(data))}
        return dictionary

    def __filter_columns(self, predicate):
        deleted_columns = []
        index = 0
        while index < self.__get_off_target_variables_count():
            column = self.columns[index]
            if not predicate(column):
                deleted_column = self.delete_column(index)
                deleted_columns.append(deleted_column)
                continue
            index += 1
        return deleted_columns

    def __get_off_target_variables_count(self) -> int:
        return len(self.columns) - self.target_variables_count

    def __get_off_target_variables(self) -> list:
        return self.columns[:-2]

    def figure_plot_correlation(self):
        df = pd.DataFrame(self.__get_dictionary())
        f = plt.figure(figsize=(20, 15))
        plt.matshow(df.corr(), fignum=f.number)
        plt.xticks(range(df.shape[1]), df.columns, fontsize=14, rotation=90)
        plt.yticks(range(df.shape[1]), df.columns, fontsize=14)
        cb = plt.colorbar()
        cb.ax.tick_params(labelsize=14)
        plt.show()

    def get_correlation_table(self) -> list[list]:
        df = pd.DataFrame(self.__get_dictionary())
        d = df.corr().to_dict()
        matrix = []
        names = self.column_names
        for name1 in names:
            row = []
            for name2 in names:
                row.append(d[name1][name2])
            matrix.append(row)
        return matrix

    def print_full_table(self):
        output = tabulate(transpose(self.get_data()), self.get_column_names(), tablefmt="grid")
        print(output)

    def get_column_names(self) -> list[str]:
        return [column.column_name for column in self.columns]

    def get_missing_rate(self) -> list[str]:
        return [column.missing_rate for column in self.columns]

    def get_unique_elements_count(self) -> list[str]:
        return [column.unique_elements_count for column in self.columns]

    def get_unique_elements_percentage(self) -> list:
        return [column.unique_elements_percentage for column in self.columns]

    def get_mode(self) -> list[str]:
        return [column.mode for column in self.columns]

    def get_mean(self) -> list[str]:
        return [column.mean for column in self.columns]

    def get_data(self) -> list[list]:
        return [column.data for column in self.columns]

    def get_upper_bound(self) -> list[list]:
        return [column.get_upper_bound() for column in self.columns]

    def get_lower_bound(self) -> list[list]:
        return [column.get_lower_bound() for column in self.columns]

    def delete_column(self, index: int) -> Column:
        deleted_column = self.columns.pop(index)
        self.column_names.pop(index)
        return deleted_column

    def fill_missing_values(self):
        filled_columns = []
        for column in self.__get_off_target_variables():
            was_filled = column.fill_missing_values()
            if was_filled:
                filled_columns.append(column)
        filled_columns_names = [column.column_name for column in filled_columns]
        logging.info(f"Missing values of columns {print_list(filled_columns_names, ', ')} were filled")

    def delete_half_empty_columns(self):
        threshold_missing_rate = 60
        deleted_columns = self.__filter_columns(lambda column: column.missing_rate < threshold_missing_rate)
        deleted_columns_names = [column.column_name for column in deleted_columns]
        logging.warning(f"Columns {print_list(deleted_columns_names, ', ')} "
                    f"(with missing rate > {threshold_missing_rate})  were deleted")

    def delete_static_columns(self):
        deleted_columns = self.__filter_columns(lambda column: column.unique_elements_count > 1)
        deleted_columns_names = [column.column_name for column in deleted_columns]
        logging.warning(f"Static columns {print_list(deleted_columns_names, ', ')} "
                    f"(with single unique element)  were deleted")

    def figure_histograms(self):
        for column in self.columns:
            column.figure_histogram()

    def print_bounds(self):
        for column in self.columns:
            print(str(column.column_name) + ": " + str(column.get_lower_bound()) + " " + str(column.get_upper_bound()))

    def find_categorical_columns(self) -> list[str]:
        categorical_columns = [column.column_name for column in self.columns if column.is_categorical]
        logging.warning(f"Find {len(categorical_columns)} categorical columns (< 24% unique values): {print_list(categorical_columns, ', ')}")
        return categorical_columns

    def get_target(self) -> list[tuple[float, float]]:
        values = []
        table_data = transpose(self.get_data()[-2:])
        for row in table_data:
            values.append((row[0], row[1]))
        return values

    def save_in_file(self, filename):
        df = pd.DataFrame(self.__get_dictionary())
        df.to_csv('out.csv', index=False)

    def normalize(self):
        for column in self.columns:
            column.normalize()



    # def delete_row(self, column_index: str):
    #     for column in self.columns:
    #         name = column.get_name()
    #         if name.find(column_index):
    #             column.


    # def filter_rows(self, predicate) -> list:
    #     deleted_rows = []
    #     i = 0
    #     while i < len(self.):
    #         if predicate(table[i]):
    #             deleted_rows.append(table[i])
    #             table[i]
    #         else:
    #             i += 1
    #     return deleted_rows
