import { useEffect, useMemo, useState } from "react";
import { BarChart3, Database, Download, Info, Loader2, RefreshCw } from "lucide-react";
import { useDatasetList } from "../../hooks/useDatasetProfile.js";
import { getChartData } from "../../services/api/visualization.js";

const types = [
  ["bar", "Bar"], ["line", "Line"], ["area", "Area"], ["pie", "Pie"],
  ["donut", "Donut"], ["scatter", "Scatter"], ["histogram", "Histogram"],
  ["boxplot", "Box plot"], ["violin", "Violin · Seaborn"], ["kde", "KDE density · Seaborn"],
  ["regression", "Regression · Seaborn"], ["countplot", "Count plot · Seaborn"],
  ["scatter3d", "3D Scatter · Multivariate"],
];

export default function Visualization() {
  const { datasets, status } = useDatasetList();
  const [id, setId] = useState("");
  const [type, setType] = useState("bar");
  const [x, setX] = useState("");
  const [y, setY] = useState("");
  const [z, setZ] = useState("");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [cacheBust, setCacheBust] = useState(Date.now());
  const [plotError, setPlotError] = useState(false);

  useEffect(() => {
    if (status === "success" && (!id || !datasets.some(d => d.id === id))) {
      setId(datasets[0]?.id || "");
      setX(""); setY("");
    }
  }, [status, datasets, id]);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true); setError("");
    getChartData(id, { chart_type: type, x: x || null, y: y || null, z: z || null })
      .then(r => {
        if (cancelled) return;
        setData(r);
        // Backend chooses intelligent defaults for the selected chart type.
        if (!x && r.x) setX(r.x);
        if (!y && r.y) setY(r.y);
        if (!z && r.z) setZ(r.z);
      })
      .catch(err => {
        if (!cancelled) { setData(null); setError(err?.response?.data?.detail || "Could not build this visualization."); }
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [id, type, x, y, z]);

  const cols = data?.available_columns || [];
  const plotUrl = useMemo(() => {
    if (!id) return "";
    const p = new URLSearchParams({ dataset_id: id, chart_type: type });
    if (x) p.set("x", x);
    if (y) p.set("y", y);
    if (z) p.set("z", z);
    p.set("_t", String(cacheBust));
    return `${import.meta.env.VITE_API_URL}/api/visualization/plot?${p.toString()}`;
  }, [id, type, x, y, z, cacheBust]);

  useEffect(() => { setCacheBust(Date.now()); setPlotError(false); }, [id, type, x, y, z]);

  const changeDataset = value => { setId(value); setX(""); setY(""); setZ(""); setData(null); setPlotError(false); };

  return (
    <main className="page">
      <div className="mb-6">
        <div className="eyebrow">DATALENS · VISUALS</div>
        <h1 className="page-title">Visualization Studio</h1>
        <p className="page-subtitle">
          Build publication-ready charts from any uploaded CSV or Excel workbook.
          Data is prepared with pandas/NumPy and rendered with Matplotlib + Seaborn on the backend.
        </p>
      </div>

      <section className="card mb-6">
        <div className="mb-4 flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-neutral-500" />
          <div>
            <h2 className="font-semibold">Chart configuration</h2>
            <p className="text-xs text-neutral-500">Defaults are selected automatically from the actual column types.</p>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-4">
          <label className="space-y-1"><span className="field-label">Dataset</span>
            <select className="input w-full" value={id} onChange={e => changeDataset(e.target.value)}>
              {datasets.map(d => <option key={d.id} value={d.id}>{d.filename}{d.sheet_name ? ` · ${d.sheet_name}` : ""}</option>)}
            </select>
          </label>
          <label className="space-y-1"><span className="field-label">Chart type</span>
            <select className="input w-full" value={type} onChange={e => { setType(e.target.value); setX(""); setY(""); setZ(""); }}>
              {types.map(([v, label]) => <option key={v} value={v}>{label}</option>)}
            </select>
          </label>
          <label className="space-y-1"><span className="field-label">X / category</span>
            <select className="input w-full" value={x} onChange={e => setX(e.target.value)}>
              <option value="">Auto</option>{cols.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>
          <label className="space-y-1"><span className="field-label">Y / value</span>
            <select className="input w-full" value={y} onChange={e => setY(e.target.value)}>
              <option value="">Auto</option>{cols.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>
          {type === "scatter3d" && <label className="space-y-1"><span className="field-label">Z / third variable</span>
            <select className="input w-full" value={z} onChange={e => setZ(e.target.value)}>
              <option value="">Auto</option>{cols.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </label>}
        </div>
      </section>

      {status === "loading" && <div className="card flex items-center gap-2 text-sm text-neutral-500"><Loader2 className="h-4 w-4 animate-spin" />Loading datasets…</div>}
      {status === "success" && !datasets.length && <div className="card text-sm text-neutral-500">Upload a CSV or XLSX file first.</div>}
      {error && <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}

      {id && data && (
        <>
          <section className="mb-4 grid grid-cols-2 gap-3 md:grid-cols-4">
            <Metric label="Rows" value={data.rows} icon={Database} />
            <Metric label="Columns" value={data.columns} icon={Database} />
            <Metric label="X field" value={data.x || "—"} />
            <Metric label="Y field" value={data.y || "Count"} />{type === "scatter3d" && <Metric label="Z field" value={data.z || "—"} />}
          </section>

          <section className="card overflow-hidden">
            <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
              <div>
                <h2 className="section-title">{type[0].toUpperCase() + type.slice(1)} chart</h2>
                <p className="mt-1 text-xs text-neutral-500">Server-rendered with Matplotlib from the selected dataset.</p>
              </div>
              <div className="flex gap-2">
                <button className="btn" onClick={() => setCacheBust(Date.now())}><RefreshCw className="h-4 w-4" />Refresh</button>
                <a className="btn" href={plotUrl} download="datalens-chart.png"><Download className="h-4 w-4" />PNG</a>
              </div>
            </div>
            <div className="min-h-[480px] rounded-2xl border bg-neutral-50 p-3 dark:border-neutral-800 dark:bg-neutral-950">
              {loading ? <div className="flex h-[450px] items-center justify-center text-sm text-neutral-500"><Loader2 className="mr-2 h-5 w-5 animate-spin" />Rendering chart…</div>
                : plotError ? <div className="flex h-[450px] items-center justify-center text-sm text-red-600">The chart could not be rendered for this configuration. Try another chart type or column.</div>
                : <img key={plotUrl} src={plotUrl} alt={`${type} chart`} className="mx-auto max-h-[700px] w-full object-contain" onError={() => setPlotError(true)} />}
            </div>
          </section>

          <section className="card mt-4">
            <div className="mb-3 flex items-center gap-2"><Info className="h-4 w-4 text-neutral-500" /><h2 className="font-semibold">Chart data</h2></div>
            <div className="overflow-auto rounded-xl border">
              <table className="min-w-full text-xs">
                <thead><tr className="border-b bg-neutral-50 dark:bg-neutral-950">
                  {(data.data[0] ? Object.keys(data.data[0]) : []).map(k => <th className="px-3 py-2 text-left font-medium text-neutral-500" key={k}>{k}</th>)}
                </tr></thead>
                <tbody>{data.data.slice(0, 100).map((row, i) => <tr className="border-b last:border-0" key={i}>
                  {Object.values(row).map((v, j) => <td className="px-3 py-2" key={j}>{v == null ? "—" : String(v)}</td>)}
                </tr>)}</tbody>
              </table>
              {!data.data.length && <div className="p-8 text-center text-sm text-neutral-500">No compatible values were found for this configuration. Try another column or chart type.</div>}
            </div>
          </section>
        </>
      )}
    </main>
  );
}

function Metric({ label, value, icon: Icon }) {
  return <div className="card">
    <div className="flex items-center justify-between text-xs uppercase tracking-wider text-neutral-500">{label}{Icon && <Icon className="h-4 w-4 text-neutral-400" />}</div>
    <div className="mt-2 truncate text-lg font-semibold" title={String(value)}>{typeof value === "number" ? value.toLocaleString() : value}</div>
  </div>;
}
