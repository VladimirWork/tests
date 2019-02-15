import numpy as np
import pandas as pd


def get_latency(filename):
    data = pd.read_csv(filename, sep='|')
    data = data.loc[data['status'] == 'succ', :]
    data['latency'] = data['client_reply'] - data['client_sent']
    return np.mean(data['latency'])


if __name__ == '__main__':
    print(get_latency('/home/indy/total_reads10.csv'))
