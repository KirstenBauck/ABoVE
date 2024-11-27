import os
import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling
from rasterio.mask import mask

def apply_na_mask(dataset_path, mask_path):
    """
    Apply a single mask to a dataset, preserving the dataset's original resolution and extent.
    Save the masked dataset to a new file.
    """
    with rasterio.open(dataset_path) as src:
        # Read the dataset metadata
        dataset_transform = src.transform
        dataset_crs = src.crs
        nodata = src.nodata if src.nodata is not None else np.nan
        profile = src.profile

        # Ensure the data type supports NaN if nodata is NaN
        if nodata is None:
            print("NoData value is not set in the dataset. Defaulting to NaN.")
            nodata = np.nan
            profile.update(dtype=rasterio.float32)
        elif np.isnan(nodata):
            profile.update(dtype=rasterio.float32)

        # Prepare output file path
        dir_name, base_name = os.path.split(dataset_path)
        output_path = os.path.join(dir_name, base_name.replace('.tif', '_masked.tif'))
        profile.update({'nodata': nodata})

        # Open the mask raster
        with rasterio.open(mask_path) as mask_src, rasterio.open(output_path, 'w', **profile) as dst:
            try:
                for ji, window in src.block_windows(1):
                    # Read the data for this window
                    original_data = src.read(1, window=window)

                    # Ensure data supports NaN values
                    if np.isnan(nodata):
                        original_data = original_data.astype(np.float32)

                    # Reproject the mask to align with the current window
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

                    # Apply the mask to the data
                    mask_bool = mask_aligned.astype(bool)
                    original_data[mask_bool] = nodata

                    # Write the masked data for this window
                    dst.write(original_data, 1, window=window)
            except Exception as e:
                print(f"Error processing raster: {e}")


    print(f"Masked dataset saved to: {output_path}")


# Paths
canada_mask = "/projects/arctic/share/ABoVE_Biomass/OtherSpatialDatasets/CommonNA_Canada_Mask.tif"
alaska_mask = "/projects/arctic/share/ABoVE_Biomass/OtherSpatialDatasets/CommonNA_Alaska_Mask.tif"
canada_datasets = ["/projects/arctic/share/ABoVE_Biomass/Guindon2023/Guindon2023_102001.tif",
                    "/projects/arctic/share/ABoVE_Biomass/Matasci2018/matasci_102001.tif"]
canada_alaska_datasets =[ "/projects/arctic/share/ABoVE_Biomass/Soto-Navarro2020/Soto2020_102001.tif",
                      "/projects/arctic/share/ABoVE_Biomass/SpawnGibbs2020/SpawnGibbs2020_mask_102001.tif",
                      "/projects/arctic/share/ABoVE_Biomass/Duncanson2023/Duncanson2023_102001.tif"]

# Apply both masks to Canada-Alaska datasets
#for dataset in canada_alaska_datasets:
#    apply_na_mask(dataset, alaska_mask)

# Apply Canada mask to Canada datasets
#for dataset in canada_datasets:
#    apply_na_mask(dataset, canada_mask)

apply_na_mask("/projects/arctic/share/ABoVE_Biomass/Duncanson2023/Duncanson2023_102001.tif", alaska_mask)
