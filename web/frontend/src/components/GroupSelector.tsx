import { useChatContext } from "../controllers/useChatStore";
import type { GroupSelection } from "../controllers/chatStore";

const GROUP_OPTIONS: { value: GroupSelection; label: string }[] = [
  { value: "gp2", label: "Group 2" },
  { value: "gp3", label: "Group 3" },
];

const GroupSelector = () => {
  const { selectedGroup, setSelectedGroup } = useChatContext();

  return (
    <div className="sidebar-section">
      <div className="sidebar-select-wrapper">
        <select
          className="sidebar-select"
          value={selectedGroup}
          onChange={(e) => setSelectedGroup(e.target.value as GroupSelection)}
        >
          {GROUP_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <svg
          className="sidebar-select-arrow"
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
      </div>
    </div>
  );
};

export default GroupSelector;
