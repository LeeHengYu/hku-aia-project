import { useRef, type ChangeEvent } from "react";
import { useChatContext } from "../controllers/useChatStore";
import GroupSelector from "./GroupSelector";
import ChatList from "./ChatList";

const Sidebar = () => {
  const { handleNewChat, handleImport } = useChatContext();

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const data = JSON.parse(text);
      handleImport(data);
    } catch (error) {
      console.error(error);
      alert(
        "Unable to parse the JSON file. Please use the prompt exported from Vertex AI Studio.",
      );
    } finally {
      event.target.value = "";
    }
  };

  return (
    <aside className="sidebar bg-slate-100 dark:bg-slate-900 border-r border-slate-200 dark:border-slate-700">
      <div className="sidebar-top">
        <button
          className="sidebar-action bg-slate-200 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-slate-100"
          onClick={handleNewChat}
          type="button"
        >
          New chat
        </button>
        <button
          className="sidebar-secondary border border-slate-300 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800"
          onClick={() => {
            fileInputRef.current?.click();
          }}
          type="button"
        >
          Import prompt
        </button>
        <input
          ref={fileInputRef}
          className="file-input"
          type="file"
          accept="application/json"
          onChange={handleFileChange}
        />
        <GroupSelector />
      </div>
      <ChatList />
    </aside>
  );
};

export default Sidebar;
