import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def plot_metrics(paths):
    titles = [path.split('/')[-1].replace('.csv', '') for path in paths]
    metrics = ['ordered_batch_size_per_sec', 'backup_ordered_batch_size_per_sec',
               'avg_monitor_avg_latency', 'avg_request_queue_size', 'avg_monitor_unordered_request_queue_size',
               'max_view_change_in_progress', 'max_current_view',
               'max_domain_ledger_size', 'timestamp']
    # metrics = ['max_view_change_in_progress', 'max_current_view',
    #            'max_domain_ledger_size', 'timestamp']
    for path, title in zip(paths, titles):
        pd.read_csv(path).loc[:, metrics].\
            plot(x='timestamp', subplots=True, cmap='cool', title=title, figsize=(9.5, 4.5))
    plt.show()


def plot_client_stats(path):
    data = pd.read_csv(path, sep='|')
    data = data.loc[data['status'] == 'succ', :]
    data['latency'] = data['client_reply'] - data['client_sent']
    test_time = np.max(data['client_reply']) - np.min(data['client_sent'])
    print('MEAN LATENCY: {}'.format(np.mean(data['latency'])))
    print('MEAN THROUGHPUT: {}'.format(len(data.index)/test_time))


if __name__ == '__main__':
    # plot_metrics(['/home/indy/1965_15_02_2019/node5.csv',
    #               '/home/indy/1965_15_02_2019/node10.csv',
    #               '/home/indy/1965_15_02_2019/node20.csv',
    #               '/home/indy/1965_15_02_2019/node25.csv'])
    plot_client_stats('/home/indy/total_writes.csv')
