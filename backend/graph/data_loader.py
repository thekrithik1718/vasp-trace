"""Data loader and validation module for blockchain transaction records."""

import os
from typing import Set
import pandas as pd

REQUIRED_COLUMNS: Set[str] = {
    "transaction_hash",
    "sender",
    "receiver",
    "amount",
    "timestamp",
}


def load_transactions(file_path: str) -> pd.DataFrame:
    """Load transaction records from a CSV file into a pandas DataFrame.

    Args:
        file_path: Path to the CSV file containing transactions.

    Returns:
        pd.DataFrame containing the raw transaction records.

    Raises:
        FileNotFoundError: If the file does not exist at file_path.
        ValueError: If the file is empty or cannot be parsed as a CSV.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Transaction file not found: '{file_path}'")

    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        raise ValueError(f"Failed to read CSV from '{file_path}': {exc}") from exc

    return df


def validate_transactions(df: pd.DataFrame) -> bool:
    """Validate that a transaction DataFrame meets all schema and integrity rules.

    Checks performed:
    - Required columns exist ('transaction_hash', 'sender', 'receiver', 'amount', 'timestamp').
    - DataFrame is not empty.
    - 'transaction_hash' values are unique.
    - 'sender' and 'receiver' are not null/empty.
    - 'amount' is numeric and strictly greater than 0.
    - 'timestamp' values can be parsed as valid datetime values.

    Args:
        df: pandas DataFrame to validate.

    Returns:
        True if all validation checks pass.

    Raises:
        ValueError: If any validation check fails.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")

    # 1. Non-empty check
    if df.empty:
        raise ValueError("Transaction DataFrame is empty.")

    # 2. Required columns check
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"Missing required columns: {sorted(list(missing_cols))}. "
            f"Expected: {sorted(list(REQUIRED_COLUMNS))}"
        )

    # 3. Unique transaction_hash check
    if df["transaction_hash"].duplicated().any():
        duplicate_hashes = df.loc[
            df["transaction_hash"].duplicated(), "transaction_hash"
        ].tolist()
        raise ValueError(
            f"Duplicate transaction_hash values detected: {duplicate_hashes[:5]}"
        )

    # 4. Null / empty sender and receiver checks
    for col in ["sender", "receiver"]:
        if df[col].isna().any():
            raise ValueError(f"Column '{col}' contains null/NaN values.")
        str_series = df[col].astype(str).str.strip()
        if (str_series == "").any():
            raise ValueError(f"Column '{col}' contains empty or blank strings.")

    # 5. Amount check: numeric and greater than 0
    numeric_amounts = pd.to_numeric(df["amount"], errors="coerce")
    if numeric_amounts.isna().any():
        raise ValueError("Column 'amount' contains non-numeric values.")
    if (numeric_amounts <= 0).any():
        invalid_amounts = numeric_amounts[numeric_amounts <= 0].tolist()
        raise ValueError(
            f"Column 'amount' contains non-positive values (must be > 0): {invalid_amounts[:5]}"
        )

    # 6. Timestamp check: valid datetime values
    try:
        parsed_timestamps = pd.to_datetime(df["timestamp"], errors="coerce", format="ISO8601")
    except (ValueError, TypeError):
        parsed_timestamps = pd.to_datetime(df["timestamp"], errors="coerce")

    if parsed_timestamps.isna().any():
        # Fallback to mixed parsing for non-ISO timestamps
        try:
            parsed_timestamps = pd.to_datetime(df["timestamp"], errors="coerce", format="mixed")
        except (ValueError, TypeError):
            parsed_timestamps = pd.to_datetime(df["timestamp"], errors="coerce")

    if parsed_timestamps.isna().any():
        invalid_ts_indices = df.index[parsed_timestamps.isna()].tolist()
        raise ValueError(
            f"Column 'timestamp' contains invalid datetime values at rows: {invalid_ts_indices[:5]}"
        )

    return True


def load_and_validate_transactions(file_path: str) -> pd.DataFrame:
    """Convenience function to load and validate transactions from CSV.

    Args:
        file_path: Path to the CSV file.

    Returns:
        Validated pd.DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If loading fails or any validation check fails.
    """
    df = load_transactions(file_path)
    validate_transactions(df)
    return df
