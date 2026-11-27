# ERDDAP files that need regenerating

49 of the 317 committed `.erddap` files under
`tests/records/hakai-metadata-entry-form-files/hakai` are **not well-formed XML**,
so ERDDAP will refuse them when it loads `datasets.xml`.

The generator was fixed in "Escape attribute text so the generated dataset.xml
is valid XML" (PR #21) - `_generate_dataset_xml` built the file by string
concatenation and escaped nothing, so any record whose text carried `&`, `<` or
`>` produced a broken file. The fix does not touch the already-committed
artifacts: **these 49 stay invalid on disk until the conversion is rerun.**

Rerunning any one of them is enough to fix it - there is nothing to edit in the
record itself. From a checkout of the records repo:

```bash
hakai_metadata_conversion convert \
    --input '<stem>.yaml' \
    --input-schema CIOOS \
    --output-format erddap \
    --output-dir .
```

A glob covering several records at once works too:

```bash
hakai_metadata_conversion convert \
    --input '*.yaml' \
    --input-schema CIOOS \
    --output-format erddap \
    --output-dir .
```

Note that bulk form only became safe with "Address Copilot review on #17": the
destination used to be computed once and reused, so a glob wrote every record
over the first one's file and left a single output behind. On an older install,
rerun them one at a time.

Verify afterwards with `python -c "from lxml import etree;
etree.parse('<stem>.erddap')"` - it should parse without error.

Breakdown: 35 fail on a bare ampersand, 11 on a bare angle bracket, 3 on both.

| Record | Catalogue | Breaks on | Where |
| --- | --- | --- | --- |
| Ancient Forest Wetlands, BC - Upper Fraser River - 2019 - Airborne Coast | [c3eff62f…](https://catalogue.hakai.org/dataset/ca-cioos_c3eff62f-bcee-4faa-a7e1-7b9380d94e74) | `&` | `summary`: …ata (TIFF) – 4 band orthophotos – RGB & NIR. Hyperspectral data …… |
| Bamfield Region UAV Imagery and Surface Model Data | [40d86401…](https://catalogue.hakai.org/dataset/ca-cioos_40d86401-0e95-4ff3-b1c7-25e4e9138157) | `& and < >` | `summary`: …Bamfield UAV Data Capture April 9 & 10th 2016. Hakai Institute: …… |
| Big Bar Slide - 2020 - Airborne Coastal Observatory Data | [82a543b1…](https://catalogue.hakai.org/dataset/ca-cioos_82a543b1-686c-45c9-a03d-4f93e0ab8e8a) | `&` | `summary`: …ata (TIFF) – 4 band orthophotos – RGB & NIR. Hyperspectral data …… |
| Bowhead Whale Drone Data Collection - Cumberland Sound - Nunavut | [35900174…](https://catalogue.hakai.org/dataset/ca-cioos_35900174-c64a-493e-9a7e-390ac7e997e4) | `&` | `creator_name`: …Whale Ecology & Conservation Lab… |
| Bute Inlet Geo-Hazards & Ramsay West - 2024 - Airborne Coastal Observato | [52d4f546…](https://catalogue.hakai.org/dataset/ca-cioos_52d4f546-dfdf-4bf1-b1ad-f6ec6f2663c0) | `&` | `title`: …Bute Inlet Geo-Hazards & Ramsay West - 2024 - Airborne… |
| Cloud-Based LiDAR Application - ELVIZ - Place Glacier, Mt. Robson, and E | [53730b70…](https://catalogue.hakai.org/dataset/ca-cioos_53730b70-be6f-4e24-8b9d-4a5e2c491121) | `&` | `summary`: …and export format types (e.g.,GeoTIFF & geopackage) to aid in la…… |
| Daily satellite (Sentinel 3A and 3B) chlorophyll and suspended matter co | [d1bef0b7…](https://catalogue.hakai.org/dataset/ca-cioos_d1bef0b7-4d15-4bc1-bf34-faca6352891f) | `< >` | `summary`: …shown to have low systematic biases (<1%) and follow expected se…… |
| Data record does not exist anymore: Geomorphology - Calvert Island | [9fafb4c8…](https://catalogue.hakai.org/dataset/ca-cioos_9fafb4c8-e61f-4372-ac71-c1ddbe57d80c) | `&` | `summary`: …following citation: Heathfield, D., & Team, H. G. T. (2016). Geo…… |
| Denali Fault - 2024 - Airborne LiDAR Survey | [f762a307…](https://catalogue.hakai.org/dataset/ca-cioos_f762a307-6dfb-41a8-a56c-ecacfb075a0a) | `&` | `contributor_name`: …tute;Hakai Institute;Kîsik Geospatial & Aerial Survey… |
| Fin Island & K'yel - 2020 - Airborne Coastal Observatory Data | [d2e83e40…](https://catalogue.hakai.org/dataset/ca-cioos_d2e83e40-9e95-4a47-a899-b37c744be3ab) | `&` | `title`: …Fin Island & K'yel - 2020 - Airborne Coasta… |
| Fountain Valley LiDAR Data - 2019 & 2020 - Hakai Airborne Coastal Observ | [bb59cb9e…](https://catalogue.hakai.org/dataset/ca-cioos_bb59cb9e-887a-40a3-b41a-f4a5b2263ce6) | `&` | `title`: …Fountain Valley LiDAR Data - 2019 & 2020 - Hakai Airborne Coasta…… |
| Fraser River Landslide Project - Sites of Concern 2024 | [f25b00ba…](https://catalogue.hakai.org/dataset/ca-cioos_f25b00ba-ad63-42b3-8021-3fb6aa99baff) | `&` | `summary`: …icular type of sediment layer (Clague & Evans, 2003) and detaile…… |
| Fucus Dynamics - Point Intercept Surveys - BC Central Coast | [52797e17…](https://catalogue.hakai.org/dataset/ca-cioos_52797e17-c0ed-46a4-9dcd-e34f801c6205) | `&` | `summary`: …ure and composition of the macroalgae & benthic invertebrate com…… |
| Gitanyow Archaeology, Cranberry Junction - 2020 - Airborne Coastal Obser | [0f524f76…](https://catalogue.hakai.org/dataset/ca-cioos_0f524f76-a88b-4e0a-9c3c-ee83114c3679) | `&` | `summary`: …ata (TIFF) – 4 band orthophotos – RGB & NIR. Hyperspectral data …… |
| Gitga'at Territory Coastal Mapping Project | [b5f0f854…](https://catalogue.hakai.org/dataset/ca-cioos_b5f0f854-efe1-4132-808d-074244d813e1) | `< >` | `summary`: …all surveys achieving an accuracy of <10 cm. Final digital eleva…… |
| Glacier and Icefield Mapping - British Columbia - 2019 - Airborne Coasta | [0ebfdd89…](https://catalogue.hakai.org/dataset/ca-cioos_0ebfdd89-61d6-453c-870a-83167617b26a) | `&` | `summary`: …ata (TIFF) – 4 band orthophotos – RGB & NIR. Hyperspectral data …… |
| Global Eutrophication Monitoring Dataset of Trinidad and Tobago | [741bd412…](https://catalogue.hakai.org/dataset/ca-cioos_741bd412-6387-4dcd-8d61-7046b949f406) | `&` | `creator_country`: …Trinidad & Tobago… |
| Google Earth Engine Kelp Tool - Central Coast Output | [2a92ca16…](https://catalogue.hakai.org/dataset/ca-cioos_2a92ca16-f5c6-4362-acea-6bb5117b8d65) | `&` | `summary`: …change. *Nijland, W., Reshitnyk, L., & Rubidge, E. (2019). Satel…… |
| Hakai Institute Nutrients (Dosser et al., 2021) | [476204a7…](https://catalogue.hakai.org/dataset/ca-cioos_476204a7-0714-4755-953d-61fa3c5df497) | `&` | `summary`: …son, J. M., Hannah, C. G., Evans, W., & Hunt, B. P. V. (2021). S…… |
| Hakai RPAS (Drone) Operations and Methods | [582909b1…](https://catalogue.hakai.org/dataset/ca-cioos_582909b1-c87d-4c5a-8594-5f44726f43a4) | `&` | `summary`: …nning Specifications • Ground Control & Field Methodologies • El…… |
| High-resolution record of 8-m seawater CO2 content entering Fanny Bay Oy | [77a256cd…](https://catalogue.hakai.org/dataset/ca-cioos_77a256cd-baf7-434e-9f62-53ba809e48cb) | `< >` | `summary`: …ocessing descriptions to Wiley Evans (<a href="mailto:wiley.evan…… |
| Imagery and Elevation Models for Monitoring Invertebrates at Intertidal  | [06ddfa63…](https://catalogue.hakai.org/dataset/ca-cioos_06ddfa63-2611-46a5-8d63-c1b576e85bcb) | `< >` | `summary`: …r for each survey is determined to be < 0.10 m. For several of t…… |
| Island Food Web Study - Central Coast Islands (100 Islands Project) - Ap | [5eda02a9…](https://catalogue.hakai.org/dataset/ca-cioos_5eda02a9-36b6-4875-91c9-989e9e06c5ad) | `&` | `title`: …Project) - April to July 2015, 2016, & 2017… |
| Juvenile pink and chum salmon diet study – Discovery Islands and Johnsto | [89b3c6d8…](https://catalogue.hakai.org/dataset/ca-cioos_89b3c6d8-983b-48f4-a0b5-04eea65602f6) | `< >` | `summary`: …stomach fullness values ranging from < 0.5% to > 5 % body weight…… |
| Kelp Field Data for Remote Sensing - BC Central Coast | [94b4992f…](https://catalogue.hakai.org/dataset/ca-cioos_94b4992f-19e2-46d4-875e-f0c952ea62f7) | `< >` | `summary`: …ta soaking for 5-10 seconds providing < 10 cm X / Y accuracy. Fi…… |
| Kilbella River Estuary LiDAR Survey - 2019 - Airborne Coastal Observator | [62de21ed…](https://catalogue.hakai.org/dataset/ca-cioos_62de21ed-90fb-422a-9c55-29c513a00f95) | `&` | `summary`: …ata (TIFF) – 4 band orthophotos – RGB & NIR. Hyperspectral data …… |
| Killer Whale Foraging Drone Observations - Coastal British Columbia - 20 | [1815be54…](https://catalogue.hakai.org/dataset/ca-cioos_1815be54-9081-4031-80fa-d3d071340a7d) | `&` | `title`: …ons - Coastal British Columbia - 2019 & 2020… |
| Knight Inlet Multibeam Bathymetry Survey | [6c34ed6e…](https://catalogue.hakai.org/dataset/ca-cioos_6c34ed6e-5a17-41f2-b83a-cd59d1ce07bd) | `&` | `summary`: …nserved Area (IPCA) in the Hoeya Head & Lull Bay regions, center…… |
| LiDAR Dataset - Calvert Island - 2012 & 2014 - British Columbia - Canada | [244b5915…](https://catalogue.hakai.org/dataset/ca-cioos_244b5915-0ccf-4fab-9720-d2ac9394a27b) | `&` | `title`: …LiDAR Dataset - Calvert Island - 2012 & 2014 - British Columbia …… |
| LiDAR Derived Watersheds with Metrics - Calvert Island | [d94882f8…](https://catalogue.hakai.org/dataset/ca-cioos_d94882f8-c069-454d-a0ea-96c2b17d789d) | `< >` | `summary`: …gton et al’s methods and tools (found <a href="http://www.werc.u…… |
| Moore Island Archaeology Survey - 2019 - Airborne Coastal Observatory | [c3958106…](https://catalogue.hakai.org/dataset/ca-cioos_c3958106-fc49-44bd-8227-bfc3e8bcb58c) | `&` | `summary`: …ata (TIFF) – 4 band orthophotos – RGB & NIR. Hyperspectral data …… |
| Mussel Dynamics - Length & Bed Depth - BC Central Coast | [d683512f…](https://catalogue.hakai.org/dataset/ca-cioos_d683512f-5e47-4b1d-baac-c653fb761806) | `&` | `title`: …Mussel Dynamics - Length & Bed Depth - BC Central Coast… |
| Mussel Dynamics - Point Intercepts - BC Central Coast | [cec3dcef…](https://catalogue.hakai.org/dataset/ca-cioos_cec3dcef-8dba-4d91-aee6-b60ce416497c) | `&` | `summary`: …ure and composition of the macroalgae & sessile invertebrate com…… |
| North Vancouver Island Survey - 2019 - Airborne Coastal Observatory | [95bee6a0…](https://catalogue.hakai.org/dataset/ca-cioos_95bee6a0-ae38-4427-b5b2-5cc5835df70d) | `&` | `summary`: …ata (TIFF) – 4 band orthophotos – RGB & NIR. Hyperspectral data …… |
| Owikeno Basin LiDAR Survey - 2019 - Airborne Coastal Observatory | [a60a0468…](https://catalogue.hakai.org/dataset/ca-cioos_a60a0468-3f56-4f22-abd4-5268fcfb9744) | `&` | `summary`: …ata (TIFF) – 4 band orthophotos – RGB & NIR. Hyperspectral data …… |
| Protistan plankton time series and spatial data from the Salish Sea and  | [6756b221…](https://catalogue.hakai.org/dataset/ca-cioos_6756b221-28a0-4848-9761-905cbd558cd7) | `& and < >` | `summary`: …ne solution (1% concentration) (Edler & Elbrächter 2010; Del Bel…… |
| Sea wrack wet to dry biomass calibrations for macroalgae of the Central  | [94cdfcba…](https://catalogue.hakai.org/dataset/ca-cioos_94cdfcba-bbd4-4053-8976-75de69460c14) | `< >` | `summary`: …at all species displayed a strong (R2 > 0.5) and predictable (p …… |
| Seagrass fish and macroinvertebrate swaths BC Central Coast | [b2b18171…](https://catalogue.hakai.org/dataset/ca-cioos_b2b18171-35b6-4345-b81b-497a90c2e7c5) | `&` | `summary`: …The Seagrass Fish & Macroinvertebrate dataset is a… |
| Seastar & Macroinvertebrate Dynamics - BC Central Coast | [3bc02dd8…](https://catalogue.hakai.org/dataset/ca-cioos_3bc02dd8-7654-44f0-8c7c-02739937bdf4) | `&` | `title`: …Seastar & Macroinvertebrate Dynamics - B… |
| Seastar & Macroinvertebrate Dynamics - BC Central Coast - 2016-2017 | [154e88e6…](https://catalogue.hakai.org/dataset/ca-cioos_154e88e6-2300-4ca0-b3f8-ee822d32a9a4) | `&` | `title`: …Seastar & Macroinvertebrate Dynamics - B… |
| Sentinel 3A and 3B Chlorophyll and Suspended Matter Concentrations for C | [91107fce…](https://catalogue.hakai.org/dataset/ca-cioos_91107fce-93a4-4bc9-bce4-e7d9e1cf02a0) | `< >` | `summary`: …shown to have low systematic biases (<1%) and follow expected se…… |
| Spatial extent of surface canopy kelp (Nereocystis luetkeana) derived fr | [b8483c9e…](https://catalogue.hakai.org/dataset/ca-cioos_b8483c9e-81e6-4e1a-b09f-2d66f8fee9a2) | `&` | `summary`: …Reshitnyk, L., Timmer, B., Guyn, A., & Baum, J. (2024). Spatial …… |
| Surfgrass Community Structure - Length & Density - BC Central Coast | [93a9bb9a…](https://catalogue.hakai.org/dataset/ca-cioos_93a9bb9a-b54e-4623-9e0e-93d8b7d0020b) | `&` | `title`: …urfgrass Community Structure - Length & Density - BC Central Coa…… |
| Time series of eelgrass (Zostera marina) meadow extent derived from dron | [5e4f925a…](https://catalogue.hakai.org/dataset/ca-cioos_5e4f925a-9cf2-4e33-ae22-75c5b326ce6c) | `< >` | `summary`: …ed annually during morning low tides (<0.5 m) and collect RGB (r…… |
| Time series of quarterly kelp canopy extent from Landsat 5, 7, 8, and 9  | [7cafde4f…](https://catalogue.hakai.org/dataset/ca-cioos_7cafde4f-bdd5-4b95-a41d-7939ddcf08c6) | `& and < >` | `summary`: …, T.W., Allen, J.G., Cavanaugh, K.C., & Siegel, D.A. (2020). Thr…… |
| Time series of surface kelp canopy area derived from remotely piloted ae | [291b98a4…](https://catalogue.hakai.org/dataset/ca-cioos_291b98a4-d868-462c-852a-d6cf79ecf6ce) | `< >` | `summary`: …ually in July/August during low tide (<1.5 m, chart datum) and c…… |
| Time-lapse Camera Imagery of Calvert Island Beaches (2012-Present) | [82a3f5ec…](https://catalogue.hakai.org/dataset/ca-cioos_82a3f5ec-95c5-4aeb-a0c0-bf168c985676) | `&` | `summary`: …by name, they are ‘HOTEL’, ‘YANKEE’, & ‘FOXTROT’. Originally con…… |
| Trails - Calvert Island - British Columbia - Canada | [ea4e84d5…](https://catalogue.hakai.org/dataset/ca-cioos_ea4e84d5-c89c-4611-9594-449e468bd76c) | `&` | `summary`: …onnecting. Examples: West Beach Trail & 4th Beach to 7th Beach (…… |
| World View 2 Imagery - Coverage of three regions of the BC Central Coast | [ab901b46…](https://catalogue.hakai.org/dataset/ca-cioos_ab901b46-43f6-4044-b0c3-b5fd825622f4) | `&` | `title`: …BC Central Coast - Summer 2014, 2015, & 2016… |

<details><summary>File stems, for running the conversion</summary>

- `8_day_average_satellite__senti_91107` — 91107fce-93a4-4bc9-bce4-e7d9e1cf02a0
- `ancient_forest_wetlands__bc____c3eff` — c3eff62f-bcee-4faa-a7e1-7b9380d94e74
- `bamfield_region_uav_imagery_an_40d86` — 40d86401-0e95-4ff3-b1c7-25e4e9138157
- `big_bar_slide___2020___airborn_82a54` — 82a543b1-686c-45c9-a03d-4f93e0ab8e8a
- `bowhead_whale_drone_data_colle_35900` — 35900174-c64a-493e-9a7e-390ac7e997e4
- `bute_inlet_geo_hazards___ramsa_52d4f` — 52d4f546-dfdf-4bf1-b1ad-f6ec6f2663c0
- `daily_satellite__sentinel_3a_a_d1bef` — d1bef0b7-4d15-4bc1-bf34-faca6352891f
- `data_record_does_not_exist_any_9fafb` — 9fafb4c8-e61f-4372-ac71-c1ddbe57d80c
- `denali_fault___2024___airborne_f762a` — f762a307-6dfb-41a8-a56c-ecacfb075a0a
- `fin_island___k_yel___2020___ai_d2e83` — d2e83e40-9e95-4a47-a899-b37c744be3ab
- `fountain_valley_lidar_data___2_bb59c` — bb59cb9e-887a-40a3-b41a-f4a5b2263ce6
- `fraser_river_landslide_project_f25b0` — f25b00ba-ad63-42b3-8021-3fb6aa99baff
- `fucus_dynamics___point_interce_d87de` — 52797e17-c0ed-46a4-9dcd-e34f801c6205
- `gem_dataset_trinidad_and_tobag_741bd` — 741bd412-6387-4dcd-8d61-7046b949f406
- `geoconnections_model_applicati_53730` — 53730b70-be6f-4e24-8b9d-4a5e2c491121
- `gitanyow_archaeology__cranberr_0f524` — 0f524f76-a88b-4e0a-9c3c-ee83114c3679
- `gitga_at_territory_coastal_map_b5f0f` — b5f0f854-efe1-4132-808d-074244d813e1
- `glacier_and_icefield_mapping___0ebfd` — 0ebfdd89-61d6-453c-870a-83167617b26a
- `google_earth_engine_kelp_tool__2a92c` — 2a92ca16-f5c6-4362-acea-6bb5117b8d65
- `hakai_institute_nutrients__dos_47620` — 476204a7-0714-4755-953d-61fa3c5df497
- `hakai_rpas__drone__operations__58290` — 582909b1-c87d-4c5a-8594-5f44726f43a4
- `high_resolution_record_of_8_m__77a25` — 77a256cd-baf7-434e-9f62-53ba809e48cb
- `imagery_and_elevation_models_f_06ddf` — 06ddfa63-2611-46a5-8d63-c1b576e85bcb
- `island_food_web_study___centra_5eda0` — 5eda02a9-36b6-4875-91c9-989e9e06c5ad
- `juvenile_pink_and_chum_salmon__89b3c` — 89b3c6d8-983b-48f4-a0b5-04eea65602f6
- `kelp_field_data_for_remote_sen_94b49` — 94b4992f-19e2-46d4-875e-f0c952ea62f7
- `kilbella_river_estuary_lidar_s_62de2` — 62de21ed-90fb-422a-9c55-29c513a00f95
- `killer_whale_foraging_drone_ob_1815b` — 1815be54-9081-4031-80fa-d3d071340a7d
- `knight_inlet_multibeam_bathyme_6c34e` — 6c34ed6e-5a17-41f2-b83a-cd59d1ce07bd
- `lidar_dataset___calvert_island_244b5` — 244b5915-0ccf-4fab-9720-d2ac9394a27b
- `lidar_derived_watersheds_with__d9488` — d94882f8-c069-454d-a0ea-96c2b17d789d
- `moore_island_archaeology_surve_c3958` — c3958106-fc49-44bd-8227-bfc3e8bcb58c
- `mussel_dynamics___length___bed_d6835` — d683512f-5e47-4b1d-baac-c653fb761806
- `mussel_dynamics___point_interc_cec3d` — cec3dcef-8dba-4d91-aee6-b60ce416497c
- `north_vancouver_island_survey__95bee` — 95bee6a0-ae38-4427-b5b2-5cc5835df70d
- `owikeno_basin_lidar_survey___2_a60a0` — a60a0468-3f56-4f22-abd4-5268fcfb9744
- `protistan_plankton_time_series_6756b` — 6756b221-28a0-4848-9761-905cbd558cd7
- `sea_wrack_wet_to_dry_biomass_c_94cdf` — 94cdfcba-bbd4-4053-8976-75de69460c14
- `seagrass_subtidal_fish_and_mac_b2b18` — b2b18171-35b6-4345-b81b-497a90c2e7c5
- `seastar___macroinvertebrate_dy_3bc02` — 3bc02dd8-7654-44f0-8c7c-02739937bdf4
- `seastar___macroinvertebrate_dy_d87de` — 154e88e6-2300-4ca0-b3f8-ee822d32a9a4
- `spatial_extent_of_surface_cano_b8483` — b8483c9e-81e6-4e1a-b09f-2d66f8fee9a2
- `surfgrass_community_structure__93a9b` — 93a9bb9a-b54e-4623-9e0e-93d8b7d0020b
- `time_lapse_camera_imagery_of_c_82a3f` — 82a3f5ec-95c5-4aeb-a0c0-bf168c985676
- `time_series_of_eelgrass__zoste_5e4f9` — 5e4f925a-9cf2-4e33-ae22-75c5b326ce6c
- `time_series_of_quarterly_kelp__7cafd` — 7cafde4f-bdd5-4b95-a41d-7939ddcf08c6
- `time_series_of_surface_kelp_ca_291b9` — 291b98a4-d868-462c-852a-d6cf79ecf6ce
- `trails___calvert_island___brit_ea4e8` — ea4e84d5-c89c-4611-9594-449e468bd76c
- `world_view_2_imagery___coverag_ab901` — ab901b46-43f6-4044-b0c3-b5fd825622f4

</details>
