

def parse_labels(cfg):
    """
    Parse labels to dict where label is key and list
    of patterns is corresponding value

    cfg: ConfigParser with loaded configuration of labels
    """
    return {
        label: list(filter(None, cfg['labels'][label].splitlines()))
        for label in cfg['labels']
    }
