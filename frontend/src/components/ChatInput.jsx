import { useState } from 'react';
import './ChatInput.css';

export default function ChatInput({ onSend, disabled, isClarifying }) {
  const [value, setValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue('');
  };

  return (
    <form className="chat-input-bar" onSubmit={handleSubmit}>
      <input
        id="chat-input"
        className="chat-input"
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={
          isClarifying
            ? 'Type your answer or pick an option above…'
            : 'Ask a question about your data…'
        }
        disabled={disabled}
        autoComplete="off"
      />
      <button
        id="chat-send"
        className="chat-send"
        type="submit"
        disabled={disabled || !value.trim()}
        aria-label="Send"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <line x1="22" y1="2" x2="11" y2="13" />
          <polygon points="22 2 15 22 11 13 2 9 22 2" />
        </svg>
      </button>
    </form>
  );
}
