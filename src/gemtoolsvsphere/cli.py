from pathlib import Path
from typing import Optional

from gemtoolsconfig import Configurations, preset_file_loader
from gemtoolsio import decrypt

VALID_GETTERS = ['all', 'hosts', 'vms', 'vm-summaries']


def cmd_get(args):
    # Load configuration
    file: Path = args.config
    key: Optional[Path] = args.config_key
    Configurations.add_loader(preset_file_loader(file.parent, key))
    Configurations.load_config(path=file.name)
    config = Configurations.get_config()

    # Read configuration
    password_key: Optional[Path] = args.config_password_key
    for conf_client in config['client']:
        if password_key is not None:
            conf_client['password'] = decrypt(conf_client['password'], password_key.read_bytes())
        print(conf_client)
