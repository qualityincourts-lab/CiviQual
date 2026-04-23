#!/usr/bin/env python3
"""
CiviQual Stats Data Handler

Handles loading and processing of data files.

Copyright (c) 2026 A Step in the Right Direction LLC
All Rights Reserved.
"""

import pandas as pd
import numpy as np
from pathlib import Path


class DataHandler:
    """Data handling for CiviQual Stats."""
    
    def __init__(self):
        """Initialize the data handler."""
        self.supported_extensions = {'.csv', '.xlsx', '.xls'}
    
    def load_file(self, file_path):
        """
        Load data from a file.
        
        Args:
            file_path: Path to data file (CSV or Excel)
            
        Returns:
            pandas DataFrame
            
        Raises:
            ValueError: If file type is not supported
            FileNotFoundError: If file does not exist
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        ext = path.suffix.lower()
        
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {ext}. "
                           f"Supported types: {', '.join(self.supported_extensions)}")
        
        if ext == '.csv':
            return self._load_csv(path)
        else:
            return self._load_excel(path)
    
    def _load_csv(self, path):
        """Load CSV file with automatic encoding detection."""
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(path, encoding=encoding)
                return self._clean_dataframe(df)
            except UnicodeDecodeError:
                continue
            except Exception as e:
                raise ValueError(f"Error reading CSV: {str(e)}")
        
        raise ValueError("Could not decode file with any standard encoding")
    
    def _load_excel(self, path):
        """Load Excel file."""
        try:
            # Try to read first sheet
            df = pd.read_excel(path, sheet_name=0)
            return self._clean_dataframe(df)
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
    
    def _clean_dataframe(self, df):
        """Clean and prepare dataframe for analysis."""
        # Remove completely empty rows and columns
        df = df.dropna(how='all')
        df = df.dropna(axis=1, how='all')
        
        # Strip whitespace from string columns
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('nan', np.nan)
        
        # Convert date-like columns
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col])
                except (ValueError, TypeError):
                    pass
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def get_numeric_columns(self, df):
        """
        Get list of numeric columns from dataframe.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            list: Column names with numeric data
        """
        return df.select_dtypes(include=[np.number]).columns.tolist()
    
    def get_categorical_columns(self, df):
        """
        Get list of categorical columns from dataframe.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            list: Column names with categorical/object data
        """
        return df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def get_datetime_columns(self, df):
        """
        Get list of datetime columns from dataframe.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            list: Column names with datetime data
        """
        return df.select_dtypes(include=['datetime64']).columns.tolist()
    
    def split_by_column(self, df, split_column, output_dir):
        """
        Split dataframe by values in a column and save to separate files.
        
        Args:
            df: pandas DataFrame
            split_column: Column to split by
            output_dir: Directory to save output files
            
        Returns:
            list: Paths to created files
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        created_files = []
        
        for value in df[split_column].unique():
            if pd.isna(value):
                subset = df[df[split_column].isna()]
                filename = f"{split_column}_NA.csv"
            else:
                subset = df[df[split_column] == value]
                # Clean filename
                clean_value = str(value).replace('/', '_').replace('\\', '_')
                filename = f"{split_column}_{clean_value}.csv"
            
            file_path = output_path / filename
            subset.to_csv(file_path, index=False)
            created_files.append(str(file_path))
        
        return created_files
    
    def random_sample(self, df, n=None, fraction=None, seed=None):
        """
        Take a random sample from dataframe.
        
        Args:
            df: pandas DataFrame
            n: Number of rows to sample
            fraction: Fraction of rows to sample (0-1)
            seed: Random seed for reproducibility
            
        Returns:
            pandas DataFrame: Sampled data
        """
        if n is not None:
            return df.sample(n=min(n, len(df)), random_state=seed)
        elif fraction is not None:
            return df.sample(frac=fraction, random_state=seed)
        else:
            return df
    
    def stratified_sample(self, df, strata_column, n_per_stratum=None, fraction=None, seed=None):
        """
        Take a stratified random sample from dataframe.
        
        Args:
            df: pandas DataFrame
            strata_column: Column to stratify by
            n_per_stratum: Number of rows per stratum
            fraction: Fraction of rows per stratum
            seed: Random seed
            
        Returns:
            pandas DataFrame: Stratified sample
        """
        if seed is not None:
            np.random.seed(seed)
        
        samples = []
        
        for stratum in df[strata_column].unique():
            stratum_df = df[df[strata_column] == stratum]
            
            if n_per_stratum is not None:
                sample = stratum_df.sample(n=min(n_per_stratum, len(stratum_df)), random_state=seed)
            elif fraction is not None:
                sample = stratum_df.sample(frac=fraction, random_state=seed)
            else:
                sample = stratum_df
            
            samples.append(sample)
        
        return pd.concat(samples, ignore_index=True)
    
    def merge_files(self, file_paths, output_path):
        """
        Merge multiple data files into one.
        
        Args:
            file_paths: List of file paths to merge
            output_path: Path for merged output file
            
        Returns:
            pandas DataFrame: Merged data
        """
        dfs = []
        
        for path in file_paths:
            df = self.load_file(path)
            df['_source_file'] = Path(path).name
            dfs.append(df)
        
        merged = pd.concat(dfs, ignore_index=True)
        
        # Save merged file
        output = Path(output_path)
        if output.suffix.lower() == '.csv':
            merged.to_csv(output, index=False)
        else:
            merged.to_excel(output, index=False)
        
        return merged
    
    def validate_data(self, df, column):
        """
        Validate data in a column for analysis.
        
        Args:
            df: pandas DataFrame
            column: Column name to validate
            
        Returns:
            dict: Validation results
        """
        data = df[column]
        
        results = {
            'total_rows': len(data),
            'missing_count': data.isna().sum(),
            'missing_percent': (data.isna().sum() / len(data)) * 100,
            'valid_count': data.notna().sum(),
            'is_numeric': pd.api.types.is_numeric_dtype(data),
            'unique_values': data.nunique(),
            'duplicates': data.duplicated().sum()
        }
        
        if results['is_numeric']:
            valid_data = data.dropna()
            results['min'] = valid_data.min()
            results['max'] = valid_data.max()
            results['has_negative'] = (valid_data < 0).any()
            results['has_zero'] = (valid_data == 0).any()
        
        return results
