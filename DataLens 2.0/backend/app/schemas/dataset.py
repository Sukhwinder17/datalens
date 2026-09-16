"""Pydantic schemas for universal DataLens dataset profiling."""
from __future__ import annotations
from pydantic import BaseModel, Field


class DatasetSummary(BaseModel):
    id: str
    filename: str
    format: str
    size: int
    status: str
    sheet_name: str | None = None


class UploadError(BaseModel):
    filename: str
    error: str


class UploadResponse(BaseModel):
    uploaded: list[DatasetSummary]
    errors: list[UploadError]


class ColumnTypeCounts(BaseModel):
    numerical: int = 0
    categorical: int = 0
    datetime: int = 0
    boolean: int = 0
    other: int = 0


class MissingDataSummary(BaseModel):
    total_missing: int = 0
    missing_percentage: float = 0.0
    rows_with_missing: int = 0
    rows_all_missing: int = 0
    per_column: dict[str, int] = Field(default_factory=dict)
    per_column_percentage: dict[str, float] = Field(default_factory=dict)
    top_missing_columns: list[dict] = Field(default_factory=list)


class DuplicatesSummary(BaseModel):
    duplicate_rows: int = 0
    duplicate_percentage: float = 0.0
    duplicate_groups: int = 0


class HistogramBin(BaseModel):
    label: str
    start: float
    end: float
    count: int


class NumericColumnStats(BaseModel):
    count: int = 0
    mean: float | None = None
    median: float | None = None
    mode: float | None = None
    std: float | None = None
    variance: float | None = None
    min: float | None = None
    max: float | None = None
    p01: float | None = None
    p05: float | None = None
    p10: float | None = None
    p25: float | None = None
    p50: float | None = None
    p75: float | None = None
    p90: float | None = None
    p95: float | None = None
    p99: float | None = None
    range: float | None = None
    iqr: float | None = None
    skewness: float | None = None
    kurtosis: float | None = None
    coefficient_variation: float | None = None
    zeros: int = 0
    negatives: int = 0
    positives: int = 0
    infinities: int = 0
    outlier_count: int = 0
    outlier_percentage: float = 0.0
    lower_fence: float | None = None
    upper_fence: float | None = None
    unique: int = 0
    histogram: list[HistogramBin] = Field(default_factory=list)


class CategoricalValue(BaseModel):
    value: str
    frequency: int
    percentage: float


class CategoricalColumnStats(BaseModel):
    unique: int = 0
    top_value: str | None = None
    top_value_frequency: int | None = None
    top_value_percentage: float | None = None
    top_values: list[CategoricalValue] = Field(default_factory=list)
    rare_values: list[CategoricalValue] = Field(default_factory=list)
    missing: int = 0
    empty_strings: int = 0
    whitespace_only: int = 0
    min_length: int | None = None
    max_length: int | None = None
    mean_length: float | None = None
    median_length: float | None = None


class DatetimeColumnStats(BaseModel):
    earliest: str | None = None
    latest: str | None = None
    date_range_days: float | None = None
    unique_dates: int = 0
    missing_dates: int = 0
    invalid_values: int = 0


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    pandas_dtype: str
    semantic_type: str = "unknown"
    row_count: int = 0
    non_null_count: int = 0
    missing_count: int = 0
    missing_percentage: float = 0.0
    unique_count: int = 0
    unique_percentage: float = 0.0
    duplicate_count: int = 0
    sample_values: list[str] = Field(default_factory=list)
    placeholder_values: dict[str, int] = Field(default_factory=dict)
    blank_count: int = 0
    whitespace_count: int = 0
    constant: bool = False
    near_constant: bool = False
    high_cardinality: bool = False
    possible_id: bool = False
    possible_index: bool = False
    numeric_like: bool = False
    numeric_parse_percentage: float = 0.0
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    numeric_stats: NumericColumnStats | None = None
    categorical_stats: CategoricalColumnStats | None = None
    datetime_stats: DatetimeColumnStats | None = None


class DataQualityFlags(BaseModel):
    high_missing_columns: list[str] = Field(default_factory=list)
    duplicate_rows_present: bool = False
    constant_columns: list[str] = Field(default_factory=list)
    near_constant_columns: list[str] = Field(default_factory=list)
    high_cardinality_columns: list[str] = Field(default_factory=list)
    mixed_type_columns: list[str] = Field(default_factory=list)
    empty_columns: list[str] = Field(default_factory=list)
    outlier_columns: list[str] = Field(default_factory=list)
    invalid_date_columns: list[str] = Field(default_factory=list)
    placeholder_columns: list[str] = Field(default_factory=list)
    numeric_like_columns: list[str] = Field(default_factory=list)
    possible_id_columns: list[str] = Field(default_factory=list)
    possible_index_columns: list[str] = Field(default_factory=list)
    whitespace_columns: list[str] = Field(default_factory=list)


class DatasetProfile(BaseModel):
    dataset_id: str
    filename: str
    format: str
    size: int
    sheet_name: str | None = None
    available_sheets: list[str] = Field(default_factory=list)
    rows: int
    columns: int
    memory_usage_bytes: int = 0
    total_cells: int = 0
    column_types: ColumnTypeCounts
    missing_data: MissingDataSummary
    duplicates: DuplicatesSummary
    column_profiles: list[ColumnProfile]
    quality_flags: DataQualityFlags
    overview: dict = Field(default_factory=dict)
    row_quality: dict = Field(default_factory=dict)
    correlation: dict = Field(default_factory=dict)
    cleaning_recommendations: list[dict] = Field(default_factory=list)


class DatasetPreview(BaseModel):
    dataset_id: str
    columns: list[str]
    rows: list[dict[str, str | None]]
    page: int
    page_size: int
    total_rows: int
    total_pages: int
