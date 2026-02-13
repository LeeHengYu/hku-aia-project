import { PROMPT_LOADED_LABEL } from "../constants/uiText";

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
        {subtitle ? <div className="main-subtitle">{subtitle}</div> : null}
      </div>
      {showPromptLoaded ? (
        <div className="system-indicator">{PROMPT_LOADED_LABEL}</div>
      ) : null}
    </div>
  );
};

export default MainHeader;
