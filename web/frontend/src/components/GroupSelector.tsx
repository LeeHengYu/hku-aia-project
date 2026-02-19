import { useChatContext } from "../controllers/useChatStore";
import type { GroupSelection } from "../controllers/chatStore";

const GROUP_OPTIONS: { value: GroupSelection; label: string }[] = [
  { value: "gp2", label: "Market" },
  { value: "gp3", label: "Product" },
];

const DropdownArrow = () => (
  <svg
    className="sidebar-select-arrow text-slate-500 dark:text-slate-400"
    xmlns="http://www.w3.org/2000/svg"
    width="12"
    height="12"
    viewBox="0 0 12 12"
    aria-hidden="true"
  >
    <path
      d="M2 4l4 4 4-4"
      stroke="currentColor"
      strokeWidth="1.5"
      fill="none"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const GroupSelector = () => {
  const { selectedGroup, setSelectedGroup } = useChatContext();

  return (
    <div className="sidebar-section">
      <div className="sidebar-select-wrapper">
        <select
          className="sidebar-select bg-lime-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100"
          value={selectedGroup}
          onChange={(e) => setSelectedGroup(e.target.value as GroupSelection)}
        >
          {GROUP_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <DropdownArrow />
      </div>
    </div>
  );
};

export default GroupSelector;
