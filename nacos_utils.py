from dotenv import load_dotenv
import os
import socket
import nacos

load_dotenv()

# Both HTTP/HTTPS protocols are supported, if not set protocol prefix default is HTTP, and HTTPS with no ssl check(verify=False)
# "192.168.3.4:8848" or "https://192.168.3.4:443" or "http://192.168.3.4:8848,192.168.3.5:8848" or "https://192.168.3.4:443,https://192.168.3.5:443"
SERVER_ADDRESSES = os.environ.get("NACOS_SERVER_ADDRESSES")
NAMESPACE = os.environ.get("NACOS_NAMESPACE")

# no auth mode
client = nacos.NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE)
# auth mode
#client = nacos.NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE, ak="{ak}", sk="{sk}")

my_ip = socket.gethostbyname(socket.gethostname())
my_port = os.getenv("PORT")

# get config
data_id = "datasource"
group = "DEFAULT_GROUP"
nacos_config = client.get_config(data_id, group)

def nacos_add():
    client.add_naming_instance("agi-provider", my_ip, my_port)

def nacos_remove():
    client.remove_naming_instance("agi-provider", my_ip, my_port)