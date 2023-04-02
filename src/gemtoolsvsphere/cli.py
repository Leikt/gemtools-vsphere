from pathlib import Path
from typing import Optional

from gemtoolsconfig import Configurations, preset_file_loader
from gemtoolsio import decrypt

VALID_GETTERS = ['all', 'hosts', 'vms', 'vm-summaries']


def _load_config(args):
    # Load configuration
    Configurations.add_loader(preset_file_loader(args.config.parent, args.config_key))
    config = Configurations.load_config(path=args.config.name)

    # Decrypt passwords
    password_key: Optional[Path] = args.config_password_key
    if password_key is not None:
        for conf_client in config['client']:
            conf_client['password'] = decrypt(conf_client['password'], password_key.read_bytes())

    return config


def cmd_get(args):
    config = _load_config(args)
    print(config)
