import ThemeToggle from "./ThemeToggle";

interface MainHeaderProps {
  title?: string;
  subtitle?: string;
}

const MainHeader = ({ title, subtitle }: MainHeaderProps) => {
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
        <ThemeToggle />
      </div>
    </div>
  );
};

export default MainHeader;
