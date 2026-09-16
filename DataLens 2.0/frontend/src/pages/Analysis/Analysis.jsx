import { useEffect, useMemo, useState } from "react";
import { BarChart3, Database, Loader2, Sparkles } from "lucide-react";
import { useDatasetList } from "../../hooks/useDatasetProfile.js";
import { getAnalysis } from "../../services/api/analysis.js";

function fmt(v){return v==null?"—":Number(v).toLocaleString(undefined,{maximumFractionDigits:4})}

const modes = [
  {id:"univariate", label:"Univariate", icon:"①", help:"One variable at a time"},
  {id:"bivariate", label:"Bivariate", icon:"②", help:"Relationship between two variables"},
  {id:"multivariate", label:"Multivariate", icon:"③", help:"Three or more variables together"},
];

export default function Analysis(){
 const {datasets,status}=useDatasetList();
 const [id,setId]=useState("");
 const [data,setData]=useState(null);
 const [loading,setLoading]=useState(false);
 const [error,setError]=useState("");
 const [mode,setMode]=useState("univariate");
 const [column,setColumn]=useState("");
 const [x,setX]=useState("");
 const [y,setY]=useState("");
 const [z,setZ]=useState("");
 const [uniChart,setUniChart]=useState("histogram");
 const [biChart,setBiChart]=useState("scatter");
 const [cache,setCache]=useState(Date.now());

 useEffect(()=>{if(status==="success"&&(!id||!datasets.some(d=>d.id===id))){setId(datasets[0]?.id||"")}},[status,datasets,id]);
 useEffect(()=>{if(!id)return;setLoading(true);setError("");getAnalysis(id).then(r=>{setData(r);setColumn(r.numeric_columns?.[0]||r.categorical_columns?.[0]||"");setX(r.numeric_columns?.[0]||"");setY(r.numeric_columns?.[1]||"");setZ(r.numeric_columns?.[2]||"");}).catch(()=>setError("Analysis could not be generated.")).finally(()=>setLoading(false))},[id]);

 const numeric=data?.numeric_columns||[];
 const selectedStat=useMemo(()=>data?.numeric_stats?.find(s=>s.column===column),[data,column]);
 const plotUrl=useMemo(()=>{
   if(!id)return "";
   const p=new URLSearchParams({dataset_id:id});
   if(mode==="univariate"){p.set("chart_type",uniChart);p.set("x",column||"");}
   if(mode==="bivariate"){p.set("chart_type",biChart);p.set("x",x||"");p.set("y",y||"");}
   if(mode==="multivariate"){p.set("chart_type","scatter3d");p.set("x",x||"");p.set("y",y||"");p.set("z",z||"");}
   p.set("_t",String(cache));
   return `${import.meta.env.VITE_API_URL}/api/visualization/plot?${p.toString()}`;
 },[id,mode,uniChart,biChart,column,x,y,z,cache]);

 return <main className="page">
   <div className="mb-6">
     <div className="eyebrow">DATALENS · ANALYTICS</div>
     <h1 className="page-title">Analysis Studio</h1>
     <p className="page-subtitle">Explore your real dataset through univariate, bivariate and multivariate analysis without changing the uploaded data.</p>
   </div>

   <section className="card mb-6">
     <div className="mb-4 flex items-center gap-2"><Database className="h-5 w-5 text-neutral-500"/><div><h2 className="font-semibold">Analysis workspace</h2><p className="text-xs text-neutral-500">Choose the dataset and analysis level you want to explain.</p></div></div>
     <div className="grid gap-3 md:grid-cols-[minmax(220px,1fr)_2fr]">
       <label className="space-y-1"><span className="field-label">Dataset</span><select value={id} onChange={e=>setId(e.target.value)} className="input w-full">{datasets.map(d=><option key={d.id} value={d.id}>{d.filename}</option>)}</select></label>
       <div className="space-y-1"><span className="field-label">Analysis level</span><div className="grid grid-cols-3 gap-2">{modes.map(m=><button key={m.id} onClick={()=>{setMode(m.id);setCache(Date.now())}} className={`rounded-xl border px-3 py-3 text-left transition ${mode===m.id?"border-indigo-500 bg-indigo-50 text-indigo-700 shadow-sm":"border-neutral-200 bg-white hover:border-indigo-200 dark:border-neutral-800 dark:bg-neutral-900"}`}><div className="flex items-center gap-2 text-sm font-semibold"><span>{m.icon}</span>{m.label}</div><div className="mt-1 text-[11px] text-neutral-500">{m.help}</div></button>)}</div></div>
     </div>
   </section>

   {loading?<Loading/>:error?<Error text={error}/>:data&&<>
     {mode==="univariate"&&<Univariate data={data} column={column} setColumn={setColumn} chart={uniChart} setChart={setUniChart} stat={selectedStat} plotUrl={plotUrl} onRefresh={()=>setCache(Date.now())}/>}
     {mode==="bivariate"&&<Bivariate data={data} x={x} y={y} setX={setX} setY={setY} chart={biChart} setChart={setBiChart} plotUrl={plotUrl} onRefresh={()=>setCache(Date.now())}/>}
     {mode==="multivariate"&&<Multivariate data={data} x={x} y={y} z={z} setX={setX} setY={setY} setZ={setZ} plotUrl={plotUrl} onRefresh={()=>setCache(Date.now())}/>}
   </>}
 </main>
}

function Univariate({data,column,setColumn,chart,setChart,stat,plotUrl,onRefresh}){
 const categorical=data.categorical_columns||[];
 const all=[...(data.numeric_columns||[]),...categorical];
 return <div className="space-y-6">
  <section className="card"><div className="mb-4 flex items-center gap-2"><Sparkles className="h-5 w-5 text-indigo-500"/><div><h2 className="section-title">Univariate Analysis</h2><p className="text-xs text-neutral-500">Study one column independently: distribution, center and spread.</p></div></div>
   <div className="grid gap-3 md:grid-cols-2"><label className="space-y-1"><span className="field-label">Variable</span><select className="input w-full" value={column} onChange={e=>setColumn(e.target.value)}>{all.map(c=><option key={c}>{c}</option>)}</select></label><label className="space-y-1"><span className="field-label">Chart</span><select className="input w-full" value={chart} onChange={e=>setChart(e.target.value)}><option value="histogram">Histogram · Seaborn</option><option value="boxplot">Box plot · Seaborn</option><option value="violin">Violin · Seaborn</option><option value="kde">KDE density · Seaborn</option><option value="bar">Category frequency</option></select></label></div>
  </section>
  {stat&&<section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4"><Metric label="Mean" value={fmt(stat.mean)}/><Metric label="Median" value={fmt(stat.median)}/><Metric label="Std deviation" value={fmt(stat.std)}/><Metric label="Range" value={`${fmt(stat.min)} – ${fmt(stat.max)}`}/></section>}
  <PlotCard title={`${chart==="boxplot"?"Box plot":"Histogram"} — ${column||"Variable"}`} url={plotUrl} onRefresh={onRefresh}/>
 </div>
}

function Bivariate({data,x,y,setX,setY,chart,setChart,plotUrl,onRefresh}){
 const numeric=data.numeric_columns||[];
 const corr=data.correlation?.find(r=>r.row===x)?.values?.find(v=>v.column===y)?.value;
 return <div className="space-y-6">
  <section className="card"><div className="mb-4"><h2 className="section-title">Bivariate Analysis</h2><p className="text-xs text-neutral-500">Compare two numerical variables and inspect their relationship.</p></div><div className="grid gap-3 md:grid-cols-3"><Field label="X variable" value={x} setValue={setX} options={numeric}/><Field label="Y variable" value={y} setValue={setY} options={numeric}/><label className="space-y-1"><span className="field-label">Relationship plot</span><select className="input w-full" value={chart} onChange={e=>setChart(e.target.value)}><option value="scatter">Scatter · Seaborn</option><option value="regression">Regression · Seaborn</option></select></label></div></section>
  <section className="grid gap-3 md:grid-cols-3"><Metric label="X" value={x||"—"}/><Metric label="Y" value={y||"—"}/><Metric label="Pearson correlation" value={corr==null?"—":corr.toFixed(4)}/></section>
  <PlotCard title={`${x || "X"} × ${y || "Y"} — relationship`} url={plotUrl} onRefresh={onRefresh}/>
 </div>
}

function Multivariate({data,x,y,z,setX,setY,setZ,plotUrl,onRefresh}){
 const numeric=data.numeric_columns||[];
 return <div className="space-y-6">
  <section className="card"><div className="mb-4"><h2 className="section-title">Multivariate Analysis</h2><p className="text-xs text-neutral-500">Study three numerical variables simultaneously with a 3D scatter plot and the full correlation matrix.</p></div><div className="grid gap-3 md:grid-cols-3"><Field label="X variable" value={x} setValue={setX} options={numeric}/><Field label="Y variable" value={y} setValue={setY} options={numeric}/><Field label="Z variable" value={z} setValue={setZ} options={numeric}/></div></section>
  <PlotCard title={`3D relationship — ${x}, ${y}, ${z}`} url={plotUrl} onRefresh={onRefresh}/>
  <section><h2 className="section-title mb-3">Correlation matrix</h2>{data.correlation?.length?<div className="overflow-x-auto rounded-2xl border"><table className="min-w-full text-sm"><thead><tr className="border-b bg-neutral-50"><th className="px-4 py-3 text-left">Column</th>{numeric.map(c=><th key={c} className="px-4 py-3 text-right">{c}</th>)}</tr></thead><tbody>{data.correlation.map(r=><tr className="border-b last:border-0" key={r.row}><td className="px-4 py-3 font-medium">{r.row}</td>{r.values.map(v=><td key={v.column} className="px-4 py-3 text-right font-mono">{v.value==null?"—":v.value.toFixed(3)}</td>)}</tr>)}</tbody></table></div>:<Empty text="Correlation needs at least two numerical columns."/>}</section>
 </div>
}

function Field({label,value,setValue,options}){return <label className="space-y-1"><span className="field-label">{label}</span><select className="input w-full" value={value} onChange={e=>setValue(e.target.value)}>{options.map(c=><option key={c}>{c}</option>)}</select></label>}
function PlotCard({title,url,onRefresh}){return <section className="card"><div className="mb-4 flex items-center justify-between gap-3"><div><h2 className="section-title">{title}</h2><p className="mt-1 text-xs text-neutral-500">Generated from the selected uploaded dataset.</p></div><button className="btn" onClick={onRefresh}>Refresh chart</button></div><div className="min-h-[480px] rounded-2xl border bg-white/70 p-3"><img src={url} alt={title} className="mx-auto max-h-[680px] w-full object-contain" onError={e=>{e.currentTarget.style.display="none"}}/></div></section>}
function Metric({label,value}){return <div className="card"><div className="text-xs uppercase tracking-wider text-neutral-500">{label}</div><div className="mt-2 truncate text-lg font-semibold" title={String(value)}>{value}</div></div>}
function Loading(){return <div className="card flex items-center gap-2 text-sm text-neutral-500"><Loader2 className="h-4 w-4 animate-spin"/>Calculating from the real dataset…</div>}
function Error({text}){return <div className="card border-red-200 bg-red-50 text-sm text-red-700">{text}</div>}
function Empty({text}){return <div className="card text-sm text-neutral-500">{text}</div>}
