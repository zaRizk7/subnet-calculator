from typing import List, Dict
from math import log2, ceil


def input_ip() -> List[int]:
    try:
        ip = list(map(int, input("Input IP Address: ").split(".")))
        assert len(ip) == 4, "Must have 4 octets!"
        assert all([0 <= octet <= 255 for octet in ip]), "Octet range is between 0-255!"
        return ip
    except Exception as e:
        print(f"Invalid input: {e.args[0]}")


def generate_netmask(prefix: int) -> List[int]:
    try:
        assert 4 <= prefix <= 32, "Prefix is between 4-32!"
        netmask_binary = [1 for i in range(prefix)]
        netmask_binary.extend(0 for i in range(32 - prefix))
        netmask = [
            int("".join(str(bit) for bit in netmask_binary[i : i + 8]), 2)
            for i in range(0, 32, 8)
        ]
        return netmask
    except Exception as e:
        print(f"Error: {e.args[0]}")


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
    return subnet_info


def generate_subnet_info(subnet_list: List[Dict], initial_net_id) -> List[Dict]:
    for i in range(len(subnet_list)):
        size = subnet_list[i]["size"]
        if i == 0:
            subnet_list[i]["network-id"] = initial_net_id
            subnet_list[i]["broadcast-id"] = generate_broadcast_id(initial_net_id, size)
        else:
            net_id = subnet_list[i - 1]["broadcast-id"].copy()
            for j in range(len(net_id) - 1):
                if net_id[j + 1] >= 255:
                    net_id[j] += 1
                    net_id[j + 1] = 0
            if net_id[-1] > 0:
                net_id[-1] += 1
            subnet_list[i]["network-id"] = net_id
            subnet_list[i]["broadcast-id"] = generate_broadcast_id(net_id, size)

    return subnet_list


def sort_subnet_list(subnet_list: List[Dict]) -> List[Dict]:
    return sorted(subnet_list, key=lambda subnet: subnet["size"], reverse=True)


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
            print(subnet_list)
            break
        except Exception as e:
            print(f"Error: {e.args[0]}")
