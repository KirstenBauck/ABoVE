import rasterio
import numpy as np
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin

def combine_masks(mask_path_1, mask_path_2, output_path):
    with rasterio.open(mask_path_1) as src1, rasterio.open(mask_path_2) as src2:
        # Step 1: Get the combined extent
        min_x = min(src1.bounds.left, src2.bounds.left)
        max_x = max(src1.bounds.right, src2.bounds.right)
        min_y = min(src1.bounds.bottom, src2.bounds.bottom)
        max_y = max(src1.bounds.top, src2.bounds.top)

        # Step 2: Define the target resolution and transform
        res = src1.res[0]  # Use the resolution of the first mask
        target_width = int((max_x - min_x) / res)
        target_height = int((max_y - min_y) / res)
        target_transform = from_origin(min_x, max_y, res, res)  # Correct transform

        # Step 3: Define the target profile
        target_profile = {
            'driver': 'GTiff',
            'dtype': 'uint8',
            'nodata': 1,  # Define 1 as no-data
            'count': 1,
            'height': target_height,
            'width': target_width,
            'crs': src1.crs,  # Use CRS from the first mask
            'transform': target_transform,
            'compress': 'lzw'  # Optional: compression to save space
        }

        # Step 4: Resample both masks to the target grid
        resampled_mask_1 = np.ones((target_height, target_width), dtype=np.uint8)
        resampled_mask_2 = np.ones((target_height, target_width), dtype=np.uint8)

        reproject(
            source=src1.read(1),
            destination=resampled_mask_1,
            src_transform=src1.transform,
            src_crs=src1.crs,
            dst_transform=target_transform,
            dst_crs=src1.crs,
            resampling=Resampling.nearest,
            src_nodata=1,
            dst_nodata=1
        )

        reproject(
            source=src2.read(1),
            destination=resampled_mask_2,
            src_transform=src2.transform,
            src_crs=src2.crs,
            dst_transform=target_transform,
            dst_crs=src1.crs,
            resampling=Resampling.nearest,
            src_nodata=1,
            dst_nodata=1
        )

        # Step 5: Combine masks using logical AND (keep valid data where either mask is 0)
        combined_mask = np.logical_and(resampled_mask_1, resampled_mask_2).astype(np.uint8)

        # Step 6: Write the combined mask
        with rasterio.open(output_path, 'w', **target_profile) as dst:
            dst.write(combined_mask, 1)

    print(f"Combined mask saved to: {output_path}")

# Usage
directory = "/projects/arctic/share/ABoVE_Biomass"
mask_path_1 = f"{directory}/OtherSpatialDatasets/CommonNA_ABoVE_Mask.tif"
mask_path_2 = f"{directory}/OtherSpatialDatasets/CommonNA_Canada_Mask.tif"
output_path = f"{directory}/OtherSpatialDatasets/Combined_Mask.tif"
combine_masks(mask_path_1, mask_path_2, output_path)
