// .bolt-workspace/scripts/checks.js

async function httpGet(url) {
  const response = await fetch(url);
  return await response.text();
}

async function postChat() {
  const body = JSON.stringify({ question: "hello", session_identifier: "bolt-123" });
  const response = await fetch("http://localhost:3000/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: body
  });
  return await response.json();
}

async function getHist() {
  const response = await fetch("http://localhost:3000/api/history?session_identifier=bolt-123");
  return await response.json();
}

(async () => {
  try {
    const h = await httpGet("http://localhost:3000/healthz");
    console.log("HEALTHZ:", h);
    const chat = await postChat();
    console.log("CHAT:", JSON.stringify(chat));
    const hist = await getHist();
    console.log("HISTORY:", JSON.stringify(hist));
    process.exit(0);
  } catch (e) {
    console.error("CHECKS FAILED:", e.message || e);
    process.exit(1);
  }
})();