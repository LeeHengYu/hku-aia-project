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
    <div className="auth-row">
      <input
        id="auth-key"
        className="auth-input"
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
};

export default AuthKeyInput;
