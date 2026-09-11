"""Unit tests for the data_loader module."""

import os
import pandas as pd
import pytest

from backend.graph.data_loader import (
    REQUIRED_COLUMNS,
    load_transactions,
    validate_transactions,
    load_and_validate_transactions,
)

# Determine path to sample_data.csv relative to this test file
SAMPLE_DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "sample_data.csv")
)


@pytest.fixture
def valid_dataframe() -> pd.DataFrame:
    """Fixture providing a minimal valid transactions DataFrame."""
    return pd.DataFrame(
        {
            "transaction_hash": ["0xaaa", "0xbbb"],
            "sender": ["wallet_1", "wallet_2"],
            "receiver": ["wallet_2", "wallet_3"],
            "amount": [10.5, 20.0],
            "timestamp": ["2026-03-01T10:00:00Z", "2026-03-01T11:00:00Z"],
        }
    )


def test_load_sample_data_file_exists():
    """Test that sample_data.csv exists and can be loaded successfully."""
    assert os.path.exists(SAMPLE_DATA_PATH), f"File not found: {SAMPLE_DATA_PATH}"
    df = load_transactions(SAMPLE_DATA_PATH)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) >= 25


def test_load_nonexistent_file_raises():
    """Test that attempting to load a non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_transactions("non_existent_path_to_file_12345.csv")


def test_validate_valid_dataframe(valid_dataframe):
    """Test that a well-formed DataFrame passes validation."""
    assert validate_transactions(valid_dataframe) is True


def test_validate_sample_data_success():
    """Test that the project's sample_data.csv passes all validation checks."""
    df = load_and_validate_transactions(SAMPLE_DATA_PATH)
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 25
    assert set(REQUIRED_COLUMNS).issubset(set(df.columns))


def test_validate_empty_dataframe():
    """Test that an empty DataFrame fails validation."""
    empty_df = pd.DataFrame(columns=list(REQUIRED_COLUMNS))
    with pytest.raises(ValueError, match="empty"):
        validate_transactions(empty_df)


def test_validate_missing_required_columns(valid_dataframe):
    """Test that omitting any required column raises ValueError."""
    for col in REQUIRED_COLUMNS:
        incomplete_df = valid_dataframe.drop(columns=[col])
        with pytest.raises(ValueError, match="Missing required columns"):
            validate_transactions(incomplete_df)


def test_validate_duplicate_transaction_hash(valid_dataframe):
    """Test that duplicate transaction hashes trigger a ValueError."""
    dup_df = valid_dataframe.copy()
    dup_df.loc[1, "transaction_hash"] = dup_df.loc[0, "transaction_hash"]
    with pytest.raises(ValueError, match="Duplicate transaction_hash"):
        validate_transactions(dup_df)


def test_validate_negative_amount(valid_dataframe):
    """Test that negative amounts trigger a ValueError."""
    invalid_df = valid_dataframe.copy()
    invalid_df.loc[0, "amount"] = -5.0
    with pytest.raises(ValueError, match="non-positive"):
        validate_transactions(invalid_df)


def test_validate_zero_amount(valid_dataframe):
    """Test that zero amounts trigger a ValueError."""
    invalid_df = valid_dataframe.copy()
    invalid_df.loc[0, "amount"] = 0.0
    with pytest.raises(ValueError, match="non-positive"):
        validate_transactions(invalid_df)


def test_validate_non_numeric_amount(valid_dataframe):
    """Test that non-numeric amounts trigger a ValueError."""
    invalid_df = valid_dataframe.copy()
    invalid_df["amount"] = invalid_df["amount"].astype(object)
    invalid_df.loc[0, "amount"] = "not_a_number"
    with pytest.raises(ValueError, match="non-numeric"):
        validate_transactions(invalid_df)


def test_validate_invalid_timestamp(valid_dataframe):
    """Test that invalid timestamps trigger a ValueError."""
    invalid_df = valid_dataframe.copy()
    invalid_df.loc[0, "timestamp"] = "not_a_valid_timestamp"
    with pytest.raises(ValueError, match="invalid datetime"):
        validate_transactions(invalid_df)


def test_validate_empty_sender_or_receiver(valid_dataframe):
    """Test that null or blank sender/receiver triggers a ValueError."""
    for col in ["sender", "receiver"]:
        # Test None / NaN
        nan_df = valid_dataframe.copy()
        nan_df.loc[0, col] = None
        with pytest.raises(ValueError, match=f"Column '{col}' contains null"):
            validate_transactions(nan_df)

        # Test empty string / whitespace
        blank_df = valid_dataframe.copy()
        blank_df.loc[0, col] = "   "
        with pytest.raises(ValueError, match=f"Column '{col}' contains empty or blank strings"):
            validate_transactions(blank_df)
