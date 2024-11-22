from rasterio.warp import reproject, Resampling
import numpy as np

def apply_na_mask(dataset_path, mask_paths):
    """
    Apply one or more masks to a dataset, preserving the dataset's original resolution and extent.
    """
    with rasterio.open(dataset_path) as src:
        # Read the dataset metadata
        dataset_transform = src.transform
        dataset_crs = src.crs
        dataset_width = src.width
        dataset_height = src.height
        nodata = src.nodata if src.nodata is not None else np.nan

        # Read the original dataset data
        original_data = src.read(1)
        
        # Initialize the mask aligned to the dataset's resolution
        aligned_mask = np.zeros((dataset_height, dataset_width), dtype=bool)

        # Reproject and align each mask to the dataset grid
        for mask_path in mask_paths:
            with rasterio.open(mask_path) as mask_src:
                # Create an array to store the reprojected mask
                mask_aligned = np.empty((dataset_height, dataset_width), dtype=np.uint8)

                reproject(
                    source=rasterio.band(mask_src, 1),
                    destination=mask_aligned,
                    src_transform=mask_src.transform,
                    src_crs=mask_src.crs,
                    dst_transform=dataset_transform,
                    dst_crs=dataset_crs,
                    resampling=Resampling.nearest
                )

                # Combine the aligned mask with the current mask
                aligned_mask |= mask_aligned.astype(bool)

    # Apply the mask to the dataset data
    original_data[aligned_mask] = nodata

    # Save the masked dataset
    dir_name, base_name = os.path.split(dataset_path)
    output_path = os.path.join(dir_name, base_name.replace('.tif', '_masked.tif'))

    profile = src.profile
    profile.update({'nodata': nodata})

    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(original_data, 1)
    print(f"Masked dataset saved to: {output_path}")



# Paths
canada_mask = "/projects/arctic/share/ABoVE_Biomass/OtherSpatialDatasets/CommonNA_Canada_Mask.tif"
alaska_mask = "/projects/arctic/share/ABoVE_Biomass/OtherSpatialDatasets/CommonNA_Alaska_Mask.tif"
canada_datasets = ["/projects/arctic/share/ABoVE_Biomass/Guindon2023/Guindon2023_102001.tif",
                    "/projects/arctic/share/ABoVE_Biomass/Matasci2018/matasci_102001.tif"]
canada_alaska_datasets =["/projects/arctic/share/ABoVE_Biomass/Duncanson2023/Duncanson2023_102001.tif", 
                        "/projects/arctic/share/ABoVE_Biomass/Soto-Navarro2020/Soto2020_102001.tif",
                      "/projects/arctic/share/ABoVE_Biomass/SpawnGibbs2020/SpawnGibbs2020_mask_102001.tif"]

# Apply Canada mask to Canada datasets
for dataset in canada_datasets:
    apply_na_mask(dataset, [canada_mask])

# Apply both masks to Canada-Alaska datasets
#for dataset in canada_alaska_datasets:
#    apply_na_mask(dataset, [canada_mask, alaska_mask])
