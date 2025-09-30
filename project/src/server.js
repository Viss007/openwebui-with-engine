import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs/promises';
import OpenAI from "openai";
import { createClient } from '@supabase/supabase-js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const port = process.env.PORT || 3000;
const oi = process.env.OPENAI_API_KEY ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY }) : null;
const openaiActive = !!process.env.OPENAI_API_KEY;

// Initialize Supabase client if credentials are available
const supabase = (process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY) 
  ? createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY)
  : null;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging middleware
const logReq = (req,res,next) => {
  const t0 = Date.now();
  res.on("finish", () => {
    const ms = Date.now() - t0;
    const sid = req.body?.session_identifier ?? req.query?.session_identifier ?? "<none>";
    console.log(JSON.stringify({ t:new Date().toISOString(), route:req.method+" "+req.path, session_identifier:sid, ms }));
  });
  next();
};
app.use(logReq);

app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "content-type");
  next();
});
app.use(express.static('public'));

// In-memory storage for chat history
const chatHistory = new Map();

// Health check endpoint
app.get('/healthz', (req, res) => {
  res.status(200).send('ok');
});

// Version endpoint
app.get('/version', (req, res) => {
  try {
    const response = {
      version: "v0.1-local-pass",
      time: new Date().toISOString()
    };
    res.status(200).json(response);
  } catch (error) {
    console.error('Version endpoint error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Mode endpoint
app.get('/mode', (req, res) => {
  res.json({ openai: openaiActive });
});

// Storage proof endpoint
app.get('/proof/messages', async (req, res) => {
  try {
    if (!supabase) {
      return res.status(500).json({ ok: false, error: "supabase_not_configured" });
    }
    
    const limit = Math.min(parseInt(req.query.limit ?? "5", 10), 20);
    const { data, error } = await supabase
      .from("messages")
      .select("session_identifier,role,message_text,created_time")
      .order("created_time", { ascending: false })
      .limit(limit);
      
    if (error) {
      return res.status(500).json({ ok: false, error: "db_error", detail: error.message });
    }
    
    return res.json({ ok: true, rows: data ?? [] });
  } catch (e) {
    return res.status(500).json({ ok: false, error: "internal_error", detail: (e && e.message) || String(e) });
  }
});

// Chat endpoint
app.post('/api/chat', async (req, res) => {
  try {
    const { question, session_identifier } = req.body;
    
    if (!question || !session_identifier) {
      return res.status(400).json({ 
        error: 'Missing required fields: question and session_identifier' 
      });
    }

    // Get or create session history
    if (!chatHistory.has(session_identifier)) {
      chatHistory.set(session_identifier, []);
    }
    
    const sessionHistory = chatHistory.get(session_identifier);
    
    // decide reply: OpenAI if key is present, else fallback
    let reply = `Hello! You asked: "${question}"`;
    let usage = undefined;
    if (oi) {
      try {
        const sys = "You are a concise assistant. Keep answers short and helpful.";
        const msg = [
          { role: "system", content: sys },
          { role: "user", content: question }
        ];
        const start = Date.now();
        const r = await oi.chat.completions.create({
          model: process.env.OPENAI_MODEL || "gpt-4o-mini",
          messages: msg,
          max_tokens: 200,
          temperature: 0.7
        });
        reply = r.choices?.[0]?.message?.content?.trim() || reply;
        // Extract usage information if available
        if (r?.usage) {
          usage = { 
            tokens_in: r.usage.prompt_tokens, 
            tokens_out: r.usage.completion_tokens 
          };
        }
        // optional usage log (if returned)
        const tokens_in = r.usage?.prompt_tokens ?? null;
        const tokens_out = r.usage?.completion_tokens ?? null;
        const ms = Date.now() - start;
        console.log(JSON.stringify({ t:new Date().toISOString(), route:"OPENAI chat", session_identifier, ms, tokens_in, tokens_out }));
      } catch (e) {
        console.error("OPENAI ERROR:", e?.message || e);
        // fall back to safe echo
      }
    }
    
    const response = {
      answer: reply,
      timestamp: new Date().toISOString(),
      session_identifier,
      mode: (oi ? "openai" : "echo"),
      ...(usage && { usage })
    };
    
    // Store the conversation
    sessionHistory.push({
      question,
      answer: reply,
      timestamp: response.timestamp
    });
    
    res.json(response);
  } catch (error) {
    console.error('Chat endpoint error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// History endpoint
app.get('/api/history', (req, res) => {
  try {
    const { session_identifier } = req.query;
    
    if (!session_identifier) {
      return res.status(400).json({ 
        error: 'Missing required query parameter: session_identifier' 
      });
    }
    
    const history = chatHistory.get(session_identifier) || [];
    
    res.json({
      session_identifier,
      history,
      count: history.length
    });
  } catch (error) {
    console.error('History endpoint error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});