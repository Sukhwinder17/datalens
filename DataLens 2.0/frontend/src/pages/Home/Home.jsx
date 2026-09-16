import { BarChart3, Database, FileSpreadsheet, GitCompare, Sparkles, Upload } from "lucide-react";
import { Link } from "react-router-dom";
import DataLensHero from "../../components/ui/hero.jsx";
import { ROUTES } from "../../constants/routes.js";

export default function Home() {
  return (
    <div className="home-page">
      <DataLensHero />
      <section className="home-below">
        <div className="home-section-heading">
          <span className="home-mini-kicker"><Sparkles size={14} /> One workspace</span>
          <h2>From raw file to useful insight.</h2>
          <p>Keep the existing DataLens workflow — just make the experience feel like a real data product.</p>
        </div>
        <div className="home-workflow-grid">
          <WorkflowCard icon={<Upload />} number="01" title="Upload" text="Bring in CSV or XLSX files and let DataLens detect the structure." to={ROUTES.UPLOAD} />
          <WorkflowCard icon={<Database />} number="02" title="Profile & Clean" text="Inspect missing values, duplicates, outliers, types and real rows." to={ROUTES.DATASETS} />
          <WorkflowCard icon={<BarChart3 />} number="03" title="Analyze" text="Explore univariate, bivariate and multivariate relationships." to={ROUTES.ANALYSIS} />
          <WorkflowCard icon={<GitCompare />} number="04" title="Visualize & Compare" text="Build charts, compare datasets and turn evidence into findings." to={ROUTES.VISUALIZATION} />
        </div>
        <div className="home-proof-row">
          <div><FileSpreadsheet size={17} /><span>CSV + Excel ready</span></div>
          <div><Sparkles size={17} /><span>Automatic data-quality signals</span></div>
          <div><BarChart3 size={17} /><span>Publication-ready visualizations</span></div>
        </div>
      </section>
    </div>
  );
}

function WorkflowCard({ icon, number, title, text, to }) {
  return (
    <Link to={to} className="home-workflow-card">
      <div className="home-workflow-top"><span>{number}</span><div>{icon}</div></div>
      <h3>{title}</h3>
      <p>{text}</p>
      <span className="home-card-link">Open <span>→</span></span>
    </Link>
  );
}
