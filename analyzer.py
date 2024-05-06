
from typing import List, Dict

import pandas as pd


class Analyzer:
    def __init__(self, packets_dicts: List[Dict]):
        self.packets_df = pd.DataFrame(packets_dicts)

    def append_packets(self, packets_dicts: List[Dict]):
        print(f'\r\nPackets amount: {len(self.packets_df)}')
        new_packets_df = pd.DataFrame(packets_dicts)
        self.packets_df = pd.concat([self.packets_df, new_packets_df], ignore_index=True)
        print(f'Packets amount after concat: {len(self.packets_df)}\r\n')


    def describe_packets(self):
        # described_packets = self.packets_df.transpose(copy=True).describe(percentiles=[]).reset_index()
        # del(described_packets['count'])

        print(f'Described: \r\n{self.packets_df.describe()}\r\n\r\n')
        print(f'Rolling standard deviatio for each value:\r\n'
              f'{self.packets_df.rolling(window=50).std()}')
