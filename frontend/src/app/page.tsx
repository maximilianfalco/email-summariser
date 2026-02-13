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

const MOCK_EMAILS: Email[] = [
  {
    id: "mock-1",
    subject: "Q1 Budget Review",
    from: "sarah.chen@acme.com",
    date: "Thu, 13 Feb 2026 08:30:00 +0000",
    snippet: "Please review the attached Q1 budget proposal...",
    body: "Hi team,\n\nPlease review the attached Q1 budget proposal before our meeting on Friday. Key changes include a 15% increase in engineering headcount and a new allocation for cloud infrastructure.\n\nLet me know if you have questions.\n\nBest,\nSarah",
  },
  {
    id: "mock-2",
    subject: "Re: API Migration Timeline",
    from: "james.miller@acme.com",
    date: "Thu, 13 Feb 2026 09:15:00 +0000",
    snippet: "The migration is on track for next week...",
    body: "Hey,\n\nQuick update on the API migration — we're on track for the v2 cutover next Wednesday. The staging environment has been running stable for 3 days now with zero errors.\n\nI'll send the runbook by EOD tomorrow.\n\nJames",
  },
  {
    id: "mock-3",
    subject: "Lunch tomorrow?",
    from: "alex.wong@gmail.com",
    date: "Thu, 13 Feb 2026 10:00:00 +0000",
    snippet: "Are you free for lunch tomorrow?",
    body: "Hey! Are you free for lunch tomorrow around 12:30? There's a new ramen place on King St I've been wanting to try.\n\nLet me know!\nAlex",
  },
  {
    id: "mock-4",
    subject: "Your invoice from Vercel",
    from: "billing@vercel.com",
    date: "Thu, 13 Feb 2026 06:00:00 +0000",
    snippet: "Your February invoice is ready...",
    body: "Hi Maximilian,\n\nYour invoice for February 2026 is ready.\n\nAmount: $20.00\nPlan: Pro\nPeriod: Feb 1 - Feb 28, 2026\n\nView your invoice: https://vercel.com/billing\n\nThanks,\nVercel Billing",
  },
];

const MOCK_SUMMARY = `**Daily Email Briefing — Feb 13, 2026**

**Work**
- **Sarah Chen** — Q1 Budget Review: Requesting review of Q1 budget proposal with 15% engineering headcount increase and new cloud infrastructure allocation. Meeting on Friday.
- **James Miller** — API Migration Timeline: v2 API cutover on track for next Wednesday. Staging stable for 3 days. Runbook coming tomorrow.

**Personal**
- **Alex Wong** — Lunch invitation for tomorrow at 12:30, new ramen place on King St.

**Billing**
- **Vercel** — February invoice ready, $20.00 for Pro plan.

**Action Items**
1. Review Q1 budget proposal before Friday meeting
2. Confirm lunch with Alex
3. Check Vercel invoice`;

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

export default function Dashboard() {
  const [mockMode, setMockMode] = useState(false);
  const [emails, setEmails] = useState<Email[]>([]);
  const [summary, setSummary] = useState("");
  const [slackStatus, setSlackStatus] = useState("");
  const [pingStatus, setPingStatus] = useState("");
  const [loading, setLoading] = useState({
    emails: false,
    summary: false,
    slack: false,
    ping: false,
  });
  const [error, setError] = useState("");

  async function fetchEmails() {
    setLoading((l) => ({ ...l, emails: true }));
    setError("");
    try {
      if (mockMode) {
        await sleep(600);
        setEmails(MOCK_EMAILS);
      } else {
        const res = await fetch(`${API}/api/emails`);
        if (!res.ok) throw new Error((await res.json()).detail);
        const data = await res.json();
        setEmails(data.emails);
      }
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
      if (mockMode) {
        await sleep(1200);
        setSummary(MOCK_SUMMARY);
      } else {
        const res = await fetch(`${API}/api/summarise`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ emails }),
        });
        if (!res.ok) throw new Error((await res.json()).detail);
        const data = await res.json();
        setSummary(data.summary);
      }
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
      if (mockMode) {
        await sleep(400);
        setSlackStatus("Sent! (mock)");
      } else {
        const res = await fetch(`${API}/api/send-slack`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ summary }),
        });
        if (!res.ok) throw new Error((await res.json()).detail);
        setSlackStatus("Sent!");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send to Slack");
    } finally {
      setLoading((l) => ({ ...l, slack: false }));
    }
  }

  async function pingSlack() {
    setLoading((l) => ({ ...l, ping: true }));
    setError("");
    try {
      if (mockMode) {
        await sleep(400);
        setPingStatus("Sent! (mock)");
      } else {
        const res = await fetch(`${API}/api/ping-slack`, { method: "POST" });
        if (!res.ok) throw new Error((await res.json()).detail);
        setPingStatus("Sent!");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to ping Slack");
    } finally {
      setLoading((l) => ({ ...l, ping: false }));
    }
  }

  function toggleMockMode() {
    setMockMode((m) => !m);
    setEmails([]);
    setSummary("");
    setSlackStatus("");
    setPingStatus("");
    setError("");
  }

  return (
    <main className="max-w-4xl mx-auto p-8 font-(family-name:--font-geist-sans)">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">
          Email Summariser — Debug Dashboard
        </h1>
        <button
          onClick={toggleMockMode}
          className={`px-3 py-1.5 rounded text-sm font-medium border transition-colors ${
            mockMode
              ? "bg-yellow-500/10 border-yellow-500/30 text-yellow-400"
              : "bg-gray-800 border-gray-700 text-gray-400"
          }`}
        >
          {mockMode ? "Mock Mode" : "Live Mode"}
        </button>
      </div>

      {mockMode && (
        <div className="bg-yellow-500/10 border border-yellow-500/30 text-yellow-400 px-4 py-3 rounded mb-6 text-sm">
          Mock mode — using fake data, no API calls or backend required.
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

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
                  <pre className="whitespace-pre-wrap font-(family-name:--font-geist-mono) text-xs bg-gray-900 text-gray-200 p-3 rounded">
                    {email.body || email.snippet}
                  </pre>
                </div>
              </details>
            ))}
          </div>
        )}
      </section>

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
          <pre className="whitespace-pre-wrap font-(family-name:--font-geist-mono) text-sm bg-gray-900 text-gray-200 border border-gray-700 p-4 rounded">
            {summary}
          </pre>
        )}
      </section>

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

      <section className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <h2 className="text-lg font-semibold">Ping Slack</h2>
          <button
            onClick={pingSlack}
            disabled={loading.ping}
            className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50 text-sm"
          >
            {loading.ping ? "Pinging..." : "Ping"}
          </button>
          {pingStatus && (
            <span className="text-sm text-green-400">{pingStatus}</span>
          )}
        </div>
      </section>
    </main>
  );
}
