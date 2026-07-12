const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

/**
 * POST /ask — start a new question.
 * @param {string} question
 * @returns {Promise<Object>} response body (clarification_needed | answered)
 */
export async function askQuestion(question) {
  const res = await fetch(`${API_URL}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    throw new Error(`Server error (${res.status}): ${res.statusText}`);
  }

  return res.json();
}

/**
 * POST /answer — submit a clarification answer.
 * @param {string} sessionId
 * @param {string} answer
 * @returns {Promise<Object>} response body (clarification_needed | answered | error)
 */
export async function submitAnswer(sessionId, answer) {
  const res = await fetch(`${API_URL}/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, answer }),
  });

  if (!res.ok) {
    throw new Error(`Server error (${res.status}): ${res.statusText}`);
  }

  return res.json();
}

/**
 * GET /dataset-summary — fetch dataset statistics.
 * @returns {Promise<Object>} dataset summary
 */
export async function fetchDatasetSummary() {
  const res = await fetch(`${API_URL}/dataset-summary`);

  if (!res.ok) {
    throw new Error(`Server error (${res.status}): ${res.statusText}`);
  }

  return res.json();
}

