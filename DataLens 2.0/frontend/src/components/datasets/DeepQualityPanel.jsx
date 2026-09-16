import { useEffect, useMemo, useState } from "react";
import apiClient from "../../services/api/client.js";
import { AlertTriangle, BarChart3, CheckCircle2, Database, Rows3, Sparkles } from "lucide-react";

const fmt = (v) => v === null || v === undefined ? "—" : typeof v === "number" ? v.toLocaleString(undefined, { maximumFractionDigits: 4 }) : String(v);

function Metric({ label, value, hint, icon: Icon }) {
  return <div className="card">
    <div className="flex items-center justify-between"><span className="text-xs font-medium uppercase tracking-wider text-neutral-500">{label}</span>{Icon && <Icon className="h-4 w-4 text-neutral-400"/>}</div>
    <div className="mt-2 text-2xl font-semibold tracking-tight">{fmt(value)}</div>
    {hint && <div className="mt-1 text-xs text-neutral-400">{hint}</div>}
  </div>;
}

function Plot({ datasetId, type, column, title, description }) {
  const params = new URLSearchParams({ plot_type: type });
  if (column) params.set("column", column);
  const [failed, setFailed] = useState(false);
  useEffect(() => { setFailed(false); }, [datasetId, type, column]);
  return <div className="card overflow-hidden">
    <h3 className="font-semibold">{title}</h3><p className="mt-1 text-xs text-neutral-500">{description}</p>
    <div className="mt-4 flex min-h-[260px] items-center justify-center overflow-auto rounded-xl bg-neutral-50 p-2 dark:bg-neutral-950">
      {failed ? <div className="p-8 text-center text-sm text-red-600">This plot could not be rendered. The dataset profile is still available above.</div>
        : <img className="mx-auto max-h-[520px] max-w-full object-contain" src={`${import.meta.env.VITE_API_URL}/api/datasets/${datasetId}/plot?${params.toString()}`}alt={title} onError={() => setFailed(true)}/>}
    </div>
  </div>;
}

function QualityList({ title, items, tone = "warning" }) {
  if (!items?.length) return null;
  return <div className="card">
    <h3 className="font-semibold">{title} <span className="text-xs font-normal text-neutral-400">({items.length})</span></h3>
    <div className="mt-3 flex flex-wrap gap-2">{items.map((x, i) => <span key={i} className={`rounded-full px-3 py-1.5 text-xs ${tone === "high" ? "bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300" : "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300"}`}>{x}</span>)}</div>
  </div>;
}

function Correlation({ data }) {
  if (!data?.matrix?.length) return <div className="card text-sm text-neutral-500">Correlation needs at least two variable numeric columns.</div>;
  return <div className="card">
    <div className="flex items-center justify-between gap-3"><div><h3 className="font-semibold">Correlation matrix</h3><p className="mt-1 text-xs text-neutral-500">Pearson correlation across numeric and numeric-like columns.</p></div><BarChart3 className="h-5 w-5 text-neutral-400"/></div>
    <div className="mt-4 overflow-auto rounded-xl border"><table className="min-w-full text-xs"><thead><tr className="border-b bg-neutral-50 dark:bg-neutral-950"><th className="sticky left-0 bg-neutral-50 px-3 py-2 text-left dark:bg-neutral-950">Column</th>{data.columns.map(c=><th className="px-3 py-2 text-right" key={c}>{c}</th>)}</tr></thead><tbody>{data.matrix.map(r=><tr className="border-b last:border-0" key={r.row}><td className="sticky left-0 bg-white px-3 py-2 font-medium dark:bg-neutral-900">{r.row}</td>{r.values.map(v=><td key={v.column} className="px-3 py-2 text-right font-mono">{v.value == null ? "—" : Number(v.value).toFixed(3)}</td>)}</tr>)}</tbody></table></div>
    {data.strongest?.length > 0 && <div className="mt-4"><h4 className="text-xs font-semibold uppercase tracking-wider text-neutral-500">Strongest relationships</h4><div className="mt-2 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">{data.strongest.slice(0, 12).map(x=><div className="rounded-xl bg-neutral-50 p-3 dark:bg-neutral-950" key={`${x.column_a}-${x.column_b}`}><div className="text-xs font-medium">{x.column_a} ↔ {x.column_b}</div><div className="mt-1 font-mono text-sm">{x.correlation}</div></div>)}</div></div>}
  </div>;
}

export default function DeepQualityPanel({ profile, datasetId }) {
  const [problemRows, setProblemRows] = useState([]);
  const [showProblems, setShowProblems] = useState(false);
  const [problemLoading, setProblemLoading] = useState(false);
  const [plotColumn, setPlotColumn] = useState("");

  const numeric = useMemo(() => profile.column_profiles.filter(c => c.numeric_stats), [profile]);
  const categorical = useMemo(() => profile.column_profiles.filter(c => c.categorical_stats), [profile]);
  const selectedNumeric = numeric.find(c => c.name === plotColumn)?.name || numeric[0]?.name || "";

  useEffect(() => {
    if (!plotColumn && numeric[0]) setPlotColumn(numeric[0].name);
  }, [numeric, plotColumn]);

  const loadProblems = async () => {
    if (showProblems) { setShowProblems(false); return; }
    setProblemLoading(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/datasets/${datasetId}/problem-rows?limit=100`)
      const json = await response.json();
      setProblemRows(json.rows || []);
      setShowProblems(true);
    } finally { setProblemLoading(false); }
  };

  const o = profile.overview || {};
  const rq = profile.row_quality || {};
  const md = profile.missing_data || {};
  const q = profile.quality_flags || {};

  return <div className="space-y-6">
    <section>
      <div className="mb-3"><h2 className="section-title">Deep dataset audit</h2><p className="mt-1 text-xs text-neutral-500">Everything below is calculated from the uploaded file with pandas, NumPy and Matplotlib. No fixed dataset assumptions.</p></div>
      <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Metric label="Total cells" value={profile.total_cells} icon={Database}/>
        <Metric label="Memory used" value={`${(profile.memory_usage_bytes / 1024 / 1024).toFixed(2)} MB`} icon={Database}/>
        <Metric label="Data density" value={`${o.data_density ?? 0}%`} hint={`${md.missing_percentage ?? 0}% missing`} icon={CheckCircle2}/>
        <Metric label="Rows with missing" value={md.rows_with_missing} hint={`${md.rows_with_missing_percentage ?? 0}% of rows`} icon={Rows3}/>
        <Metric label="Empty rows" value={md.rows_all_missing} icon={Rows3}/>
        <Metric label="Duplicate rows" value={profile.duplicates.duplicate_rows} hint={`${profile.duplicates.duplicate_percentage}%`} icon={Rows3}/>
        <Metric label="Columns with missing" value={o.columns_with_missing} icon={Database}/>
        <Metric label="Problem signals" value={profile.cleaning_recommendations?.length || 0} icon={AlertTriangle}/>
      </div>
    </section>

    <section>
      <div className="mb-3"><h2 className="section-title">Detected data-quality signals</h2><p className="mt-1 text-xs text-neutral-500">Only signals actually found in this dataset are listed.</p></div>
      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
        <QualityList title="High missing" items={q.high_missing_columns} tone="high"/>
        <QualityList title="Completely empty" items={q.empty_columns} tone="high"/>
        <QualityList title="Constant columns" items={q.constant_columns} tone="high"/>
        <QualityList title="Near constant" items={q.near_constant_columns}/>
        <QualityList title="Placeholders" items={q.placeholder_columns}/>
        <QualityList title="Whitespace" items={q.whitespace_columns}/>
        <QualityList title="Mixed types" items={q.mixed_type_columns}/>
        <QualityList title="Numeric-like text" items={q.numeric_like_columns}/>
        <QualityList title="Possible index" items={q.possible_index_columns}/>
        <QualityList title="Possible IDs" items={q.possible_id_columns}/>
        <QualityList title="Outlier columns" items={q.outlier_columns}/>
        <QualityList title="Invalid dates" items={q.invalid_date_columns}/>
      </div>
    </section>

    <section className="card">
      <div className="mb-3"><h3 className="font-semibold">Missing-data detail</h3><p className="mt-1 text-xs text-neutral-500">Every column is listed, including columns with zero missing values.</p></div>
      <div className="overflow-auto rounded-xl border"><table className="min-w-full text-xs">
        <thead><tr className="border-b bg-neutral-50 dark:bg-neutral-950"><th className="px-3 py-2 text-left">Column</th><th className="px-3 py-2 text-right">Missing</th><th className="px-3 py-2 text-right">%</th><th className="px-3 py-2 text-left">Status</th></tr></thead>
        <tbody>{profile.column_profiles.map(c => <tr className="border-b last:border-0" key={c.name}><td className="px-3 py-2 font-medium">{c.name}</td><td className="px-3 py-2 text-right">{fmt(c.missing_count)}</td><td className="px-3 py-2 text-right">{fmt(c.missing_percentage)}%</td><td className="px-3 py-2">{c.missing_count === profile.rows ? <span className="text-red-600">100% empty</span> : c.missing_count ? <span className="text-amber-600">Missing values</span> : <span className="text-emerald-600">Complete</span>}</td></tr>)}</tbody>
      </table></div>
    </section>

    <section className="grid gap-4 lg:grid-cols-2">
      <Plot datasetId={datasetId} type="missing" title="Missing values by column" description="See every column with missing cells and how large the problem is."/>
      <Plot datasetId={datasetId} type="heatmap" title="Missingness heatmap" description="Row-by-column view of missing cells; large files are sampled for responsiveness."/>
    </section>

    {numeric.length > 0 && <section>
      <div className="mb-3 flex flex-wrap items-end justify-between gap-3"><div><h2 className="section-title">Numerical distributions</h2><p className="mt-1 text-xs text-neutral-500">Histogram + box plot for any numeric or numeric-like column.</p></div><select className="input min-w-[220px]" value={selectedNumeric} onChange={e=>setPlotColumn(e.target.value)}>{numeric.map(c=><option key={c.name}>{c.name}</option>)}</select></div>
      <div className="grid gap-4 lg:grid-cols-2"><Plot datasetId={datasetId} type="histogram" column={selectedNumeric} title={`Histogram — ${selectedNumeric}`} description="Frequency distribution calculated from finite numeric values."/><Plot datasetId={datasetId} type="boxplot" column={selectedNumeric} title={`Box plot — ${selectedNumeric}`} description="Median, quartiles and IQR-based outlier view."/></div>
    </section>}

    {categorical.length > 0 && <section>
      <div className="mb-3"><h2 className="section-title">Categorical distributions</h2><p className="mt-1 text-xs text-neutral-500">Top-value frequencies for each categorical/text field.</p></div>
      <div className="grid gap-4 lg:grid-cols-2">{categorical.slice(0, 8).map(c=><Plot key={c.name} datasetId={datasetId} type="category" column={c.name} title={`Top values — ${c.name}`} description={`${fmt(c.categorical_stats.unique)} unique values; showing the most frequent values.`}/>)}</div>
    </section>}

    <Correlation data={profile.correlation}/>

    <section>
      <div className="mb-3"><h2 className="section-title">Row-level investigation</h2><p className="mt-1 text-xs text-neutral-500">Inspect actual records affected by missing values, placeholders and numeric outliers.</p></div>
      <button className="btn btn-dark" onClick={loadProblems} disabled={problemLoading}>{problemLoading ? "Finding problem rows…" : showProblems ? "Hide problem rows" : "Find problem rows"}</button>
      {showProblems && <div className="mt-4 overflow-hidden rounded-2xl border"><div className="max-h-[560px] overflow-auto"><table className="min-w-[1000px] text-xs"><thead className="sticky top-0 bg-neutral-50 dark:bg-neutral-900"><tr><th className="px-3 py-3 text-left">Row</th><th className="px-3 py-3 text-left">Problems</th>{profile.column_profiles.map(c=><th className="px-3 py-3 text-left" key={c.name}>{c.name}</th>)}</tr></thead><tbody>{problemRows.map(r=><tr className="border-t align-top" key={r.row_number}><td className="px-3 py-2 font-mono">{r.row_number}</td><td className="max-w-[240px] px-3 py-2 text-red-700 dark:text-red-300">{r.issues.join(" · ")}</td>{profile.column_profiles.map(c=><td className="max-w-[180px] px-3 py-2" key={c.name}>{r.data[c.name] == null ? <span className="font-semibold text-red-600">NULL</span> : String(r.data[c.name])}</td>)}</tr>)}{!problemRows.length&&<tr><td colSpan={profile.columns + 2} className="px-4 py-10 text-center text-sm text-neutral-500">No problem rows were detected by the current rules.</td></tr>}</tbody></table></div></div>}
    </section>

    <section>
      <div className="mb-3"><h2 className="section-title">Cleaning recommendations</h2><p className="mt-1 text-xs text-neutral-500">Suggestions are generated from detected evidence; nothing is silently changed.</p></div>
      <div className="space-y-2">{profile.cleaning_recommendations?.length ? profile.cleaning_recommendations.map((r,i)=><div key={i} className="flex gap-3 rounded-xl border p-3"><Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600"/><div><div className="text-sm font-medium">{r.column || "Dataset"} <span className="ml-2 rounded-full bg-neutral-100 px-2 py-0.5 text-[10px] uppercase tracking-wide dark:bg-neutral-800">{r.severity}</span></div><p className="mt-1 text-xs text-neutral-500">{r.recommendation}</p></div></div>) : <div className="card text-sm text-neutral-500">No cleaning recommendations from the current rule set.</div>}</div>
    </section>
  </div>;
}
