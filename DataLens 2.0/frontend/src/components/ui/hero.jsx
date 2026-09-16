import { useEffect, useRef, useState } from "react";
import { MeshGradient, PulsingBorder } from "@paper-design/shaders-react";
import { motion } from "framer-motion";
import { ArrowRight, BarChart3, Database, Sparkles, Upload, WandSparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { ROUTES } from "../../constants/routes.js";

export default function DataLensHero() {
  const containerRef = useRef(null);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    const node = containerRef.current;
    if (!node) return undefined;
    const enter = () => setIsActive(true);
    const leave = () => setIsActive(false);
    node.addEventListener("mouseenter", enter);
    node.addEventListener("mouseleave", leave);
    return () => {
      node.removeEventListener("mouseenter", enter);
      node.removeEventListener("mouseleave", leave);
    };
  }, []);

  return (
    <section ref={containerRef} className="dl-hero" aria-label="DataLens data intelligence workspace">
      <div className="dl-shader dl-shader-main" aria-hidden="true">
        <MeshGradient
          className="absolute inset-0 h-full w-full"
          colors={["#050816", "#312e81", "#0891b2", "#7c3aed", "#ec4899"]}
          speed={0.22}
          backgroundColor="#050816"
        />
        <MeshGradient
          className="absolute inset-0 h-full w-full opacity-50"
          colors={["#000000", "#22d3ee", "#a78bfa", "#fb7185"]}
          speed={0.15}
          wireframe="true"
          backgroundColor="transparent"
        />
      </div>

      <div className="dl-hero-grid" aria-hidden="true" />
      <div className={`dl-glow dl-glow-a ${isActive ? "is-active" : ""}`} aria-hidden="true" />
      <div className={`dl-glow dl-glow-b ${isActive ? "is-active" : ""}`} aria-hidden="true" />

      <div className="dl-hero-content">
        <motion.div
          className="dl-kicker"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55 }}
        >
          <Sparkles size={15} />
          Intelligent data workspace
        </motion.div>

        <motion.h1
          className="dl-hero-title"
          initial={{ opacity: 0, y: 28 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.1 }}
        >
          <span>See your data.</span>
          <span className="dl-gradient-text">Understand it.</span>
          <span>Act on it.</span>
        </motion.h1>

        <motion.p
          className="dl-hero-lead"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.25 }}
        >
          Upload CSV or Excel files, automatically profile data quality, clean issues, explore
          univariate, bivariate and multivariate patterns, and turn results into publication-ready visuals.
        </motion.p>

        <motion.div
          className="dl-hero-actions"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <Link to={ROUTES.UPLOAD} className="dl-primary-btn">
            <Upload size={17} />
            Upload dataset
            <ArrowRight size={16} />
          </Link>
          <Link to={ROUTES.DATASETS} className="dl-secondary-btn">
            <Database size={17} />
            Explore datasets
          </Link>
        </motion.div>

        <motion.div
          className="dl-feature-row"
          initial={{ opacity: 0, y: 22 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.55 }}
        >
          <Feature icon={<WandSparkles size={17} />} title="Auto profiling" text="Types, missing values, duplicates & outliers" />
          <Feature icon={<BarChart3 size={17} />} title="Deep analysis" text="Uni · Bi · Multi-variable exploration" />
          <Feature icon={<Sparkles size={17} />} title="Visual insights" text="Charts, correlations and clear findings" />
        </motion.div>
      </div>

      <motion.div
        className="dl-data-orb"
        animate={{ y: [0, -14, 0], rotate: [0, 5, 0] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
        aria-hidden="true"
      >
        <div className="dl-orb-core">
          <div className="dl-orb-label">DATA</div>
          <div className="dl-orb-value">360°</div>
          <div className="dl-orb-sub">intelligence</div>
        </div>
        <div className="dl-orbit-ring dl-orbit-ring-one" />
        <div className="dl-orbit-ring dl-orbit-ring-two" />
        <div className="dl-orbit-dot dot-one" />
        <div className="dl-orbit-dot dot-two" />
        <div className="dl-orbit-dot dot-three" />
      </motion.div>

      <div className="dl-pulse-badge" aria-hidden="true">
        <PulsingBorder
          colors={["#22d3ee", "#8b5cf6", "#f472b6", "#f59e0b", "#22d3ee"]}
          colorBack="#00000000"
          speed={1.2}
          roundness={1}
          thickness={0.12}
          softness={0.18}
          intensity={4}
          spotsPerColor={4}
          spotSize={0.12}
          pulse={0.15}
          smoke={0.45}
          smokeSize={3}
          scale={0.8}
          rotation={0}
          style={{ width: "58px", height: "58px", borderRadius: "50%" }}
        />
      </div>
    </section>
  );
}

function Feature({ icon, title, text }) {
  return (
    <motion.div className="dl-feature-card" whileHover={{ y: -5, scale: 1.015 }} transition={{ type: "spring", stiffness: 320, damping: 20 }}>
      <div className="dl-feature-icon">{icon}</div>
      <div>
        <strong>{title}</strong>
        <span>{text}</span>
      </div>
    </motion.div>
  );
}
