import { CheckCircle2 } from "lucide-react";
import { Link } from "react-router-dom";
import { formatFileSize } from "../../utils/formatters.js";
import { ROUTES } from "../../constants/routes.js";

/**
 * Read-only summary of datasets that have finished uploading this
 * session, each linking through to its full profile on the Datasets
 * page. These ids are what later phases (cleaning, analysis, ...)
 * will operate on too.
 */
export default function UploadedDatasetList({ datasets }) {
  if (datasets.length === 0) return null;

  return (
    <div>
      <p className="mb-2 text-sm font-medium text-neutral-700 dark:text-neutral-300">
        {datasets.length} dataset{datasets.length === 1 ? "" : "s"} uploaded
      </p>
      <ul className="flex flex-col gap-2">
        {datasets.map((dataset) => (
          <li
            key={dataset.id}
            className="flex items-center justify-between gap-3 rounded-xl border border-emerald-200 bg-emerald-50/60 px-4 py-3 dark:border-emerald-900 dark:bg-emerald-500/10"
          >
            <div className="flex min-w-0 items-center gap-3">
              <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" strokeWidth={1.75} />
              <div className="min-w-0">
                <p className="truncate text-sm text-neutral-900 dark:text-neutral-100">
                  {dataset.filename}
                </p>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  {dataset.format.toUpperCase()} &middot; {formatFileSize(dataset.size)}
                </p>
              </div>
            </div>
            <Link
              to={`${ROUTES.DATASETS}?dataset=${dataset.id}`}
              className="shrink-0 rounded-lg border border-emerald-300 bg-white px-3 py-1.5 text-xs font-medium text-emerald-700 transition-colors hover:bg-emerald-50 dark:border-emerald-800 dark:bg-neutral-900 dark:text-emerald-400 dark:hover:bg-emerald-500/10"
            >
              View Profile
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
