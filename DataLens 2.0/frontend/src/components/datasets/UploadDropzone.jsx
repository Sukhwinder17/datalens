import { useCallback, useRef, useState } from "react";
import { Aperture } from "lucide-react";
import { ACCEPTED_EXTENSIONS } from "../../hooks/useDatasets.js";

/**
 * Drag-and-drop + click-to-browse target for picking dataset files.
 * Purely presentational — the parent owns what happens to the files.
 */
export default function UploadDropzone({ onFilesSelected }) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  const handleDrop = useCallback(
    (event) => {
      event.preventDefault();
      setIsDragging(false);
      if (event.dataTransfer.files?.length) {
        onFilesSelected(event.dataTransfer.files);
      }
    },
    [onFilesSelected]
  );

  const handleBrowseChange = useCallback(
    (event) => {
      if (event.target.files?.length) {
        onFilesSelected(event.target.files);
      }
      // allow picking the same file again after removing it
      event.target.value = "";
    },
    [onFilesSelected]
  );

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") inputRef.current?.click();
      }}
      className={[
        "group flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed px-6 py-14 text-center transition-colors",
        isDragging
          ? "border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-500/10"
          : "border-neutral-300 hover:border-neutral-400 dark:border-neutral-700 dark:hover:border-neutral-600",
      ].join(" ")}
    >
      <Aperture
        className={[
          "h-9 w-9 transition-transform duration-300",
          isDragging ? "rotate-45 text-blue-500 dark:text-blue-400" : "text-neutral-400 group-hover:rotate-12 dark:text-neutral-500",
        ].join(" ")}
        strokeWidth={1.5}
      />
      <div>
        <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
          Drop files here or browse files
        </p>
        <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">
          CSV &middot; XLSX
        </p>
      </div>
      <input
        ref={inputRef}
        type="file"
        multiple
        accept={ACCEPTED_EXTENSIONS.map((ext) => `.${ext}`).join(",")}
        onChange={handleBrowseChange}
        className="hidden"
      />
    </div>
  );
}
