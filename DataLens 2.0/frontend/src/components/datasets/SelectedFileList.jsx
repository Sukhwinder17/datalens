import { FileText, X } from "lucide-react";
import { formatFileSize } from "../../utils/formatters.js";

/**
 * List of files the user picked but hasn't uploaded yet, each
 * removable before the upload request goes out.
 */
export default function SelectedFileList({ files, onRemove }) {
  if (files.length === 0) return null;

  return (
    <div>
      <p className="mb-2 text-sm font-medium text-neutral-700 dark:text-neutral-300">
        Selected datasets
      </p>
      <ul className="flex flex-col gap-2">
        {files.map((file, index) => (
          <li
            key={`${file.name}-${file.size}-${file.lastModified}`}
            className="flex items-center justify-between rounded-xl border border-neutral-200 px-4 py-3 dark:border-neutral-800"
          >
            <div className="flex min-w-0 items-center gap-3">
              <FileText className="h-4 w-4 shrink-0 text-neutral-400" strokeWidth={1.75} />
              <div className="min-w-0">
                <p className="truncate text-sm text-neutral-900 dark:text-neutral-100">
                  {file.name}
                </p>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  {file.name.split(".").pop().toUpperCase()} &middot; {formatFileSize(file.size)}
                </p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => onRemove(index)}
              className="shrink-0 rounded-md p-1.5 text-neutral-400 transition-colors hover:bg-neutral-100 hover:text-neutral-700 dark:hover:bg-neutral-800 dark:hover:text-neutral-200"
              aria-label={`Remove ${file.name}`}
            >
              <X className="h-4 w-4" strokeWidth={1.75} />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
