import { useState } from "react";

export interface SystemInstructionModalProps {
  initialValue: string;
  onSave: (value: string | undefined) => void;
  onClose: () => void;
}

const SystemInstructionModal = ({
  initialValue,
  onSave,
  onClose,
}: SystemInstructionModalProps) => {
  const [draft, setDraft] = useState(initialValue);

  const handleSave = () => {
    const trimmed = draft.trim();
    onSave(trimmed.length > 0 ? trimmed : undefined);
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        className="w-[640px] max-w-[calc(100vw-48px)] rounded-[18px] p-6 flex flex-col gap-4 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="text-base font-semibold text-slate-900 dark:text-slate-100">
          Edit System Instructions
        </div>
        <textarea
          className="resize-y rounded-xl px-3 py-2.5 w-full min-h-[280px] font-[inherit] text-sm leading-relaxed outline-none bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500"
          placeholder="Enter system instruction…"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          autoFocus
        />
        <div className="flex justify-end gap-2">
          <button
            className="px-4 py-2 rounded-[10px] text-sm font-medium cursor-pointer border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
            type="button"
            onClick={onClose}
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 rounded-[10px] text-sm font-medium cursor-pointer border-none bg-teal-500 dark:bg-teal-600 text-white hover:bg-teal-600 dark:hover:bg-teal-700"
            type="button"
            onClick={handleSave}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default SystemInstructionModal;
