"""Train a product-level sales quantity prediction model.

This script evaluates 3 different models (Random Forest, Gradient Boosting, Extra Trees) and saves the best one to predict `qty` for a given product and date.
It saves a persisted model file that includes the fitted model and the label encoding mapping
for categorical features based on the new dataset structure.

Usage:
    python train_product_model.py
    python train_product_model.py --dataset ../dataset/clean_data_bismar_penjualan.csv --output model_product_sales.pkl
"""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    ExtraTreesRegressor,
)
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

MODEL_FILENAME = "model_product_sales.pkl"
DEFAULT_DATASET = Path(__file__).resolve().parents[1] / "dataset" / "master_sales.csv"


def preprocess_sales_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Tanggal"] = pd.to_datetime(df["Tanggal"])
    df["day"] = df["Tanggal"].dt.day
    df["month"] = df["Tanggal"].dt.month
    df["year"] = df["Tanggal"].dt.year

    # Ensure categories are encoded
    df["Nama_Barang"] = df["Nama_Barang"].astype("category")
    df["Kategori"] = df["Kategori"].astype("category")
    df["DayType"] = df["DayType"].astype("category")

    df["Nama_Barang_code"] = df["Nama_Barang"].cat.codes
    df["Kategori_code"] = df["Kategori"].cat.codes
    df["DayType_code"] = df["DayType"].cat.codes

    return df


def train_and_save_model(dataset_path: Path, output_path: Path):
    df = pd.read_csv(dataset_path)
    df = preprocess_sales_data(df)

    # Updated features based on new dataset
    feature_cols = ["day", "month", "year", "DayOfWeek", "Nama_Barang_code", "Kategori_code", "DayType_code"]
    target_col = "Kuantitas"

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, shuffle=True
    )

    # 1. Definisikan 3 model yang berbeda
    models = {
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
        "Extra Trees": ExtraTreesRegressor(n_estimators=100, random_state=42),
    }

    best_model = None
    best_r2 = -float("inf")
    best_name = ""

    print(f"Training on {len(X_train)} samples, testing on {len(X_test)} samples...\n")

    # 2. Latih dan evaluasi masing-masing model
    for name, m in models.items():
        m.fit(X_train, y_train)
        
        # Evaluasi Data Training
        y_train_pred = m.predict(X_train)
        train_r2 = r2_score(y_train, y_train_pred)
        
        # Evaluasi Data Testing
        y_test_pred = m.predict(X_test)
        test_r2 = r2_score(y_test, y_test_pred)
        
        print(f"[{name}]")
        print(f"  -> Training Accuracy: {train_r2 * 100:.2f}%")
        print(f"  -> Testing Accuracy : {test_r2 * 100:.2f}%\n")

        # Pilih model dengan skor R2 testing terbaik
        if test_r2 > best_r2:
            best_r2 = test_r2
            best_model = m
            best_name = name

    # Save model and encoding mappings
    mapping_nama = dict(enumerate(df["Nama_Barang"].cat.categories))
    mapping_kategori = dict(enumerate(df["Kategori"].cat.categories))
    mapping_daytype = dict(enumerate(df["DayType"].cat.categories))
    
    product_to_kategori = df.drop_duplicates("Nama_Barang").set_index("Nama_Barang")["Kategori"].to_dict()

    saved = {
        "model": best_model,
        "nama_barang_mapping": mapping_nama,
        "kategori_mapping": mapping_kategori,
        "daytype_mapping": mapping_daytype,
        "product_to_kategori": product_to_kategori,
        "model_name": best_name,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(saved, output_path)

    print(f"\nBest model selected: {best_name} (Accuracy: {best_r2 * 100:.2f}%)")
    print(f"Saved best model to {output_path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Train product quantity prediction model")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
        help="Path to sales dataset CSV",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / MODEL_FILENAME,
        help="Output path for saved model",
    )

    args = parser.parse_args(argv)

    if not args.dataset.exists():
        raise SystemExit(f"Dataset not found: {args.dataset}")

    train_and_save_model(args.dataset, args.output)


if __name__ == "__main__":
    main()
