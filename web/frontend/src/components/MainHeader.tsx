import { PROMPT_LOADED_LABEL } from "../constants/uiText";
import ThemeToggle from "./ThemeToggle";

interface MainHeaderProps {
  title?: string;
  subtitle?: string;
  showPromptLoaded: boolean;
}

const MainHeader = ({ title, subtitle, showPromptLoaded }: MainHeaderProps) => {
  return (
    <div className="main-header">
      <div>
        {title ? <div className="main-title">{title}</div> : null}
        {subtitle ? (
          <div className="main-subtitle text-slate-500 dark:text-slate-400">
            {subtitle}
          </div>
        ) : null}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        {showPromptLoaded ? (
          <div className="system-indicator bg-blue-500/[0.14] border border-blue-500/40 dark:border-blue-400/40 text-blue-700 dark:text-blue-200">
            {PROMPT_LOADED_LABEL}
          </div>
        ) : null}
        <ThemeToggle />
      </div>
    </div>
  );
};

export default MainHeader;
