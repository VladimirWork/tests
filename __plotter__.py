import matplotlib.pyplot as plt
import pandas as pd


def plot():
    path1 = '/home/indy/1965_28_01_2019/node1.csv'
    path2 = '/home/indy/1965_28_01_2019/node6.csv'
    path3 = '/home/indy/1965_28_01_2019/node11.csv'
    path4 = '/home/indy/1965_28_01_2019/node16.csv'

    metrics = ['ordered_batch_size_per_sec', 'backup_ordered_batch_size_per_sec',
               'avg_monitor_avg_latency', 'avg_request_queue_size',
               'max_view_change_in_progress', 'max_current_view',
               'max_domain_ledger_size', 'timestamp']

    pd.read_csv(path1).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='cool', title='Node 1', figsize=(9, 4))
    pd.read_csv(path2).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='jet', title='Node 6', figsize=(9, 4))
    pd.read_csv(path3).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='rainbow', title='Node 11', figsize=(9, 4))
    pd.read_csv(path4).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='gist_rainbow', title='Node 16', figsize=(9, 4))

    plt.show()


if __name__ == '__main__':
    plot()
