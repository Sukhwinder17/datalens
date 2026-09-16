import { BarChart3, CalendarDays, CheckCircle2, Database, FileWarning, Hash, Rows3, Tags, Type } from "lucide-react";

const fmt = (v) => Number(v || 0).toLocaleString();
export default function DatasetProfileSummary({ profile }) {
  const cards = [
    ["Rows", fmt(profile.rows), Rows3],
    ["Columns", fmt(profile.columns), Database],
    ["Total cells", fmt(profile.total_cells), Database],
    ["Missing cells", `${fmt(profile.missing_data.total_missing)} · ${profile.missing_data.missing_percentage}%`, FileWarning],
    ["Duplicate rows", `${fmt(profile.duplicates.duplicate_rows)} · ${profile.duplicates.duplicate_percentage}%`, Hash],
    ["Rows with missing", `${fmt(profile.missing_data.rows_with_missing)} · ${profile.row_quality?.rows_with_missing_percentage ?? 0}%`, Rows3],
    ["Memory", `${((profile.memory_usage_bytes || 0) / 1024 / 1024).toFixed(2)} MB`, Database],
    ["Quality signals", fmt(profile.cleaning_recommendations?.length), FileWarning],
  ];
  const types = [
    ["Numerical", profile.column_types.numerical, BarChart3],
    ["Categorical / text", profile.column_types.categorical, Tags],
    ["Datetime", profile.column_types.datetime, CalendarDays],
    ["Boolean", profile.column_types.boolean, CheckCircle2],
    ["Other", profile.column_types.other, Type],
  ];
  return <div className="space-y-4">
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4">{cards.map(([label, value, Icon]) => <div key={label} className="rounded-2xl border border-neutral-200 bg-white p-4 shadow-sm dark:border-neutral-800 dark:bg-neutral-900"><div className="flex items-center justify-between"><span className="text-xs font-medium uppercase tracking-wider text-neutral-500">{label}</span><Icon className="h-4 w-4 text-neutral-400"/></div><div className="mt-2 text-xl font-semibold tracking-tight">{value}</div></div>)}</div>
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">{types.map(([label, value, Icon]) => <div key={label} className="rounded-2xl border border-neutral-200 bg-neutral-50/80 p-4 dark:border-neutral-800 dark:bg-neutral-900/60"><div className="flex items-center gap-2 text-xs text-neutral-500"><Icon className="h-3.5 w-3.5"/>{label}</div><div className="mt-1 text-lg font-semibold">{fmt(value)}</div></div>)}</div>
  </div>;
}
