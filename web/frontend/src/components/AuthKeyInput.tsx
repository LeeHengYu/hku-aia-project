import { AUTH_PLACEHOLDER } from "../constants/uiText";

interface AuthKeyInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

const AuthKeyInput = ({
  value,
  onChange,
  placeholder = AUTH_PLACEHOLDER,
}: AuthKeyInputProps) => {
  return (
    <div className="auth-row bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
      <input
        id="auth-key"
        className="auth-input placeholder-slate-400 dark:placeholder-slate-500"
        type="password"
        placeholder={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
};

export default AuthKeyInput;
