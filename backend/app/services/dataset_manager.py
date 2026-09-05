datasets = {}
active_dataset_id = None


def register_dataset(
    dataset_id: str,
    filename: str,
    file_path: str,
    dataset_type: str = "original",
    parent_dataset: str | None = None,
):
    global active_dataset_id

    datasets[dataset_id] = {
        "dataset_id": dataset_id,
        "filename": filename,
        "file_path": file_path,
        "dataset_type": dataset_type,
        "parent_dataset": parent_dataset,
    }

    if active_dataset_id is None:
        active_dataset_id = dataset_id

    return datasets[dataset_id]


def get_dataset(dataset_id: str):
    return datasets.get(dataset_id)


def get_all_datasets():
    return list(datasets.values())


def set_active_dataset(dataset_id: str):
    global active_dataset_id

    if dataset_id not in datasets:
        return None

    active_dataset_id = dataset_id
    return datasets[dataset_id]


def get_active_dataset():
    if active_dataset_id is None:
        return None

    return datasets.get(active_dataset_id)


def get_active_dataset_id():
    return active_dataset_id
