import { useState, useRef, useEffect, useCallback } from 'react';
import { askQuestion, submitAnswer } from './api';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';
import TypingIndicator from './components/TypingIndicator';
import DataInfoPanel from './components/DataInfoPanel';
import './App.css';

const EXAMPLE_QUESTIONS = [
  "Show me the best customer",
  "What were last month's sales?",
  "Top products by revenue",
  "Which products belong to Electronics?",
  "How many pending orders do we have?",
  "Show total payments by payment method",
  "Which customers registered recently?",
  "List all completed orders from last week",
];

export default function App() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isClarifying, setIsClarifying] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change or loading state changes
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const resetConversation = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    setIsLoading(false);
    setIsClarifying(false);
  }, []);

  const handleError = useCallback((error) => {
    const errorMessage =
      error?.message || 'Something went wrong. Please try again.';

    setMessages((prev) => [
      ...prev,
      { role: 'assistant', content: errorMessage, isError: true },
    ]);
    setIsLoading(false);
    setIsClarifying(false);
    setSessionId(null);
  }, []);

  const processResponse = useCallback(
    (data) => {
      if (data.status === 'error') {
        // Backend-level error (e.g., session not found)
        handleError({ message: data.message });
        return;
      }

      if (data.status === 'clarification_needed') {
        setSessionId(data.session_id);
        setIsClarifying(true);
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: data.question,
            options: data.options,
          },
        ]);
      } else if (data.status === 'answered') {
        setSessionId(null);
        setIsClarifying(false);
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: data.answer,
            sql: data.sql,
          },
        ]);
      }
    },
    [handleError]
  );

  const handleSend = useCallback(
    async (text) => {
      // Add user message to chat
      setMessages((prev) => [...prev, { role: 'user', content: text }]);
      setIsLoading(true);

      try {
        let data;
        if (isClarifying && sessionId) {
          // User is answering a clarification (typed or clicked)
          data = await submitAnswer(sessionId, text);
        } else {
          // New question
          data = await askQuestion(text);
        }
        processResponse(data);
      } catch (err) {
        handleError(err);
      } finally {
        setIsLoading(false);
      }
    },
    [isClarifying, sessionId, processResponse, handleError]
  );

  const handleOptionClick = useCallback(
    (option) => {
      // Clicking an option is the same as typing it
      handleSend(option);
    },
    [handleSend]
  );

  const hasMessages = messages.length > 0;

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-title">
          <img src="/favicon.svg" alt="" className="app-logo" />
          <h1>SQL Clarification Engine</h1>
        </div>
        {hasMessages && (
          <button
            id="btn-new-conversation"
            className="btn-reset"
            onClick={resetConversation}
          >
            New conversation
          </button>
        )}
      </header>

      <div className="chat-messages" role="log" aria-live="polite">
        {!hasMessages && !isLoading && (
          <div className="welcome">
            <div className="welcome-icon">💬</div>
            <h2>Ask anything about your data</h2>
            <p>
              I'll convert your natural language questions into SQL. If your
              question is ambiguous, I'll ask clarifying questions first to make
              sure I get it right.
            </p>

            <DataInfoPanel />

            <div className="welcome-examples-section">
              <span className="examples-title">Try asking an example question:</span>
              <div className="welcome-hint">
                {EXAMPLE_QUESTIONS.map((q, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="example-chip"
                    onClick={() => handleSend(q)}
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatMessage
            key={i}
            role={msg.role}
            content={msg.content}
            sql={msg.sql}
            options={
              // Only show options on the LAST assistant message with options
              // (disable old option buttons after they've been used)
              msg.options && i === messages.length - 1 ? msg.options : undefined
            }
            onOptionClick={handleOptionClick}
            isError={msg.isError}
            onStartOver={msg.isError ? resetConversation : undefined}
          />
        ))}

        {isLoading && <TypingIndicator />}

        <div ref={messagesEndRef} />
      </div>

      <ChatInput
        onSend={handleSend}
        disabled={isLoading}
        isClarifying={isClarifying}
      />
    </div>
  );
}
