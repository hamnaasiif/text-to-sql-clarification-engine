import { useState } from 'react';
import './ChatMessage.css';

export default function ChatMessage({ role, content, sql, options, onOptionClick, isError, onStartOver }) {
  const [sqlExpanded, setSqlExpanded] = useState(false);

  return (
    <div className={`msg-row msg-row--${role}${isError ? ' msg-row--error' : ''}`}>
      <div className={`msg-bubble msg-bubble--${role}${isError ? ' msg-bubble--error' : ''}`}>
        {/* Message content */}
        <p className="msg-text">{content}</p>

        {/* Collapsible SQL block */}
        {sql && (
          <div className="msg-sql">
            <button
              className="msg-sql-toggle"
              onClick={() => setSqlExpanded(!sqlExpanded)}
              aria-expanded={sqlExpanded}
            >
              <svg
                className={`msg-sql-chevron${sqlExpanded ? ' msg-sql-chevron--open' : ''}`}
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="9 18 15 12 9 6" />
              </svg>
              View generated SQL
            </button>
            {sqlExpanded && (
              <pre className="msg-sql-code"><code>{sql}</code></pre>
            )}
          </div>
        )}

        {/* Clarification option buttons */}
        {options && options.length > 0 && (
          <div className="msg-options">
            {options.map((opt, i) => (
              <button
                key={i}
                className="msg-option-btn"
                onClick={() => onOptionClick(opt)}
              >
                {opt}
              </button>
            ))}
          </div>
        )}

        {/* Error: start over */}
        {isError && onStartOver && (
          <button className="msg-start-over" onClick={onStartOver}>
            Start new conversation
          </button>
        )}
      </div>
    </div>
  );
}
