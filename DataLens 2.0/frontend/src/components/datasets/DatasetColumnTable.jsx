import { useState } from "react";
import { AlertTriangle, ChevronDown, ChevronUp, Search, Sparkles } from "lucide-react";

const TYPE_STYLES = {
  numerical: "bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300",
  categorical: "bg-purple-50 text-purple-700 dark:bg-purple-950/40 dark:text-purple-300",
  datetime: "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
  boolean: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
  other: "bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300",
};

const fmt = (v) => {
  if (v === null || v === undefined || v === "") return "—";
  if (typeof v === "number") return Number.isInteger(v) ? v.toLocaleString() : v.toLocaleString(undefined, { maximumFractionDigits: 6 });
  return String(v);
};

function Stat({ l, v }) {
  return <div className="rounded-xl border border-neutral-100 bg-neutral-50 p-3 dark:border-neutral-800 dark:bg-neutral-950/60">
    <div className="text-[10px] font-medium uppercase tracking-wider text-neutral-400">{l}</div>
    <div className="mt-1 break-words text-sm font-semibold">{fmt(v)}</div>
  </div>;
}

function Badge({ children, tone = "neutral" }) {
  const styles = {
    neutral: "bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300",
    warning: "bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300",
    high: "bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300",
    success: "bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300",
  };
  return <span className={`rounded-full px-2 py-1 text-[11px] font-medium ${styles[tone]}`}>{children}</span>;
}

function NumericDetails({ c }) {
  const s = c.numeric_stats;
  if (!s) return null;
  return <div className="space-y-4">
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-6">
      <Stat l="Count" v={s.count}/><Stat l="Mean" v={s.mean}/><Stat l="Median" v={s.median}/><Stat l="Mode" v={s.mode}/>
      <Stat l="Min" v={s.min}/><Stat l="Max" v={s.max}/><Stat l="Range" v={s.range}/><Stat l="Std dev" v={s.std}/>
      <Stat l="Variance" v={s.variance}/><Stat l="Q1 / P25" v={s.p25}/><Stat l="Q2 / P50" v={s.p50}/><Stat l="Q3 / P75" v={s.p75}/>
      <Stat l="P01" v={s.p01}/><Stat l="P05" v={s.p05}/><Stat l="P10" v={s.p10}/><Stat l="P90" v={s.p90}/>
      <Stat l="P95" v={s.p95}/><Stat l="P99" v={s.p99}/><Stat l="IQR" v={s.iqr}/><Stat l="CV" v={s.coefficient_variation}/>
      <Stat l="Skewness" v={s.skewness}/><Stat l="Kurtosis" v={s.kurtosis}/><Stat l="Zeros" v={s.zeros}/><Stat l="Negative" v={s.negatives}/>
      <Stat l="Positive" v={s.positives}/><Stat l="Infinity" v={s.infinities}/><Stat l="Outliers" v={`${fmt(s.outlier_count)} · ${fmt(s.outlier_percentage)}%`}/>
      <Stat l="Lower fence" v={s.lower_fence}/><Stat l="Upper fence" v={s.upper_fence}/><Stat l="Unique" v={s.unique}/>
    </div>
    <div className="rounded-xl border p-3">
      <div className="mb-2 text-xs font-semibold">Distribution bins</div>
      <div className="grid gap-1 sm:grid-cols-2 lg:grid-cols-4">
        {s.histogram?.map((b, i) => <div key={i} className="flex items-center justify-between rounded-lg bg-neutral-50 px-3 py-2 text-xs dark:bg-neutral-950"><span className="truncate">{b.label}</span><b>{b.count.toLocaleString()}</b></div>)}
      </div>
    </div>
  </div>;
}

function CategoricalDetails({ c }) {
  const s = c.categorical_stats;
  if (!s) return null;
  return <div className="space-y-4">
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-6">
      <Stat l="Unique" v={s.unique}/><Stat l="Missing" v={s.missing}/><Stat l="Top frequency" v={s.top_value_frequency}/>
      <Stat l="Top %" v={s.top_value_percentage}/><Stat l="Min length" v={s.min_length}/><Stat l="Max length" v={s.max_length}/>
      <Stat l="Mean length" v={s.mean_length}/><Stat l="Median length" v={s.median_length}/>
      <Stat l="Empty strings" v={s.empty_strings}/><Stat l="Whitespace only" v={s.whitespace_only}/>
    </div>
    <div>
      <div className="mb-2 text-xs font-semibold">Top 20 values</div>
      <div className="space-y-1.5">{s.top_values?.map((v) => <div key={v.value} className="flex items-center gap-2 text-xs">
        <span className="w-36 truncate" title={v.value}>{v.value}</span>
        <div className="h-2 flex-1 overflow-hidden rounded-full bg-neutral-100 dark:bg-neutral-800"><div className="h-2 rounded-full bg-neutral-700" style={{ width: `${Math.min(v.percentage, 100)}%` }}/></div>
        <span className="w-24 text-right text-neutral-500">{v.frequency.toLocaleString()} · {v.percentage}%</span>
      </div>)}</div>
    </div>
    {s.rare_values?.length > 0 && <div><div className="mb-2 text-xs font-semibold">Rare values (≤ 1% each)</div><div className="flex flex-wrap gap-1">{s.rare_values.map(v=><Badge key={v.value}>{v.value} · {v.frequency}</Badge>)}</div></div>}
  </div>;
}

function Details({ c }) {
  return <div className="space-y-4">
    <div className="flex flex-wrap gap-2">
      {c.constant && <Badge tone="high">Constant / empty</Badge>}
      {c.near_constant && <Badge tone="warning">Near constant</Badge>}
      {c.high_cardinality && <Badge tone="warning">High cardinality</Badge>}
      {c.possible_id && <Badge tone="warning">Possible ID</Badge>}
      {c.possible_index && <Badge tone="warning">Possible index</Badge>}
      {c.numeric_like && <Badge tone="success">Numeric-like text · {c.numeric_parse_percentage}% parsed</Badge>}
      {c.placeholder_values && Object.keys(c.placeholder_values).length > 0 && <Badge tone="warning">Placeholders found</Badge>}
    </div>

    <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-6">
      <Stat l="Rows" v={c.row_count}/><Stat l="Non-null" v={c.non_null_count}/><Stat l="Missing" v={`${fmt(c.missing_count)} · ${c.missing_percentage}%`}/>
      <Stat l="Unique" v={`${fmt(c.unique_count)} · ${c.unique_percentage}%`}/><Stat l="Duplicate values" v={c.duplicate_count}/>
      <Stat l="Blank / whitespace" v={`${c.blank_count} / ${c.whitespace_count}`}/>
      <Stat l="Storage dtype" v={c.pandas_dtype}/><Stat l="Semantic type" v={c.semantic_type}/>
    </div>

    {Object.keys(c.placeholder_values || {}).length > 0 && <div className="rounded-xl border border-amber-200 bg-amber-50/70 p-3 dark:border-amber-900/50 dark:bg-amber-950/20">
      <div className="mb-2 text-xs font-semibold text-amber-800 dark:text-amber-300">Placeholder values</div>
      <div className="flex flex-wrap gap-2">{Object.entries(c.placeholder_values).map(([k,v])=><Badge key={k} tone="warning">{k} · {v}</Badge>)}</div>
    </div>}

    {c.issues?.length > 0 && <div className="rounded-xl border border-red-100 bg-red-50/60 p-3 dark:border-red-950 dark:bg-red-950/20"><div className="mb-2 flex items-center gap-2 text-xs font-semibold text-red-700 dark:text-red-300"><AlertTriangle className="h-4 w-4"/>Detected issues</div><ul className="space-y-1 text-xs text-red-700 dark:text-red-300">{c.issues.map(x=><li key={x}>• {x}</li>)}</ul></div>}

    {c.recommendations?.length > 0 && <div className="rounded-xl border border-emerald-100 bg-emerald-50/50 p-3 dark:border-emerald-950 dark:bg-emerald-950/20"><div className="mb-2 flex items-center gap-2 text-xs font-semibold text-emerald-700 dark:text-emerald-300"><Sparkles className="h-4 w-4"/>Recommended action</div><ul className="space-y-1 text-xs text-emerald-700 dark:text-emerald-300">{c.recommendations.map(x=><li key={x}>• {x}</li>)}</ul></div>}

    {c.numeric_stats && <NumericDetails c={c}/>}
    {c.categorical_stats && <CategoricalDetails c={c}/>}
    {c.datetime_stats && <div className="grid grid-cols-2 gap-2 sm:grid-cols-5"><Stat l="Earliest" v={c.datetime_stats.earliest ? new Date(c.datetime_stats.earliest).toLocaleString() : null}/><Stat l="Latest" v={c.datetime_stats.latest ? new Date(c.datetime_stats.latest).toLocaleString() : null}/><Stat l="Range days" v={c.datetime_stats.date_range_days}/><Stat l="Unique dates" v={c.datetime_stats.unique_dates}/><Stat l="Missing / invalid" v={`${c.datetime_stats.missing_dates} / ${c.datetime_stats.invalid_values}`}/></div>}
  </div>;
}

export default function DatasetColumnTable({ columns }) {
  const [open, setOpen] = useState(null);
  const [query, setQuery] = useState("");
  const filtered = columns.filter(c => c.name.toLowerCase().includes(query.toLowerCase()) || c.dtype.toLowerCase().includes(query.toLowerCase()) || c.issues?.some(i => i.toLowerCase().includes(query.toLowerCase())));
  return <div className="overflow-hidden rounded-2xl border border-neutral-200 dark:border-neutral-800">
    <div className="flex flex-wrap items-center justify-between gap-3 border-b bg-neutral-50 p-3 dark:border-neutral-800 dark:bg-neutral-900">
      <div className="text-xs text-neutral-500">{filtered.length} of {columns.length} columns</div>
      <label className="flex items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm dark:border-neutral-700 dark:bg-neutral-950"><Search className="h-4 w-4 text-neutral-400"/><input className="w-48 bg-transparent outline-none" placeholder="Search columns / issues" value={query} onChange={e=>setQuery(e.target.value)}/></label>
    </div>
    <div className="overflow-x-auto">
      <table className="w-full min-w-[1100px] text-left text-sm">
        <thead><tr className="border-b bg-white text-xs uppercase tracking-wider text-neutral-500 dark:border-neutral-800 dark:bg-neutral-950">
          {["Column","Type","Missing","Unique","Signals","Sample values","Details"].map(h=><th key={h} className="px-4 py-3 font-medium">{h}</th>)}
        </tr></thead>
        <tbody>
          {filtered.map(c => <tr key={c.name} className="border-b align-top last:border-0 dark:border-neutral-900">
            <td className="px-4 py-3 font-semibold">{c.name}</td>
            <td className="px-4 py-3"><span className={`rounded-full px-2 py-1 text-xs font-medium ${TYPE_STYLES[c.dtype] || TYPE_STYLES.other}`}>{c.dtype}</span><div className="mt-1 text-[10px] text-neutral-400">{c.pandas_dtype}</div></td>
            <td className="px-4 py-3">{fmt(c.missing_count)}<div className="text-xs text-neutral-400">{c.missing_percentage}%</div></td>
            <td className="px-4 py-3">{fmt(c.unique_count)}<div className="text-xs text-neutral-400">{c.unique_percentage}%</div></td>
            <td className="max-w-[210px] px-4 py-3"><div className="flex flex-wrap gap-1">{c.issues?.slice(0, 4).map(i=><Badge key={i} tone={i.includes("missing") || i.includes("empty") ? "high" : "warning"}>{i}</Badge>)}{!c.issues?.length&&<Badge tone="success">Clean</Badge>}</div></td>
            <td className="max-w-[250px] px-4 py-3"><div className="flex flex-wrap gap-1">{c.sample_values?.map((v,i)=><span key={i} className="max-w-[115px] truncate rounded-md bg-neutral-100 px-2 py-1 text-xs dark:bg-neutral-800" title={v}>{v}</span>)}</div></td>
            <td className="px-4 py-3"><button type="button" onClick={()=>setOpen(open===c.name?null:c.name)} className="inline-flex items-center gap-1 rounded-lg border px-2.5 py-1.5 text-xs font-medium hover:bg-neutral-50 dark:border-neutral-700 dark:hover:bg-neutral-800">{open===c.name?<ChevronUp className="h-3.5 w-3.5"/>:<ChevronDown className="h-3.5 w-3.5"/>}{open===c.name?"Hide":"View"} all</button></td>
          </tr>)}
          {filtered.map(c => open===c.name && <tr key={`${c.name}-details`} className="bg-neutral-50/80 dark:bg-neutral-900/60"><td colSpan="7" className="px-4 py-5"><Details c={c}/></td></tr>)}
        </tbody>
      </table>
    </div>
    {!filtered.length && <div className="p-10 text-center text-sm text-neutral-500">No columns match this search.</div>}
  </div>;
}
