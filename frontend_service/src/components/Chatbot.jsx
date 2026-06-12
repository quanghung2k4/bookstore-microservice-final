import { useState, useRef, useEffect } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';

const QUICK_REPLIES = [
  { label: '📱 Điện thoại hot nhất', text: 'điện thoại bán chạy nhất hiện nay' },
  { label: '💻 Laptop tốt nhất', text: 'gợi ý laptop tốt nhất' },
  { label: '📚 Sách hay nhất', text: 'gợi ý sách hay nhất' },
  { label: '👟 Giày thể thao', text: 'giày sneaker đẹp' },
  { label: '💰 Sản phẩm giá rẻ', text: 'sản phẩm giá rẻ tốt nhất' },
  { label: '🔥 Đang hot', text: 'sản phẩm đang phổ biến nhất' },
  { label: '🎮 Đồ chơi LEGO', text: 'đồ chơi lego' },
  { label: '🏋️ Dụng cụ thể thao', text: 'dụng cụ thể thao tốt' },
];

export default function Chatbot() {
  const { user } = useAuth();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Xin chào! Tôi có thể giúp bạn tìm sản phẩm phù hợp. Chọn gợi ý bên dưới hoặc nhập câu hỏi nhé 👇',
      showQuickReplies: true,
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    setMessages(prev => [...prev, { role: 'user', content: trimmed }]);
    setInput('');
    setLoading(true);

    try {
      const history = messages.slice(-6).map(m => ({ role: m.role, content: m.content }));
      const res = await api.chat(trimmed, user?.id, history);
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: res.answer, products: res.products, showQuickReplies: true }
      ]);
    } catch {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.', showQuickReplies: true }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input); }
  };

  // Only show quick replies on the last assistant message
  const lastAssistantIdx = messages.map((m, i) => m.role === 'assistant' ? i : -1).filter(i => i >= 0).pop();

  return (
    <div className="chatbot-container">
      {open && (
        <div className="chatbot-window" role="dialog" aria-label="AI Shopping Assistant">
          <div className="chatbot-header">
            <span>🤖 AI Assistant</span>
            <button onClick={() => setOpen(false)} aria-label="Close chat">✕</button>
          </div>

          <div className="chatbot-messages">
            {messages.map((msg, i) => (
              <div key={i}>
                <div className={`chatbot-msg chatbot-msg--${msg.role}`}>
                  <p>{msg.content}</p>
                  {msg.products?.length > 0 && (
                    <div className="chatbot-products">
                      {msg.products.slice(0, 3).map(p => (
                        <a key={p.id} href={`/products/${p.id}`} className="chatbot-product-chip">
                          {p.name} — ${p.price}
                        </a>
                      ))}
                    </div>
                  )}
                </div>

                {/* Quick replies only on last assistant message */}
                {msg.role === 'assistant' && msg.showQuickReplies && i === lastAssistantIdx && !loading && (
                  <div className="chatbot-quick-replies">
                    {QUICK_REPLIES.map((qr) => (
                      <button
                        key={qr.text}
                        className="chatbot-quick-reply-btn"
                        onClick={() => sendMessage(qr.text)}
                      >
                        {qr.label}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="chatbot-msg chatbot-msg--assistant">
                <span className="chatbot-typing">●●●</span>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="chatbot-input">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKey}
              placeholder="Hỏi về sản phẩm..."
              disabled={loading}
              aria-label="Chat input"
            />
            <button onClick={() => sendMessage(input)} disabled={loading || !input.trim()} aria-label="Send">
              ➤
            </button>
          </div>
        </div>
      )}
      <button
        className="chatbot-toggle"
        onClick={() => setOpen(o => !o)}
        aria-label="Toggle AI chat assistant"
      >
        {open ? '✕' : '💬'}
      </button>
    </div>
  );
}
