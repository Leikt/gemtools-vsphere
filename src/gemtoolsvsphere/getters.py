from .client import VSphereClient


def get_hosts(client: VSphereClient) -> list:
    return client.get('/rest/vcenter/host')


def get_virtual_machine_summaries(client: VSphereClient) -> list:
    return client.get('/rest/vcenter/vm')


def get_virtual_machine(client: VSphereClient, summary: dict) -> dict:
    data = client.get(f'/rest/vcenter/vm/{summary["vm"]}')
    data['vm'] = summary['vm']
    return data


def get_all_virtual_machines(client: VSphereClient, summaries: list[dict]) -> list[dict]:
    data = []
    for summary in summaries:
        virtual_machine_data = get_virtual_machine(client, summary)
        data.append(virtual_machine_data)
    return data
