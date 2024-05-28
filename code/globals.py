import socket

hostname = socket.gethostname()
if hostname == 'quehaceres':
    base_path = '/home/ivan/Documents/aaa_online_stuff/coding/phd/publication-touch-inhibits-cold'
elif hostname == 'poulet05':
    base_path = '/home/iezquer/Nextcloud/coding/phd/publication-touch-inhibits-cold'
    videos_path = '/media/iezquer/ivan_lab/phd'
else:
    base_path = None
    
data_path = f"{base_path}/data"
figures_path = f"{base_path}/figures"

to_analyse_exp1 = [
    "28052021_3",
    "28052021_2",
    "28052021_1",
    "27052021_1",
    "24052021_1",
    "21052021_3",
    "21052021_2",
    "20052021_1",
    "18052021_1",
    "14052021_1",
    "07052021_2",
    "08062021_1",
]