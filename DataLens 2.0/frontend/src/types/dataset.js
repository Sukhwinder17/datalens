// JSDoc typedefs describing dataset API shapes. Mirrors
// backend/app/schemas/dataset.py — keep them in sync.
// TODO: migrate to TypeScript, or extend with DatasetProfile /
// CleaningOperation / AnalysisResult once those backend schemas exist.

/**
 * @typedef {Object} DatasetSummary
 * @property {string} id
 * @property {string} filename
 * @property {"csv"|"xlsx"} format
 * @property {number} size - bytes
 * @property {"uploaded"} status
 */

/**
 * @typedef {Object} UploadError
 * @property {string} filename
 * @property {string} error
 */

/**
 * @typedef {Object} UploadResponse
 * @property {DatasetSummary[]} uploaded
 * @property {UploadError[]} errors
 */

// ---------------------------------------------------------------------------
// Phase 2 — dataset profiling. Mirrors the Phase 2 additions to
// backend/app/schemas/dataset.py.
// ---------------------------------------------------------------------------

/**
 * @typedef {Object} ColumnTypeCounts
 * @property {number} numerical
 * @property {number} categorical
 * @property {number} datetime
 * @property {number} boolean
 * @property {number} other
 */

/**
 * @typedef {Object} MissingDataSummary
 * @property {number} total_missing
 * @property {number} missing_percentage
 * @property {Object<string, number>} per_column
 * @property {Object<string, number>} per_column_percentage
 */

/**
 * @typedef {Object} DuplicatesSummary
 * @property {number} duplicate_rows
 * @property {number} duplicate_percentage
 */

/**
 * @typedef {Object} NumericColumnStats
 * @property {number} count
 * @property {number|null} mean
 * @property {number|null} median
 * @property {number|null} std
 * @property {number|null} min
 * @property {number|null} max
 * @property {number|null} p25
 * @property {number|null} p50
 * @property {number|null} p75
 * @property {number} unique
 */

/**
 * @typedef {Object} CategoricalColumnStats
 * @property {number} unique
 * @property {string|null} top_value
 * @property {number|null} top_value_frequency
 * @property {number} missing
 */

/**
 * @typedef {Object} ColumnProfile
 * @property {string} name
 * @property {"numerical"|"categorical"|"datetime"|"boolean"|"other"} dtype
 * @property {string} pandas_dtype
 * @property {number} missing_count
 * @property {number} missing_percentage
 * @property {NumericColumnStats|null} numeric_stats
 * @property {CategoricalColumnStats|null} categorical_stats
 */

/**
 * @typedef {Object} DataQualityFlags
 * @property {string[]} high_missing_columns
 * @property {boolean} duplicate_rows_present
 * @property {string[]} constant_columns
 * @property {string[]} high_cardinality_columns
 * @property {string[]} mixed_type_columns
 */

/**
 * @typedef {Object} DatasetProfile
 * @property {string} dataset_id
 * @property {string} filename
 * @property {string} format
 * @property {number} size
 * @property {number} rows
 * @property {number} columns
 * @property {ColumnTypeCounts} column_types
 * @property {MissingDataSummary} missing_data
 * @property {DuplicatesSummary} duplicates
 * @property {ColumnProfile[]} column_profiles
 * @property {DataQualityFlags} quality_flags
 */

export {};
