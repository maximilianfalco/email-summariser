"use client";

import { useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Email {
  id: string;
  subject: string;
  from: string;
  date: string;
  snippet: string;
  body: string;
}

export default function Dashboard() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [summary, setSummary] = useState("");
  const [slackStatus, setSlackStatus] = useState("");
  const [loading, setLoading] = useState({
    emails: false,
    summary: false,
    slack: false,
  });
  const [error, setError] = useState("");

  async function fetchEmails() {
    setLoading((l) => ({ ...l, emails: true }));
    setError("");
    try {
      const res = await fetch(`${API}/api/emails`);
      if (!res.ok) throw new Error((await res.json()).detail);
      const data = await res.json();
      setEmails(data.emails);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to fetch emails");
    } finally {
      setLoading((l) => ({ ...l, emails: false }));
    }
  }

  async function summariseEmails() {
    setLoading((l) => ({ ...l, summary: true }));
    setError("");
    try {
      const res = await fetch(`${API}/api/summarise`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ emails }),
      });
      if (!res.ok) throw new Error((await res.json()).detail);
      const data = await res.json();
      setSummary(data.summary);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to summarise");
    } finally {
      setLoading((l) => ({ ...l, summary: false }));
    }
  }

  async function sendToSlack() {
    setLoading((l) => ({ ...l, slack: true }));
    setError("");
    try {
      const res = await fetch(`${API}/api/send-slack`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ summary }),
      });
      if (!res.ok) throw new Error((await res.json()).detail);
      setSlackStatus("Sent!");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send to Slack");
    } finally {
      setLoading((l) => ({ ...l, slack: false }));
    }
  }

  return (
    <main className="max-w-4xl mx-auto p-8 font-[family-name:var(--font-geist-sans)]">
      <h1 className="text-2xl font-bold mb-6">
        Email Summariser — Debug Dashboard
      </h1>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {/* Step 1: Fetch Emails */}
      <section className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <h2 className="text-lg font-semibold">1. Fetch Unread Emails</h2>
          <button
            onClick={fetchEmails}
            disabled={loading.emails}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
          >
            {loading.emails ? "Fetching..." : "Fetch Emails"}
          </button>
          {emails.length > 0 && (
            <span className="text-sm text-gray-400">
              {emails.length} email(s)
            </span>
          )}
        </div>
        {emails.length > 0 && (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {emails.map((email) => (
              <details
                key={email.id}
                className="border border-gray-700 rounded p-3"
              >
                <summary className="cursor-pointer">
                  <span className="font-medium">{email.subject}</span>
                  <span className="text-gray-400 text-sm ml-2">
                    from {email.from}
                  </span>
                </summary>
                <div className="mt-2 text-sm text-gray-300">
                  <p className="text-gray-500 mb-1">{email.date}</p>
                  <pre className="whitespace-pre-wrap font-[family-name:var(--font-geist-mono)] text-xs bg-gray-900 p-3 rounded">
                    {email.body || email.snippet}
                  </pre>
                </div>
              </details>
            ))}
          </div>
        )}
      </section>

      {/* Step 2: Summarise */}
      <section className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <h2 className="text-lg font-semibold">2. Summarise</h2>
          <button
            onClick={summariseEmails}
            disabled={loading.summary || emails.length === 0}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 text-sm"
          >
            {loading.summary ? "Summarising..." : "Summarise"}
          </button>
        </div>
        {summary && (
          <pre className="whitespace-pre-wrap font-[family-name:var(--font-geist-mono)] text-sm bg-gray-900 border border-gray-700 p-4 rounded">
            {summary}
          </pre>
        )}
      </section>

      {/* Step 3: Send to Slack */}
      <section className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <h2 className="text-lg font-semibold">3. Send to Slack</h2>
          <button
            onClick={sendToSlack}
            disabled={loading.slack || !summary}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 text-sm"
          >
            {loading.slack ? "Sending..." : "Send to Slack"}
          </button>
          {slackStatus && (
            <span className="text-sm text-green-400">{slackStatus}</span>
          )}
        </div>
      </section>
    </main>
  );
}
