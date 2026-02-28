import { useRef, useState, type ChangeEvent } from "react";
import { useChatState, useChatActions } from "../controllers/useChatStore";
import GroupSelector from "./GroupSelector";
import ChatList from "./ChatList";
import SystemInstructionModal from "./SystemInstructionModal";
import type { VertexPromptExport } from "../lib/types";

interface ImportPromptButtonProps {
  onImport: (data: VertexPromptExport) => Promise<void>;
}

const ImportPromptButton = ({ onImport }: ImportPromptButtonProps) => {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    let data: VertexPromptExport;
    try {
      const text = await file.text();
      data = JSON.parse(text);
    } catch (error) {
      console.error(error);
      alert(
        "Unable to parse the JSON file. Please use the prompt exported from Vertex AI Studio.",
      );
      event.target.value = "";
      return;
    }

    try {
      await onImport(data);
    } catch (error) {
      console.error(error);
      alert("Failed to save the imported messages to the database.");
    } finally {
      event.target.value = "";
    }
  };

  return (
    <>
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
    </>
  );
};

const Sidebar = () => {
  const { activeChat } = useChatState();
  const { handleNewChat, handleImport, handleSetSystemInstruction } = useChatActions();
  const [modalOpen, setModalOpen] = useState(false);

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
        <ImportPromptButton onImport={handleImport} />
        <GroupSelector />
      </div>
      <ChatList />
      <div className="mt-auto pt-3">
        <button
          className="sidebar-secondary border border-slate-300 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed w-full !text-center"
          type="button"
          onClick={() => setModalOpen(true)}
          disabled={!activeChat}
        >
          System Instructions
        </button>
      </div>
      {modalOpen && activeChat && (
        <SystemInstructionModal
          initialValue={activeChat.systemInstruction ?? ""}
          onSave={(value) => handleSetSystemInstruction(activeChat.id, value)}
          onClose={() => setModalOpen(false)}
        />
      )}
    </aside>
  );
};

export default Sidebar;
