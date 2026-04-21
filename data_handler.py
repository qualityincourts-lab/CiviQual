"""Data import and lightweight data management for CiviQual Stats."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd


class DataHandler:
    """Load tabular data and keep the active dataset in memory."""

    def __init__(self):
        self._df: Optional[pd.DataFrame] = None
        self._source: Optional[Path] = None

    # ------------------------------------------------------------------
    def load_file(self, path: str | Path) -> pd.DataFrame:
        path = Path(path)
        suffix = path.suffix.lower()
        if suffix in {".csv", ".txt"}:
            df = pd.read_csv(path)
        elif suffix in {".xlsx", ".xls", ".xlsm"}:
            df = pd.read_excel(path)
        elif suffix in {".tsv",}:
            df = pd.read_csv(path, sep="\t")
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        self._df = df
        self._source = path
        return df

    def set_dataframe(self, df: pd.DataFrame, source: Optional[Path] = None) -> None:
        self._df = df.copy()
        self._source = source

    def dataframe(self) -> Optional[pd.DataFrame]:
        return self._df

    def source(self) -> Optional[Path]:
        return self._source

    def numeric_columns(self) -> list[str]:
        if self._df is None:
            return []
        return self._df.select_dtypes(include="number").columns.tolist()

    def categorical_columns(self) -> list[str]:
        if self._df is None:
            return []
        return self._df.select_dtypes(exclude="number").columns.tolist()

    def has_data(self) -> bool:
        return self._df is not None and not self._df.empty

    def summary(self) -> pd.DataFrame:
        if self._df is None:
            return pd.DataFrame()
        return self._df.describe(include="all").transpose()
