import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.tsx";

// Sync theme with localStorage before first render to avoid flash
const storedTheme = localStorage.getItem("theme") ?? "dark";
document.documentElement.classList.toggle("dark", storedTheme === "dark");

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
