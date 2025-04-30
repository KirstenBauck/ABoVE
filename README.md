# ABoVE Biomass Processing Scripts

Scripts used in the ABoVE Biomass Project to preprocess datasets, apply a common NoData mask, calculate zonal statistics, and analyze fire disturbance and timber harvest.

---

## 📁 Directory Structure

- `data/` - Some of the data used throughout this project
- `scripts/datasets/` – Scripts used for dataset reprojection and mosaicking.
- `scripts/` - Scripts used for creating & applying NA mask and calculating zonal statistics
- `jupyter_notebooks/` – Jupyter notebooks for visualizing zonal statistics.
- `ABoVE_Biomass_Analysis.Rmd` – RMarkdown report for fire and harvest analysis.

---

## 📦 Dataset Preprocessing

### 1. Matasci Dataset

- Reprojected to `ESRI:102001` and converted to BigTIFF using:
```bash
sbatch scripts/datasets/reproject_matasci.sh
```

### 2. Duncanson Dataset

- Original merged TIFF was bad → used only the first layer of tiles
- Mosaiced and Reprojected the tiles using:
```bash
sbatch scripts/datasets/mosaic_reproject_duncanson.sh
```

---

## 🗺️ Common NA Mask Creation & Application

To ensure consistency in data coverage, I created a Common NA Mask to account for differences in what each dataset marked as "no data".

### 1. Create Individual NA Masks
```bash
sbatch submit_na_mask.sh <type>  # type = Canada or ABoVE
```

Excluded Datasets:
- Kraatz: Limited spatial coverage
- Xu: Resolution mismatch (10,000m/pixel) <-- A shape file extraction and analysis will be applied at resolution later on.
- Matasci: High NoData due to exclusion of non-treed/low-quality (cloudy, high disturbance) plots <-- A shape file extraction and analysis will be applied at resolution later on.

Fixes for undefined NoData values in Matasci and Wang:
```python
#filename = '../Matasci2018/matasci_102001_bigtiff.tif'
filename = "../Wang2020/Wang102001.tif"

nodata = 0.0
ras = gdal.Open(filename, GA_Update)
for i in range(1, ras.RasterCount + 1):
    ras.GetRasterBand(i).SetNoDataValue(nodata)
ras = None
```

### 2. Combine Masks

```bash
sbatch submit_combine_masks.sh
```

### 3. Apply the Common NA Mask

```bash
sbatch submit_apply_mask.sh
```

---

## 📊 Zonal Statistics

Calculate statistics for:

- EPA Level 2 regions
- Canadian provinces & Alaskan regions

```bash
sbatch submit_zonal_stats.sh <input_raster_file> <script_type> <coverage_ratio>
```

Arguments:

- <input_raster_file>: Path to .tif dataset
- <script_type>: CanadaAlaska or EPA2
- <coverage_ratio>: Minimum coverage % (e.g., 45 recommended)

Preprocessing for EPA Level 2 regions

```python
from shapely.ops import unary_union
epa_shapefile = "../OtherSpatialDatasets/EPA_ecoregion_lvl2_clipped_102001.shp"
shapes = gpd.read_file(epa_shapefile)
combined_gdf = shapes.groupby(['NA_L2CODE', 'NA_L2NAME', 'NA_L2KEY']).agg({'geometry': unary_union}).reset_index()
combined_gdf = combined_gdf[['NA_L2CODE', 'NA_L2NAME', 'NA_L2KEY', 'geometry']]
combined_gdf = combined_gdf.set_geometry('geometry')
combined_gdf.to_file("../OtherSpatialDatasets/EPA_ecoregion_lvl2_102001.shp")
```

---

## 📈 Visualizing Zonal Statistics
Use this Jupyter notebook to generate graphs: `jupyter_notebooks/Create_Stats_Graphs.ipynb `

To configure:
- Specify the path to `zonal_stats*.txt`
- Choose visualization type: `EPA2` or `CanadaAlaska`

---

## 🔥/🌳 Fire Disturbance & Timber Harvest

1. Reproject masked datasets to EPSG:4326:
    ```bash
    sbatch scripts/datasets/reproject_datasets_epsg4326.sh
    ```
2. Generate final tables and visuals using: `ABoVE_Biomass_Analysis.Rmd`