# Model Card — Band Gap Predictor (Random Forest)

## Model Details

| Property | Value |
|---|---|
| Algorithm | `RandomForestRegressor` |
| Estimators | 200 |
| Random State | 42 |
| Training Split | 80% train / 20% test |
| Test Samples | 1000 |

## Performance Metrics

| Metric | Value |
|---|---|
| **MAE** | 0.3987 eV |
| **RMSE** | 0.6921 eV |
| **R²** | 0.8350 |

## Top 20 Feature Importances

| Rank | Feature | Importance |
|---|---|---|
| 1 | `MagpieData mean Electronegativity` | 0.2808 |
| 2 | `MagpieData mean NdValence` | 0.0907 |
| 3 | `MagpieData mean Row` | 0.0622 |
| 4 | `MagpieData maximum NdValence` | 0.0609 |
| 5 | `MagpieData mean CovalentRadius` | 0.0430 |
| 6 | `MagpieData mean NpValence` | 0.0282 |
| 7 | `MagpieData avg_dev Electronegativity` | 0.0194 |
| 8 | `MagpieData mean GSbandgap` | 0.0179 |
| 9 | `MagpieData avg_dev NdValence` | 0.0160 |
| 10 | `MagpieData mode GSbandgap` | 0.0160 |
| 11 | `MagpieData minimum NValence` | 0.0158 |
| 12 | `MagpieData avg_dev Column` | 0.0155 |
| 13 | `MagpieData avg_dev NUnfilled` | 0.0130 |
| 14 | `MagpieData avg_dev SpaceGroupNumber` | 0.0117 |
| 15 | `MagpieData avg_dev NpValence` | 0.0116 |
| 16 | `MagpieData mode MeltingT` | 0.0109 |
| 17 | `MagpieData mean NUnfilled` | 0.0103 |
| 18 | `MagpieData mean MeltingT` | 0.0102 |
| 19 | `MagpieData mean NdUnfilled` | 0.0101 |
| 20 | `MagpieData avg_dev NValence` | 0.0100 |

## Dataset

- **Source**: Materials Project (stable inorganic materials, `is_stable=True`)
- **Total samples**: ~5,000
- **Target variable**: Band gap (eV), DFT-computed
- **Features**: 132 Magpie composition descriptors via `matminer`

## Limitations

- Trained on DFT-computed band gaps, which systematically underestimate experimental values.
- Composition-only features — does not account for crystal structure or polymorphism.
- Limited to inorganic materials present in the Materials Project database.
