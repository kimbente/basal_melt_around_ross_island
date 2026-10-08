import torch

# All data is a bit dense (and memory intensive), so we spatially subsample
def spatial_subsample(data, n_cells = 100):
    x, y = data[:, 0], data[:, 1]

    # Compute integer cell indices
    ix = torch.clamp((x * n_cells).long(), max = n_cells - 1)
    iy = torch.clamp((y * n_cells).long(), max = n_cells - 1)
    cell_ids = ix * n_cells + iy   # [N]

    # Shuffle indices to randomize
    perm = torch.randperm(data.shape[0])
    cell_ids_perm = cell_ids[perm]

    # Get inverse mapping: which unique id each entry belongs to
    unique_ids, inv = torch.unique(cell_ids_perm, return_inverse = True)

    # First index per unique id = argmin within each group
    # Build a large index tensor and take the min
    arange = torch.arange(len(cell_ids_perm), device = data.device)
    first_idx = torch.full((len(unique_ids),), len(cell_ids_perm), device = data.device)

    first_idx = first_idx.scatter_reduce(0, inv, arange, reduce = "amin", include_self = True)

    # Map back to permuted indices
    chosen = perm[first_idx]

    return data[chosen]