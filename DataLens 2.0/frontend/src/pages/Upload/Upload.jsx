import { AlertCircle, Loader2 } from "lucide-react";
import { useDatasets } from "../../hooks/useDatasets.js";
import UploadDropzone from "../../components/datasets/UploadDropzone.jsx";
import SelectedFileList from "../../components/datasets/SelectedFileList.jsx";
import UploadedDatasetList from "../../components/datasets/UploadedDatasetList.jsx";

export default function Upload() {
  const {
    pendingFiles,
    uploadedDatasets,
    uploadErrors,
    status,
    addFiles,
    removeFile,
    upload,
  } = useDatasets();

  const isUploading = status === "uploading";

  return (
    <div className="mx-auto flex max-w-xl flex-col gap-8 px-6 py-16">
      <div className="text-center">
        <h1 className="text-3xl font-semibold tracking-tight text-neutral-900 dark:text-neutral-100">
          Upload your datasets
        </h1>
        <p className="mt-2 text-sm text-neutral-500 dark:text-neutral-400">
          Analyze multiple datasets together. Start by uploading your data files.
        </p>
      </div>

      <UploadDropzone onFilesSelected={addFiles} />

      <SelectedFileList files={pendingFiles} onRemove={removeFile} />

      {uploadErrors.length > 0 && (
        <div className="flex flex-col gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-500/10 dark:text-red-400">
          {uploadErrors.map((err, index) => (
            <div key={`${err.filename}-${index}`} className="flex items-start gap-2">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" strokeWidth={1.75} />
              <span>
                {err.filename ? <strong className="font-medium">{err.filename}:</strong> : null}{" "}
                {err.error}
              </span>
            </div>
          ))}
        </div>
      )}

      {pendingFiles.length > 0 && (
        <button
          type="button"
          onClick={upload}
          disabled={isUploading}
          className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {isUploading && <Loader2 className="h-4 w-4 animate-spin" />}
          {isUploading
            ? "Uploading..."
            : `Upload ${pendingFiles.length} dataset${pendingFiles.length === 1 ? "" : "s"}`}
        </button>
      )}

      <UploadedDatasetList datasets={uploadedDatasets} />

      {pendingFiles.length === 0 && uploadedDatasets.length === 0 && (
        <p className="text-center text-sm text-neutral-400 dark:text-neutral-500">
          No datasets yet — drop a CSV or XLSX file above to get started.
        </p>
      )}
    </div>
  );
}
