// Wraps services/api/datasets.js with the state the Upload page needs:
// which files are picked but not yet sent, which have finished
// uploading, and the request's loading/error state.

import { useCallback, useState } from "react";
import { uploadDatasets } from "../services/api/datasets.js";

export const ACCEPTED_EXTENSIONS = ["csv", "xlsx"];

function getExtension(filename) {
  return filename.split(".").pop()?.toLowerCase() ?? "";
}

function fileKey(file) {
  return `${file.name}-${file.size}-${file.lastModified}`;
}

export function useDatasets() {
  const [pendingFiles, setPendingFiles] = useState(/** @type {File[]} */ ([]));
  const [uploadedDatasets, setUploadedDatasets] = useState(
    /** @type {import("../types/dataset.js").DatasetSummary[]} */ ([])
  );
  const [uploadErrors, setUploadErrors] = useState(
    /** @type {import("../types/dataset.js").UploadError[]} */ ([])
  );
  const [status, setStatus] = useState("idle"); // idle | uploading | success | error

  // Accepts a FileList or File[]. Silently skips files whose extension
  // isn't supported and dedupes against what's already pending — the
  // server re-validates everything anyway, this is just to keep the
  // picker tidy before the request goes out.
  const addFiles = useCallback((incomingFiles) => {
    const incoming = Array.from(incomingFiles).filter((file) =>
      ACCEPTED_EXTENSIONS.includes(getExtension(file.name))
    );
    setPendingFiles((prev) => {
      const existingKeys = new Set(prev.map(fileKey));
      const deduped = incoming.filter((file) => !existingKeys.has(fileKey(file)));
      return [...prev, ...deduped];
    });
  }, []);

  const removeFile = useCallback((index) => {
    setPendingFiles((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const upload = useCallback(async () => {
    if (pendingFiles.length === 0) return;

    setStatus("uploading");
    setUploadErrors([]);

    try {
      const result = await uploadDatasets(pendingFiles);
      setUploadedDatasets((prev) => [...prev, ...result.uploaded]);
      setUploadErrors(result.errors ?? []);
      setPendingFiles([]);
      setStatus(result.errors?.length ? "error" : "success");
    } catch {
      setUploadErrors([
        {
          filename: "",
          error: "Something went wrong while uploading the dataset. Please try again.",
        },
      ]);
      setStatus("error");
    }
  }, [pendingFiles]);

  return {
    pendingFiles,
    uploadedDatasets,
    uploadErrors,
    status,
    addFiles,
    removeFile,
    upload,
  };
}
