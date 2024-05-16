from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from classes.logger_mixin import LoggerMixin
from constants import FREQUENCY_COL_NAME


class Analyzer(LoggerMixin):
    def __init__(self, packets_dicts: List[Dict]):
        super().__init__(packets_dicts)

        self.packets_df = pd.DataFrame(packets_dicts)

        # first batch of packets should be a reference batch without audio enabled
        self.packets_df.insert(2, FREQUENCY_COL_NAME, len(self.packets_df) * [0], True)

        self.z_score_threshold = 3
        self.z_score_outliners = None

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

    def calc_zscore_outliners(self):
        """
        A positive z-score indicates the raw score is higher than the mean average.
        For example, if a z-score is equal to +1, it is 1 standard deviation above the mean.
        A negative z-score reveals the raw score is below the mean average.
        For example, if a z-score is equal to -2, it is two standard deviations below the mean.
        """
        z = np.abs(stats.zscore(self.packets_df))
        self.z_score_outliners = self.packets_df[z > self.z_score_threshold].dropna(how="all")

        # outliners plot
        # plt.figure(figsize=(20, 16))
        # plt.plot(outliners['index'], outliners['ygyro'], label='ygyro', marker='o', color='b')
        # # plt.plot(outliners['index'], outliners['xgyro'], label='xgyro')
        # # plt.plot(outliners['index'],outliners['zgyro'], label='zgyro')
        # plt.legend()
        # plt.grid(True)
        # plt.show()

        return self.z_score_outliners

    def show_plot(self):
        # plt.figure(figsize=(12, 6))
        #
        # plt.plot(self.packets_df['Frequency'], self.packets_df['ygyro'], label='ygyro')
        #
        # plt.xlabel('Time (usec)')
        # plt.ylabel('Values')
        # plt.title('Sensor Data over Time')
        # plt.legend()
        # plt.grid(True)
        # plt.show()

        plt.figure(figsize=(12, 6))
        plt.plot(self.packets_df["time_usec"], self.packets_df["Frequency"], label="Frequency")
        plt.plot(self.packets_df["time_usec"], self.packets_df["xacc"], label="xacc")
        plt.plot(self.packets_df["time_usec"], self.packets_df["yacc"], label="yacc")
        plt.plot(self.packets_df["time_usec"], self.packets_df["zacc"], label="zacc")

        plt.plot(self.packets_df["time_usec"], self.packets_df["xgyro"], label="xgyro")
        plt.plot(self.packets_df["time_usec"], self.packets_df["ygyro"], label="ygyro")
        plt.plot(self.packets_df["time_usec"], self.packets_df["zgyro"], label="zgyro")

        plt.xlabel("Time (usec)")
        plt.ylabel("Values")
        plt.title("Sensor Data over Time")
        plt.legend()
        plt.grid(True)
        plt.show()

    def update_frequency_col(self, frequency: int):
        # set provided frequency value for last packets batch (without frequcny set)
        self.packets_df[FREQUENCY_COL_NAME] = self.packets_df[FREQUENCY_COL_NAME].fillna(frequency)
