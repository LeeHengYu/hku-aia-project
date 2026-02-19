import { useEffect, useRef, type KeyboardEvent } from "react";

interface SendButtonProps {
  onClick: () => void;
  disabled: boolean;
}

const SendButton = ({ onClick, disabled }: SendButtonProps) => (
  <button
    className="composer-send bg-gradient-to-br from-teal-400 to-blue-400 dark:from-teal-500 dark:to-blue-500 text-slate-900"
    type="button"
    onClick={onClick}
    disabled={disabled}
  >
    Send
  </button>
);

interface ComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  disabled?: boolean;
  visible?: boolean;
}

const Composer = ({
  value,
  onChange,
  onSend,
  disabled,
  visible = true,
}: ComposerProps) => {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "0px";
    textarea.style.height = `${textarea.scrollHeight}px`;
  }, [value]);

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (!disabled) onSend();
    }
  };

  return visible ? (
    <div className="composer bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
      <textarea
        ref={textareaRef}
        className="composer-input placeholder-slate-400 dark:placeholder-slate-500"
        placeholder="Ask Gemini 3 Pro"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
        disabled={disabled}
      />
      <SendButton
        onClick={onSend}
        disabled={!!disabled || value.trim().length === 0}
      />
    </div>
  ) : null;
};

export default Composer;
