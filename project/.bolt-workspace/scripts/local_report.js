// .bolt-workspace/scripts/local_report.js

async function runReport() {
  let healthPass = false;
  let chatPass = false;
  let historyPass = false;
  let versionPass = false;
  let storagePass = false;
  let modePass = false;

  try {
    // a) Health check
    const healthResponse = await fetch('http://localhost:3000/healthz');
    const healthText = await healthResponse.text();
    console.log(`HEALTHZ: ${healthText}`);
    healthPass = healthResponse.ok && healthText.startsWith('ok');
  } catch (error) {
    console.log(`HEALTHZ: ERROR - ${error.message}`);
  }

  try {
    // b) Chat with usage check
    const chatBody = JSON.stringify({
      question: "usage check", 
      session_identifier: "report-123"
    });
    const chatResponse = await fetch('http://localhost:3000/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: chatBody
    });
    const chatData = await chatResponse.json();
    
    if (chatResponse.ok && chatData.answer) {
      const replyExcerpt = chatData.answer.substring(0, 120);
      console.log(`CHAT: ${replyExcerpt}`);
      
      if (chatData.usage) {
        console.log(`USAGE: tokens_in=${chatData.usage.tokens_in}, tokens_out=${chatData.usage.tokens_out}`);
      }
      
      if (chatData.mode) {
        console.log(`MODE: ${chatData.mode}`);
      }
      
      chatPass = true;
    } else {
      console.log(`CHAT: ERROR - ${JSON.stringify(chatData)}`);
    }
  } catch (error) {
    console.log(`CHAT: ERROR - ${error.message}`);
  }

  try {
    // c) History check
    const historyResponse = await fetch('http://localhost:3000/api/history?session_identifier=report-123');
    const historyData = await historyResponse.json();
    
    if (historyResponse.ok && typeof historyData.count === 'number') {
      console.log(`HISTORY: count=${historyData.count}`);
      historyPass = true;
    } else {
      console.log(`HISTORY: ERROR - ${JSON.stringify(historyData)}`);
    }
  } catch (error) {
    console.log(`HISTORY: ERROR - ${error.message}`);
  }

  try {
    // d) Storage proof via server endpoint
    const storageResponse = await fetch('http://localhost:3000/proof/messages?limit=5');
    const storageData = await storageResponse.json();
    
    if (storageResponse.ok && storageData.ok) {
      console.log(`STORAGE: ${JSON.stringify(storageData.rows)}`);
      storagePass = true;
    } else {
      console.log(`STORAGE: ERROR - ${JSON.stringify(storageData)}`);
    }
  } catch (error) {
    console.log(`STORAGE: ERROR - ${error.message}`);
  }

  try {
    // e) Mode check
    const modeResponse = await fetch('http://localhost:3000/mode');
    const modeData = await modeResponse.json();
    
    if (modeResponse.ok) {
      console.log(`MODE: openai=${modeData.openai}`);
      modePass = true;
    } else {
      console.log(`MODE: ERROR - ${JSON.stringify(modeData)}`);
    }
  } catch (error) {
    console.log(`MODE: ERROR - ${error.message}`);
  }

  try {
    // f) Version check
    const versionResponse = await fetch('http://localhost:3000/version');
    const versionData = await versionResponse.json();
    
    if (versionResponse.ok) {
      console.log(`VERSION: ${JSON.stringify(versionData)}`);
      versionPass = true;
    } else {
      console.log(`VERSION: ERROR - ${JSON.stringify(versionData)}`);
    }
  } catch (error) {
    console.log(`VERSION: ERROR - ${error.message}`);
  }

  // Summary
  const formatStatus = (pass) => pass ? 'PASS' : 'FAIL';
  console.log(`SUMMARY → health ${formatStatus(healthPass)}, chat ${formatStatus(chatPass)}, history ${formatStatus(historyPass)}, storage ${formatStatus(storagePass)}, version ${formatStatus(versionPass)}`);
}

runReport().catch(console.error);