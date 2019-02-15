import numpy as np
import pandas as pd


def get_latency(filename):
    data = pd.read_csv(filename, sep='|')
    filtered = data[(data['client_sent'] != 0) & (data['label'] == 'get_nym')]
    filtered['latency'] = filtered['client_reply'] - filtered['client_sent']
    return np.mean(filtered['latency'])


if __name__ == '__main__':
    print(get_latency('/home/indy/total_reads2.csv'))
