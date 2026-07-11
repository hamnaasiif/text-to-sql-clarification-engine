CREATE TABLE conversation_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_question TEXT NOT NULL,
    ambiguities JSONB NOT NULL,
    current_index INTEGER NOT NULL DEFAULT 0,
    resolutions JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);