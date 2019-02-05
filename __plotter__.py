import matplotlib.pyplot as plt
import pandas as pd


def plot():
    path1 = '/home/indy/1983_04_02_2019/node1.csv'
    path2 = '/home/indy/1983_04_02_2019/node15.csv'
    path3 = '/home/indy/1983_04_02_2019/node20.csv'
    path4 = '/home/indy/1983_04_02_2019/node25.csv'

    metrics = ['ordered_batch_size_per_sec', 'backup_ordered_batch_size_per_sec',
               'avg_monitor_avg_latency', 'avg_request_queue_size', 'avg_monitor_unordered_request_queue_size',
               'max_view_change_in_progress', 'max_current_view',
               'max_domain_ledger_size', 'timestamp']

    pd.read_csv(path1).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='cool', title='Node 1', figsize=(9, 4))
    pd.read_csv(path2).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='jet', title='Node 15', figsize=(9, 4))
    pd.read_csv(path3).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='rainbow', title='Node 20', figsize=(9, 4))
    pd.read_csv(path4).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='gist_rainbow', title='Node 25', figsize=(9, 4))

    plt.show()


if __name__ == '__main__':
    plot()
