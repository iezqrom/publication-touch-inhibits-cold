import socket

hostname = socket.gethostname()
if hostname == 'quehaceres':
    base_path = '/home/ivan/Documents/aaa_online_stuff/coding/phd/publication-touch-inhibits-cold'
elif hostname == 'poulet05':
    base_path = '/home/iezquer/Nextcloud/coding/phd/publication-touch-inhibits-cold'
else:
    base_path = None
    
data_path = f"{base_path}/data"
figures_path = f"{base_path}/figures"