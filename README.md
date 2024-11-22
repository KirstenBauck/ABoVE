# ABoVE
Processing Scripts used in ABoVE Biomass Project

## Processing Datasets
Anything that was used to process the datasets further is located in `scripts/datasets`. The following steps were taken
1. Reproject Matasci dataset into ESRI:102001 in order to create a common NA Mask using `reproject_matasci.sh`
2. Reproject Duncanson dataset into ESRI:102001 in order to create a common NA Mask. This was done in multiple steps as it was found the original Duncanson merged tif file was bad.
    1. Download the Duncanson tiles from the [ORNAL DAAC website](https://daac.ornl.gov/ABOVE/guides/Boreal_AGB_Density_ICESat2.html). This can be run using the `submit_duncanson_download.sh` script. (**Note:** One will first need to order the data and then swap the link in the `download_duncnason.py` script, as this dataset does not have API access as of Novemebr 2024)
    2. Mosaic and reproject the downloaded tiles using gdal in the `mosaic_reproject_duncanson.sh` script.

## Creating and Applying the Common NA Mask
Of the 7 different datasets, each masked out different things as no data. For example, one dataset may have only masked out bodies of water, while another may have masked out bodies of water and baren ground. In order to acurately calculate statisticsa cross the datasets, we want to create a Common NA Mask. This mask will then be applied across the datasets before calculating statistics.
1. Create the Common NA Mask using `submit_na_mask.sh <type>`. Where `<type>` is either `Canada` or `Alaska`, creating an NA mask for each of those regions. As of right now, the Kraatz, Wang, and Xu dataset are excluded from this creation for the following reasons
   
    - Kraatz: Covers a tiny area that would not be useful in creating the na mask
    - Wang: Covers a small area that would mask out too many values in the other datasets
    - Xu: Resolution is too high (10,000m/pixel) compare to other datasets
3. Apply the Common NA Mask using `submit_apply_mask.sh`

## Calculate Zonal Statisics
Zonal statistics for the EPA level 2 regions and the Alaska/Canada proviences can be calculate using `sbatch submit_zonal_stats.sh <input_raster_file> <script_type> <coverage_ratio>` where: 

    - `<input_raster_file>` is the dataset in `.tif` format.
    - `<script_type>` is `CanadaAlaska` or `EPA2` representing what type of zonal statisics to calculate
    - `<coverage_ratio>` is the acceptance ratio that the dataset covers a specfic zonal region. It is recommended to set this to 90.
