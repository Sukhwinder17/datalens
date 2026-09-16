from pathlib import Path
import pandas as pd

from app.models.dataset import DatasetRecord
from app.services.data_profiler import profile_dataset


def test_deep_profile_detects_missing_placeholder_and_numeric_text(tmp_path: Path):
    path = tmp_path / "sample.csv"
    pd.DataFrame({
        "id": [0, 1, 2, 3],
        "score": ["10", "-", "30", "40*"],
        "empty": [None, None, None, None],
        "name": [" A ", "B", "B", "C"],
    }).to_csv(path, index=False)

    record = DatasetRecord(
        id="sample",
        filename="sample.csv",
        format="csv",
        size=path.stat().st_size,
        status="uploaded",
        path=path,
    )
    profile = profile_dataset(record)

    assert profile.rows == 4
    assert profile.columns == 4
    assert "empty" in profile.quality_flags.empty_columns
    assert "score" in profile.quality_flags.placeholder_columns
    assert "score" in profile.quality_flags.numeric_like_columns
    score = next(c for c in profile.column_profiles if c.name == "score")
    assert score.numeric_stats is not None
    assert score.numeric_stats.max == 40.0
    assert score.placeholder_values["-"] == 1
