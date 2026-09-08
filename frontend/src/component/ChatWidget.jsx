import { useState, useRef, useEffect } from "react";
import { Home, MessageCircle, Settings, Send, X, Sparkles } from "lucide-react";
import mascot from "/cha_user-serv01.png";

// ── 백엔드 설정 ──────────────────────────────────────────────
// .env 에 VITE_API_URL 을 두면 그것을 쓰고, 없으면 로컬 기본값 사용
const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export default function ChatWidget() {
  const [open, setOpen] = useState(true);
  const [tab, setTab] = useState("home");
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: "안녕하세요 👋 식품공전 안내 챗봇입니다.\n궁금한 기준·규격을 자유롭게 물어보세요. ^*^/",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, loading]);

  useEffect(() => {
    const textarea = inputRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
  }, [input]);

  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;

    setMessages((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: q, thread_id :'default' }),
      });

      if (!res.ok) {
        throw new Error(`서버 오류 (${res.status})`);
      }

      const data = await res.json();
      setMessages((m) => [
        ...m,
        {
          role: "bot",
          text: data.answer ?? "답변을 받지 못했어요."
        },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "bot", 
          text:
            "죄송해요, 답변을 가져오지 못했어요. 잠시 후 다시 시도해 주세요.\n(" +
            err.message +
            ")",
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.stage}>
      {open && (
        <div style={styles.panel}>
          {/* 헤더 */}
          <div style={styles.header}>
            <div style={styles.avatar}>
              <Sparkles size={18} color="#fff" />
            </div>
            <div>
              <div style={styles.headerTitle}>식품공전 도우미</div>
              <div style={styles.headerSub}>보통 몇 초 안에 응답해요</div>
            </div>
          </div>

          {tab === "home" && (
            <>
              {/* 메시지 영역 */}
              <div ref={scrollRef} style={styles.messages}>
                {messages.map((m, i) => (
                  <div key={i}>
                    <div
                      style={{
                        ...styles.bubbleRow,
                        justifyContent:
                          m.role === "user" ? "flex-end" : "flex-start",
                      }}
                    >
                      <div
                        style={{
                          ...styles.bubble,
                          ...(m.role === "user"
                            ? styles.bubbleUser
                            : styles.bubbleBot),
                          ...(m.role === "bot" && hasMarkdownTable(m.text)
                            ? styles.bubbleWithTable
                            : {}),
                          ...(m.isError ? styles.bubbleError : {}),
                        }}
                      >
                        {m.role === "bot" ? <MessageContent text={m.text} /> : m.text}
                      </div>
                    </div>

                    {/* 출처 표시 (있을 때만) */}
                    {m.sources && m.sources.length > 0 && (
                      <div style={styles.sources}>
                        {m.sources.map((s, j) => (
                          <span key={j} style={styles.sourceChip}>
                            {s.source || `출처 ${j + 1}`}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}

                {loading && (
                  <div style={{ ...styles.bubbleRow, justifyContent: "flex-start" }}>
                    <div style={{ ...styles.bubble, ...styles.bubbleBot }}>
                      <span style={styles.dot} />
                      <span style={{ ...styles.dot, animationDelay: "0.15s" }} />
                      <span style={{ ...styles.dot, animationDelay: "0.3s" }} />
                    </div>
                  </div>
                )}
              </div>

              {/* 입력창 */}
              <div style={styles.inputRow}>
                <textarea
                  ref={inputRef}
                  className="chat-input"
                  style={styles.input}
                  value={input}
                  placeholder="메시지를 입력하세요…"
                  disabled={loading}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      send();
                    }
                  }}
                  rows={1}
                />
                <button
                  style={{ ...styles.sendBtn, opacity: loading ? 0.5 : 1 }}
                  onClick={send}
                  disabled={loading}
                  aria-label="전송"
                >
                  <Send size={18} color="#fff" />
                </button>
              </div>
            </>
          )}

          {tab === "chat" && (
            <div style={styles.placeholder}>
              <MessageCircle size={40} color="#5b6cff" />
              <p style={styles.phText}>지난 대화 목록이 여기에 표시됩니다.</p>
            </div>
          )}
          {tab === "settings" && (
            <div style={styles.placeholder}>
              <Settings size={40} color="#5b6cff" />
              <p style={styles.phText}>알림·언어 등 설정이 여기에 표시됩니다.</p>
            </div>
          )}

          {/* 하단 탭 */}
          <div style={styles.tabbar}>
            <TabButton icon={Home} label="홈" active={tab === "home"} onClick={() => setTab("home")} />
            <TabButton icon={MessageCircle} label="대화" active={tab === "chat"} onClick={() => setTab("chat")} />
            <TabButton icon={Settings} label="설정" active={tab === "settings"} onClick={() => setTab("settings")} />
          </div>
        </div>
      )}

      {/* 플로팅 버튼 */}
      <button style={styles.fab} onClick={() => setOpen((o) => !o)} aria-label="챗봇 열기/닫기">
        {open ? (
          <X size={24} color="#fff" />
        ) : (
          <img src={mascot} alt="챗봇" style={{ width: 40, height: 40 }} />
        )}
      </button>

      <style>{`
        @keyframes blink { 0%,80%,100%{opacity:.3} 40%{opacity:1} }
        .chat-input { scrollbar-width: none; -ms-overflow-style: none; }
        .chat-input::-webkit-scrollbar { display: none; }
      `}</style>
    </div>
  );
}

function TabButton({ icon: Icon, label, active, onClick }) {
  return (
    <button style={styles.tabBtn} onClick={onClick}>
      <Icon size={20} color={active ? "#5b6cff" : "#8a8f98"} />
      <span style={{ ...styles.tabLabel, color: active ? "#5b6cff" : "#8a8f98" }}>
        {label}
      </span>
    </button>
  );
}

function hasMarkdownTable(text = "") {
  const lines = text.split("\n");
  return lines.some((line, index) =>
    index > 0 && isTableDivider(line) && lines[index - 1].includes("|"),
  );
}

function isTableDivider(line) {
  return /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$/.test(line);
}

function tableCells(line) {
  return line
    .trim()
    .replace(/^\|/, "")
    .replace(/\|$/, "")
    .split("|")
    .map((cell) => cell.trim());
}

function MessageContent({ text = "" }) {
  const lines = text.split("\n");
  const content = [];
  let paragraph = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    content.push(
      <div key={`text-${content.length}`} style={styles.answerText}>
        {paragraph.join("\n")}
      </div>,
    );
    paragraph = [];
  };

  for (let i = 0; i < lines.length; i += 1) {
    if (i + 1 < lines.length && lines[i].includes("|") && isTableDivider(lines[i + 1])) {
      flushParagraph();
      const headers = tableCells(lines[i]);
      const rows = [];
      i += 2;

      while (i < lines.length && lines[i].includes("|") && lines[i].trim()) {
        rows.push(tableCells(lines[i]));
        i += 1;
      }
      i -= 1;

      content.push(
        <div key={`table-${content.length}`} style={styles.tableScroll}>
          <table style={styles.table}>
            <thead>
              <tr>
                {headers.map((header, index) => (
                  <th key={index} style={styles.tableHeader}>{header}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, rowIndex) => (
                <tr key={rowIndex} style={rowIndex % 2 ? styles.tableAltRow : undefined}>
                  {headers.map((_, cellIndex) => (
                    <td key={cellIndex} style={styles.tableCell}>{row[cellIndex] ?? ""}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
    } else {
      paragraph.push(lines[i]);
    }
  }

  flushParagraph();
  return content;
}

const styles = {
  stage: {
    position: "relative",
    width: "100%",
    minHeight: "100vh",
    background: "linear-gradient(160deg,#e9ecf5,#d3d8ea)",
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "flex-end",
    padding: 24,
    boxSizing: "border-box",
    fontFamily: "'Pretendard','Apple SD Gothic Neo',system-ui,sans-serif",
  },
  panel: {
    position: "absolute",
    bottom: 96,
    right: 24,
    width: 460,
    height: 680,
    background: "#26282e",
    borderRadius: 20,
    boxShadow: "0 20px 60px rgba(0,0,0,.35)",
    display: "flex",
    flexDirection: "column",
    overflow: "auto",
    resize:"both"
  },
  header: {
    display: "flex",
    alignItems: "center",
    gap: 12,
    padding: "18px 18px 14px",
  },
  avatar: {
    width: 40,
    height: 40,
    borderRadius: 12,
    background: "linear-gradient(135deg,#5b6cff,#8a5bff)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  headerTitle: { color: "#fff", fontSize: 16, fontWeight: 700 },
  headerSub: { color: "#9aa0ab", fontSize: 12, marginTop: 2 },
  messages: {
    flex: 1,
    overflowY: "auto",
    padding: "8px 14px",
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },
  bubbleRow: { display: "flex", width: "100%" },
  bubble: {
    maxWidth: "78%",
    padding: "10px 14px",
    borderRadius: 16,
    fontSize: 14,
    lineHeight: 1.5,
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  bubbleBot: {
    background: "#34373f",
    color: "#e8eaed",
    borderTopLeftRadius: 4,
    textAlign: "left",
  },
  bubbleWithTable: { maxWidth: "94%", width: "94%" },
  bubbleUser: {
    background: "linear-gradient(135deg,#5b6cff,#6a5bff)",
    color: "#fff",
    borderTopRightRadius: 4,
  },
  bubbleError: { background: "#4a2b2b", color: "#ffd5d5" },
  answerText: { whiteSpace: "pre-wrap" },
  tableScroll: {
    width: "100%",
    overflowX: "auto",
    marginTop: 10,
    border: "1px solid #50545f",
    borderRadius: 10,
  },
  table: {
    width: "100%",
    minWidth: 360,
    borderCollapse: "collapse",
    background: "#2b2e35",
    fontSize: 13,
  },
  tableHeader: {
    padding: "11px 12px",
    background: "linear-gradient(135deg,#5b6cff,#755bff)",
    color: "#fff",
    fontWeight: 700,
    textAlign: "left",
    whiteSpace: "nowrap",
  },
  tableCell: {
    padding: "10px 12px",
    borderTop: "1px solid #464a54",
    color: "#e8eaed",
    textAlign: "left",
    verticalAlign: "top",
  },
  tableAltRow: { background: "#32353d" },
  sources: {
    display: "flex",
    flexWrap: "wrap",
    gap: 6,
    margin: "6px 4px 0",
  },
  sourceChip: {
    fontSize: 11,
    color: "#9aa0ab",
    background: "#2c2f36",
    border: "1px solid #3a3d45",
    borderRadius: 8,
    padding: "3px 8px",
  },
  dot: {
    display: "inline-block",
    width: 6,
    height: 6,
    margin: "0 2px",
    borderRadius: "50%",
    background: "#9aa0ab",
    animation: "blink 1.2s infinite",
  },
  inputRow: {
    display: "flex",
    gap: 8,
    padding: 12,
    borderTop: "1px solid #34373f",
  },
  input: {
    flex: 1,
    background: "#1f2126",
    border: "1px solid #3a3d45",
    borderRadius: 12,
    padding: "10px 14px",
    color: "#e8eaed",
    fontSize: 14,
    lineHeight: 1.5,
    outline: "none",
    resize: "none",
    overflowY: "auto",
    minHeight: 42,
    maxHeight: 120,
    boxSizing: "border-box",
    fontFamily: "inherit",
  },
  sendBtn: {
    width: 42,
    height: 42,
    borderRadius: 12,
    border: "none",
    cursor: "pointer",
    background: "linear-gradient(135deg,#5b6cff,#6a5bff)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexShrink: 0,
  },
  placeholder: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: 12,
    padding: 24,
  },
  phText: { color: "#9aa0ab", fontSize: 14, textAlign: "center" },
  tabbar: {
    display: "flex",
    borderTop: "1px solid #34373f",
    background: "#26282e",
  },
  tabBtn: {
    flex: 1,
    background: "none",
    border: "none",
    cursor: "pointer",
    padding: "10px 0 12px",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: 4,
  },
  tabLabel: { fontSize: 11, fontWeight: 600 },
  fab: {
    position: "absolute",
    bottom: 24,
    right: 24,
    width: 56,
    height: 56,
    borderRadius: "50%",
    border: "none",
    cursor: "pointer",
    background: "linear-gradient(135deg,#5b6cff,#6a5bff)",
    boxShadow: "0 10px 30px rgba(91,108,255,.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
};
