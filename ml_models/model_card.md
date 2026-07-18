# Model Card — Band Gap Predictor (Random Forest)

## Model Details

| Property | Value |
|---|---|
| Algorithm | `RandomForestRegressor` |
| Estimators | 200 |
| Random State | 42 |
| Training Split | 80% train / 20% test |
| Test Samples | 4000 |

## Performance Metrics

| Metric | Value |
|---|---|
| **MAE** | 0.3576 eV |
| **RMSE** | 0.6516 eV |
| **R²** | 0.8648 |

## Top 20 Feature Importances

| Rank | Feature | Importance |
|---|---|---|
| 1 | `MagpieData mode MeltingT` | 0.4067 |
| 2 | `MagpieData mean NdValence` | 0.0663 |
| 3 | `MagpieData avg_dev NdValence` | 0.0590 |
| 4 | `MagpieData maximum MendeleevNumber` | 0.0365 |
| 5 | `MagpieData mean MeltingT` | 0.0258 |
| 6 | `MagpieData avg_dev Column` | 0.0159 |
| 7 | `MagpieData mean NpValence` | 0.0157 |
| 8 | `MagpieData maximum NfUnfilled` | 0.0152 |
| 9 | `MagpieData maximum MeltingT` | 0.0148 |
| 10 | `MagpieData range NfUnfilled` | 0.0145 |
| 11 | `MagpieData range MeltingT` | 0.0127 |
| 12 | `MagpieData mode Electronegativity` | 0.0127 |
| 13 | `MagpieData avg_dev Electronegativity` | 0.0112 |
| 14 | `MagpieData mean Electronegativity` | 0.0107 |
| 15 | `MagpieData mean Row` | 0.0097 |
| 16 | `MagpieData mean SpaceGroupNumber` | 0.0093 |
| 17 | `MagpieData avg_dev NValence` | 0.0093 |
| 18 | `MagpieData avg_dev NUnfilled` | 0.0090 |
| 19 | `MagpieData mean NUnfilled` | 0.0087 |
| 20 | `MagpieData range Electronegativity` | 0.0079 |

## Dataset

- **Source**: Materials Project (stable inorganic materials, `is_stable=True`)
- **Total samples**: ~5,000
- **Target variable**: Band gap (eV), DFT-computed
- **Features**: 132 Magpie composition descriptors via `matminer`

## Limitations

- Trained on DFT-computed band gaps, which systematically underestimate experimental values.
- Composition-only features — does not account for crystal structure or polymorphism.
- Limited to inorganic materials present in the Materials Project database.
