import datetime
from typing import Dict, List

import matplotlib.pyplot as plt
import matplotlib.scale
import numpy as np
import pandas as pd
from scipy import stats

from classes.logger_mixin import LoggerMixin
from constants import COLLECTED_DATA_FOLDER, FREQUENCY_COL_NAME
from enums import PositionFieldNames


class Analyzer(LoggerMixin):
    def __init__(self, packets_dicts: List[Dict]):
        super().__init__(packets_dicts)

        # first batch of packets should be a reference batch without audio enabled
        self.packets_df = pd.DataFrame(packets_dicts)

        # add `Frequency` column
        if FREQUENCY_COL_NAME not in self.packets_df.columns.values:
            self.packets_df.insert(2, FREQUENCY_COL_NAME, len(self.packets_df) * [0], True)

        self.z_score_threshold = 3
        self.z_score_outliners = None

    # def _add_frequency_column(self):


    def append_packets(self, packets_dicts: List[Dict]):
        self.logger.info(f"Packets amount: {len(self.packets_df)}")
        new_packets_df = pd.DataFrame(packets_dicts)
        self.packets_df = pd.concat([self.packets_df, new_packets_df], ignore_index=True)
        self.logger.info(f"Packets amount after concat: {len(self.packets_df)}")

    def describe_packets(self):
        # described_packets = self.packets_df.transpose(copy=True).describe(percentiles=[]).reset_index()
        # del(described_packets['count'])

        self.logger.info(f"Described: \r\n{self.packets_df.describe()}")
        self.logger.info(
            f"\r\nRolling standard deviatio for each value:\r\n"
            f"---------------------------------------------\r\n"
            f"{self.packets_df.std()}"
        )

    def save_packets(self):
        saved_file_name = datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")  # TODO: Move saving to analyzer class
        saved_file_path = f"./{COLLECTED_DATA_FOLDER}/{saved_file_name}.csv"

        self.packets_df.to_csv(saved_file_path)
        self.logger.info(f"Saved data to {saved_file_path}")

    def calc_zscore_outliners(self):
        """
        A positive z-score indicates the raw score is higher than the mean average.
        For example, if a z-score is equal to +1, it is 1 standard deviation above the mean.
        A negative z-score reveals the raw score is below the mean average.
        For example, if a z-score is equal to -2, it is two standard deviations below the mean.
        """
        z = np.abs(stats.zscore(self.packets_df))
        self.z_score_outliners = self.packets_df[z > self.z_score_threshold].dropna(how="all")

        return self.z_score_outliners

    def show_plot(self, columns_to_show: List[PositionFieldNames], x_axis: str):
        def fw(*args, **kwargs):
            print('asdasd')
        def bkw(*args, **kwargs):
            print('asdasd')

        plt.figure(figsize=(12, 6))
        for column_name in columns_to_show:
            plt.plot(self.packets_df[x_axis], self.packets_df[column_name], label=column_name)#, scale=matplotlib.scale.FuncTransform(forward=fw, inverse=bkw))

        data_label = columns_to_show[0].name if len(columns_to_show) == 1 else "values"

        plt.ylabel(data_label)
        plt.xlabel(x_axis)

        # plt.stem(self.packets_df, 'r', )# showing the exact location of the smaples

        # plt.sca(.get_matrix())
        # plt.set_xticks(np.arange(0, 24, 1))

        plt.title(f"Sensor {data_label} data by {x_axis}")
        plt.legend()
        plt.grid(which="both")
        plt.show()
        self.logger.debug('Plot drawing finished')

    def update_frequency_col(self, frequency: int):
        # set provided frequency values_list for last packets batch (without frequcny set)
        self.packets_df[FREQUENCY_COL_NAME] = self.packets_df[FREQUENCY_COL_NAME].fillna(frequency)
