
from typing import List, Dict

import pandas as pd


class Analyzator:
    def __init__(self, packets: List[Dict]):
        self.received_packets = packets
        self.packets_df = pd.DataFrame(self.received_packets)

        self.mean = self.packets_df.mean()
        self.min = self.packets_df.min()
        self.max = self.packets_df.max()

    def check_anomaly(self, input_df):
        # Returns rows with alarms in any of columns

        concatenated_df = self.packets_df.copy()
        concatenated_df = pd.concat([concatenated_df, input_df], ignore_index=True)

        for column_name in self.packets_df.columns.values:
            concatenated_df[column_name + '_alarm'] = (
                    concatenated_df[column_name].clip(
                        lower=self.min[column_name],
                        upper=self.max[column_name],
                    ) != concatenated_df[column_name]
            )

        alarm_cols = [col for col in concatenated_df.columns if col.endswith('_alarm')]
        return concatenated_df[concatenated_df[alarm_cols].any(axis=1)]



    def describe_packets(self):
        described_packets = self.packets_df.describe(percentiles=[0.03, 0.95]).transpose()
        del(described_packets['count'])
        del(described_packets['50%'])

        described_packets.columns = ['min', 'max', 'mean', 'std', '3%', '95%']

        print(f'DESCRIBE:\r\n{described_packets}\r\n')



