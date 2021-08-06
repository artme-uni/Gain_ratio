import statistics

from math import isnan, log, sqrt
import matplotlib.pyplot as plt
import numpy as np

import numpy


def calculate_missing_rate(column: list) -> float:
    valid_values = [element for element in column if not isnan(element)]
    return round((1 - (len(valid_values) / len(column))) * 100, 3)


def calculate_unique_elements_count(column: list) -> int:
    unique_elements = set([element for element in column if not isnan(element)])
    return len(unique_elements)


def calculate_mode(column: list) -> float:
    values = [value for value in column if not isnan(value)]
    mode_elements = statistics.multimode(values)
    mode = mode_elements[0]
    return mode


def calculate_mean(column: list) -> float:
    values = [value for value in column if not isnan(value)]
    mean = numpy.mean(values)
    return mean


def calculate_variance(column: list) -> float:
    values = [value for value in column if not isnan(value)]
    variance = sqrt(np.var(values))
    return variance


def calculate_quantile(column: list, number: int) -> float:
    values = [element for element in column if not isnan(element)]
    return np.percentile(values, number * 25)


def is_categorical_variable(unique_values_percentage: float) -> bool:
    return unique_values_percentage < 24


class Column:
    data: list

    column_name: str
    is_categorical: bool

    missing_rate: float
    unique_elements_count: int
    unique_elements_percentage: float
    mode: float
    mean: float
    variance: float
    first_quantile: float
    third_quantile: float

    lower_bound: float
    upper_bound: float

    def __init__(self, data: list[float], column_name: str):
        self.column_name = column_name
        self.data = data
        self.__calculate_characteristics()

    def __calculate_characteristics(self):
        self.missing_rate = calculate_missing_rate(self.data)
        self.unique_elements_count = calculate_unique_elements_count(self.data)
        self.mode = calculate_mode(self.data)
        self.mean = calculate_mean(self.data)
        self.variance = calculate_variance(self.data)
        self.first_quantile = calculate_quantile(self.data, 1)
        self.third_quantile = calculate_quantile(self.data, 3)
        self.unique_elements_percentage = (self.unique_elements_count / len(self.get_not_nan_elements())) * 100
        self.is_categorical = is_categorical_variable(self.unique_elements_percentage)

    def get_not_nan_elements(self) -> list:
        return [element for element in self.data if not isnan(element)]

    def fill_missing_values(self) -> bool:
        if self.missing_rate != 0 and self.missing_rate < 30:
            filling_value = self.mode if self.is_categorical else self.mean
            for i in range(len(self.data)):
                if isnan(self.data[i]):
                    self.data[i] = filling_value
            self.missing_rate = calculate_missing_rate(self.data)
            return True
        return False

    def figure_histogram(self):
        sorted_data = sorted(self.data)
        bins_count = int(1 + log(len(sorted_data), 2))
        plt.hist(sorted_data, bins=bins_count, density=False)
        plt.title(self.column_name)
        upper_bound = self.get_upper_bound()
        lower_bound = self.get_lower_bound()
        if upper_bound:
            plt.axvline(x=upper_bound)
        if lower_bound:
            plt.axvline(x=lower_bound)
        plt.show()

    def get_lower_bound(self) -> float:
        bound = self.first_quantile - 1.5 * (self.third_quantile - self.first_quantile)
        return bound

    def get_upper_bound(self) -> float:
        bound = self.third_quantile + 1.5 * (self.third_quantile - self.first_quantile)
        return bound

    def get_name(self) -> str:
        return self.column_name

    def normalize(self):
        min_value = min(self.data)
        max_value = max(self.data)
        prepared_data = []
        for value in self.data:
            prepared_value = (value - min_value) / (max_value - min_value)
            prepared_data.append(prepared_value)
        self.data = prepared_data
