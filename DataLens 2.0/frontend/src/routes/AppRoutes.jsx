import { Route, Routes } from "react-router-dom";
import MainLayout from "../layouts/MainLayout.jsx";
import Home from "../pages/Home/Home.jsx";
import Upload from "../pages/Upload/Upload.jsx";
import Datasets from "../pages/Datasets/Datasets.jsx";
import Cleaning from "../pages/Cleaning/Cleaning.jsx";
import Analysis from "../pages/Analysis/Analysis.jsx";
import Visualization from "../pages/Visualization/Visualization.jsx";
import Comparison from "../pages/Comparison/Comparison.jsx";
import Insights from "../pages/Insights/Insights.jsx";
import Dashboard from "../pages/Dashboard/Dashboard.jsx";

// TODO: add route guards / not-found page once auth and error states exist.
export default function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/datasets" element={<Datasets />} />
        <Route path="/cleaning" element={<Cleaning />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/visualization" element={<Visualization />} />
        <Route path="/comparison" element={<Comparison />} />
        <Route path="/insights" element={<Insights />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Route>
    </Routes>
  );
}
