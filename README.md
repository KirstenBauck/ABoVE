# ABoVE
Processing Scripts used in ABoVE Biomass Project

## Processing Datasets
Anything that was used to process the datasets further is located in `scripts/datasets`. The following steps were taken
1. Reproject Matasci dataset into ESRI:102001 and then make it into a BigTIFF file type in order to create a common NA Mask using `reproject_matasci.sh`
2. Reproject Duncanson dataset into ESRI:102001 in order to create a common NA Mask. This was done in multiple steps as it was found the original Duncanson merged tif file was bad, note that the first layer of the tiles was used.
    1. Select appropriate (Canda and Alaska regions) Duncanson tiles and download data tiles from [MAAP](https://docs.maap-project.org/en/latest/getting_started/getting_started.html#Signing-up-for-a-new-MAAP-account)
    2. Mosaic and reproject the downloaded tiles using gdal in the `mosaic_reproject_duncanson.sh` script.

## Creating and Applying the Common NA Mask
Of the 7 different datasets, each masked out different things as no data. For example, one dataset may have only masked out bodies of water, while another may have masked out bodies of water and baren ground. In order to acurately calculate statisticsa cross the datasets, we want to create a Common NA Mask. This mask will then be applied across the datasets before calculating statistics.
1. Create the Common NA Mask using `submit_na_mask.sh <type>`. Where `<type>` is either `Canada` or `ABoVE`, creating an NA mask for each of those regions. *Note: The `*.out` files are note included in this repo as there was nothing written to them.* As of right now, the Kraatz and Xu dataset are excluded from this creation for the following reasons.
   
    - Kraatz: Covers a tiny area that would not be useful in creating the na mask
    - Xu: Resolution is too high (10,000m/pixel) compared to other datasets <-- A shape file extraction and analysis will be applied at resolution later on.
2. Apply the Common NA Mask using `submit_apply_mask.sh`
3. The Common NA Mask was applied to Xu using `submit_apply_xu_mask.sh`

## Calculate Zonal Statistics
Zonal statistics for the EPA level 2 regions and the Alaska/Canada proviences can be calculate using `sbatch submit_zonal_stats.sh <input_raster_file> <script_type> <coverage_ratio>` where:

- `<input_raster_file>` is the dataset in `.tif` format.
- `<script_type>` is `CanadaAlaska` or `EPA2` representing what type of zonal statistics to calculate
 - `<coverage_ratio>` is the acceptance ratio that the dataset covers a specfic zonal region. It is recommended to set this to 35.

# Create charts of Zonal Statistics
After running `submit_zonal_stats.sh`, data can be visualized using the jupyter notebook `jupyter_notebooks/Create_Stats_Graphs.ipynb`. The notebook is set up in such a way where one only needs to specify where the `zonal_stats*.txt` files are located and which zonal stats one wants to visualize (EPA2 or CanadaAlaska).
