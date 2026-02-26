import { useChatContext } from "../controllers/useChatStore";
import type { GroupSelection } from "../controllers/chatStore";

const GROUP_OPTIONS: { value: GroupSelection; label: string }[] = [
  { value: "market", label: "Market" },
  { value: "product", label: "Product" },
  { value: "both", label: "Both" },
];

const GroupSelector = () => {
  const { selectedGroup, setSelectedGroup } = useChatContext();

  return (
    <div className="sidebar-section">
      <div className="group-selector">
        {GROUP_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            className={`group-selector-btn${selectedGroup === opt.value ? " group-selector-btn--active" : ""}`}
            onClick={() => setSelectedGroup(opt.value)}
          >
            {opt.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default GroupSelector;
