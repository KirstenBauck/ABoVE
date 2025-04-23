import os
import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling
from rasterio.mask import mask
import traceback

def apply_na_mask(dataset_path, mask_path, name):
    """
    Apply a single mask to a dataset, preserving the dataset's original resolution and extent.
    Save the masked dataset to a new file.

    Args:
        dataset_path (str): Path to dataset to apply common mask to (should be of type `.tif`)
        mask_path (str): Path to common NA mask (should be of type `.tif`)
        name (str): Name of which type of mask was applied
    """
    with rasterio.open(dataset_path) as src:
        # Read the dataset metadata
        dataset_transform = src.transform
        dataset_crs = src.crs
        nodata = src.nodata if src.nodata is not None else np.nan
        profile = src.profile

        #This is just for Duncanson to ensure proper processing
        if os.path.basename(dataset_path) == "Duncanson2025_BigTIFF.tif":
            profile.update({'BIGTIFF': 'YES'})
            profile.update({'tiled': True})

        # Ensure the dataset is float and update the NoData value
        if np.isnan(nodata):
            print(f"NoData value is nan in {dataset_path}. Defaulting to 0.0.")
            nodata = 0.0
            profile.update({'nodata': 0.0, 'dtype': rasterio.float32})
        else:
            profile.update({'nodata': float(nodata)})  # Ensure nodata is explicitly set
        
        # Prepare output file path
        dir_name, base_name = os.path.split(dataset_path)
        output_path = os.path.join(dir_name, base_name.replace('.tif', f'_masked_{name}.tif'))

        # Open the mask raster
        with rasterio.open(mask_path) as mask_src, rasterio.open(output_path, 'w', **profile) as dst:
            try:
                for ji, window in src.block_windows(1):
                    # Read the data for this window
                    original_data = src.read(1, window=window)

                    # Ensure NoData values are consistent (replace nans with nodata)
                    original_data = np.nan_to_num(original_data, nan=nodata)

                    # Create a np array similar to the original data to fill in with masked values
                    mask_aligned = np.empty_like(original_data, dtype=np.uint8)

                    # Reproject the mask to align with the current window
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

                    # Replace any remaining NaN values in the data with the nodata value
                    original_data = np.nan_to_num(original_data, nan=nodata)

                    # Write the masked data for this window
                    dst.write(original_data, 1, window=window)

            # Something happened when processing the raster
            except Exception as e:
                error_details = traceback.format_exc()
                print(f"Error processing raster: {dataset_path}")
                print(f"Window indices: {ji}")  # Show the indices of the block being processed
                print(f"Window size: {window.width}x{window.height}")  # Show window size
                print(f"Window: {window}")
                print(f"Original data shape: {original_data.shape}")  # Show data shape
                print(f"Nodata value: {nodata}")  # Show the nodata value being used
                print(f"Error Message: {e}")  # Show the error message
                print("Traceback:")
                print(error_details)  # Show the full traceback

    print(f"Masked dataset saved to: {output_path}")


if __name__ == "__main__":
    # Change this variable as necessary
    directory = "/projects/arctic/share/ABoVE_Biomass"

    # Mask paths, made from `submit_na_mask.sh`
    canada_mask = f"{directory}/OtherSpatialDatasets/CommonNA_Canada_Mask.tif"
    above_mask = f"{directory}/OtherSpatialDatasets/CommonNA_ABoVE_Mask.tif"
    combined_mask = f"{directory}/OtherSpatialDatasets/Combined_Mask.tif"

    # Datasets to apply the masks to
    canada_datasets = [f"{directory}/Guindon2023/Guindon2023_102001.tif",
                        f"{directory}/Matasci2018/matasci_102001_bigtiff.tif"]
    above_datasets =[ f"{directory}/Wang2020/Wang102001.tif"]
    combined_datasets = [ f"{directory}/Soto-Navarro2020/Soto2020_102001.tif",
                            f"{directory}/SpawnGibbs2020/SpawnGibbs2020_mask_102001.tif",
                            f"{directory}/Duncanson2025/Duncanson2025_BigTIFF.tif",
                            f"{directory}/Xu2021/Xu2021_102001.tif"]

    # Apply ABoVE mask to ABoVE datasets
    for dataset in above_datasets:
        apply_na_mask(dataset, above_mask, 'ABoVE')

    # Apply Canada mask to Canada datasets
    for dataset in canada_datasets:
        apply_na_mask(dataset, canada_mask, 'Canada')
    
    # Apply both masks to datasets where they both apply
    for dataset in combined_datasets:
        apply_na_mask(dataset, combined_mask, 'Combined')
