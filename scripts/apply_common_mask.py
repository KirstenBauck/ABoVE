import rasterio
import os
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
        nodata = src.nodata if src.nodata is not None else np.nan
        profile = src.profile

        # Prepare for writing output
        dir_name, base_name = os.path.split(dataset_path)
        output_path = os.path.join(dir_name, base_name.replace('.tif', '_masked.tif'))
        profile.update({'nodata': nodata})

        with rasterio.open(output_path, 'w', **profile) as dst:
            # Process the dataset in chunks (windows)
            for ji, window in src.block_windows(1):
                # Read the data for this window
                original_data = src.read(1, window=window)

                # Initialize the aligned mask for this window
                aligned_mask = np.zeros_like(original_data, dtype=bool)

                # Reproject and align each mask to this window
                for mask_path in mask_paths:
                    with rasterio.open(mask_path) as mask_src:
                        # Create an array to store the reprojected mask
                        mask_aligned = np.empty_like(original_data, dtype=np.uint8)

                        reproject(
                            source=rasterio.band(mask_src, 1),
                            destination=mask_aligned,
                            src_transform=mask_src.transform,
                            src_crs=mask_src.crs,
                            dst_transform=src.window_transform(window),
                            dst_crs=dataset_crs,
                            dst_width=window.width,
                            dst_height=window.height,
                            resampling=Resampling.nearest
                        )

                        # Combine with the current aligned mask
                        aligned_mask |= mask_aligned.astype(bool)

                # Apply the mask to the data
                original_data[aligned_mask] = nodata

                # Write the masked data to the output file
                dst.write(original_data, 1, window=window)
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
for dataset in canada_alaska_datasets:
    apply_na_mask(dataset, [canada_mask, alaska_mask])
