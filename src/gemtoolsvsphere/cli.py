from pathlib import Path
from typing import Optional

from gemtoolsconfig import Configurations, preset_file_loader


def cmd_get(args):
    # Load configuration
    file: Path = args.config
    key: Optional[Path] = args.config_key
    Configurations.add_loader(preset_file_loader(file.parent, key))
    Configurations.load_config(path=file.name)
    config = Configurations.get_config()

    # Read configuration
    for conf_client in config['clients']:
        print(conf_client)
