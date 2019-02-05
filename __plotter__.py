import matplotlib.pyplot as plt
import pandas as pd


def plot():
    path1 = '/home/indy/vc/node1.csv'
    path2 = '/home/indy/vc/node2.csv'
    path3 = '/home/indy/vc/node3.csv'
    path4 = '/home/indy/vc/node4.csv'

    # metrics = ['ordered_batch_size_per_sec', 'backup_ordered_batch_size_per_sec',
    #            'avg_monitor_avg_latency', 'avg_request_queue_size', 'avg_monitor_unordered_request_queue_size',
    #            'max_view_change_in_progress', 'max_current_view',
    #            'max_domain_ledger_size', 'timestamp']

    metrics = ['max_view_change_in_progress', 'max_current_view',
               'max_domain_ledger_size', 'timestamp']

    pd.read_csv(path1).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='cool', title='Node 1', figsize=(9, 4))
    pd.read_csv(path2).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='jet', title='Node 2', figsize=(9, 4))
    pd.read_csv(path3).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='rainbow', title='Node 3', figsize=(9, 4))
    pd.read_csv(path4).loc[:, metrics].plot\
        (x='timestamp', subplots=True, cmap='gist_rainbow', title='Node 4', figsize=(9, 4))

    plt.show()


if __name__ == '__main__':
    plot()
