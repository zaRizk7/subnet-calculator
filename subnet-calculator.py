from typing import List, Dict
from math import log2, ceil
from pandas import DataFrame


def input_ip() -> List[int]:
    ip = list(map(int, input("Input IP Address: ").split(".")))
    assert len(ip) == 4, "Must have 4 octets!"
    assert all([0 <= octet <= 255 for octet in ip]), "Octet range is between 0-255!"
    return ip


def generate_netmask(prefix: int) -> List[int]:
    assert 4 <= prefix <= 32, "Prefix is between 4-32!"
    netmask_binary = [1 for i in range(prefix)]
    netmask_binary.extend(0 for i in range(32 - prefix))
    netmask = [
        int("".join(str(bit) for bit in netmask_binary[i : i + 8]), 2)
        for i in range(0, 32, 8)
    ]
    return netmask


def generate_network_id(ip: List[int], netmask: List[int]) -> List[int]:
    network_id = [
        ip_octet & netmask_octet for ip_octet, netmask_octet in zip(ip, netmask)
    ]
    return network_id


def generate_broadcast_id(network_id: List[int], size) -> List[int]:
    prefix = generate_prefix(size)
    netmask = generate_netmask(prefix)
    netmask_inverted = invert_ip(netmask)
    broadcast_id = [
        net_octet | net_inv_octet
        for net_octet, net_inv_octet in zip(network_id, netmask_inverted)
    ]
    return broadcast_id


def generate_prefix(size: int) -> int:
    assert size >= 2, "Minimum size is 2!"
    if size in [2 ** i for i in range(1, 32)]:
        size += 1
    prefix = 32 - ceil(log2(size))
    return prefix


def generate_allocated_count(prefix: int) -> int:
    allocated_count = 2 ** (32 - prefix)
    return allocated_count


def invert_ip(ip: List[int]) -> List[int]:
    ip_inverted = [255 ^ octet for octet in ip]
    return ip_inverted


def generate_initial_subnet_info(name: str, size: int) -> Dict:
    subnet_info = {}
    prefix = generate_prefix(size)
    allocated_size = generate_allocated_count(prefix)
    subnet_info["name"] = name
    subnet_info["size"] = size
    subnet_info["allocated-size"] = allocated_size
    subnet_info["prefix"] = prefix
    subnet_info["netmask"] = generate_netmask(prefix)
    return subnet_info


def generate_subnet_info(subnet_list: List[Dict], initial_net_id) -> List[Dict]:
    net_id = initial_net_id.copy()
    for i in range(len(subnet_list)):
        size = subnet_list[i]["size"]
        if i > 0:
            net_id = subnet_list[i - 1]["broadcast-id"].copy()
            if net_id[-1] > 0 and net_id[-1] < 255:
                net_id[-1] += 1
            else:
                for j in range(len(net_id) - 1):
                    if net_id[j + 1] >= 255:
                        net_id[j] += 1
                        net_id[j + 1] = 0
        subnet_list[i]["network-id"] = net_id.copy()
        subnet_list[i]["broadcast-id"] = generate_broadcast_id(net_id, size)

    return subnet_list


def generate_host_range(subnet_list: List[Dict]) -> List[Dict]:
    for i in range(len(subnet_list)):
        host_min = subnet_list[i]["network-id"].copy()
        host_min[-1] += 1
        host_max = subnet_list[i]["broadcast-id"].copy()
        host_max[-1] -= 1
        subnet_list[i]["min-host"] = host_min
        subnet_list[i]["max-host"] = host_max
    return subnet_list


def sort_subnet_list(subnet_list: List[Dict]) -> List[Dict]:
    return sorted(subnet_list, key=lambda subnet: subnet["size"], reverse=True)


def convert_list_to_ip(ip: List[int]) -> str:
    return ".".join(str(octet) for octet in ip)


def export_to_excel(subnet_list: List[Dict]):
    column_order = [
        "name",
        "size",
        "allocated-size",
        "prefix",
        "netmask",
        "network-id",
        "min-host",
        "max-host",
        "broadcast-id",
    ]
    for i in range(len(subnet_list)):
        netmask = subnet_list[i]['netmask']
        netmask = convert_list_to_ip(netmask)
        subnet_list[i]['netmask'] = netmask
        network_id = subnet_list[i]["network-id"]
        network_id = convert_list_to_ip(network_id)
        subnet_list[i]["network-id"] = network_id
        broadcast_id = subnet_list[i]["broadcast-id"]
        broadcast_id = convert_list_to_ip(broadcast_id)
        subnet_list[i]["broadcast-id"] = broadcast_id
        host_min = subnet_list[i]["min-host"]
        host_min = convert_list_to_ip(host_min)
        subnet_list[i]["min-host"] = host_min
        host_max = subnet_list[i]["max-host"]
        host_max = convert_list_to_ip(host_max)
        subnet_list[i]["max-host"] = host_max
    df = DataFrame(subnet_list)
    df = df[column_order]
    df.to_excel("subnet-table.xlsx")
    df.to_csv("subnet-table.csv")


if __name__ == "__main__":
    subnet_list = []
    while True:
        try:
            ip = input_ip()
            prefix = int(input("Prefix: "))
            netmask = generate_netmask(prefix)
            net_id = generate_network_id(ip, netmask)
            subnet_count = int(input("How many subnets: "))
            for i in range(subnet_count):
                size, *name = input("Input (host count, subnet name): ").split()
                size, name = int(size), " ".join(name)
                subnet_info = generate_initial_subnet_info(name, size)
                subnet_list.append(subnet_info)
            subnet_list = sort_subnet_list(subnet_list)
            subnet_list = generate_subnet_info(subnet_list, net_id)
            subnet_list = generate_host_range(subnet_list)
            export_to_excel(subnet_list)
            break
        except Exception as e:
            print(f"Error: {e.args[0]}, Please try again!")
