import { useState } from "react";

export default function CopyButton({ text, label = "Copy short URL" }) {
  const [done, setDone] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const el = document.createElement("textarea");
      el.value = text;
      document.body.appendChild(el);
      el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
    }
    setDone(true);
    setTimeout(() => setDone(false), 1800);
  }

  return (
    <button type="button" className="btn btn-ghost" onClick={copy}>
      {done ? "Copied" : label}
    </button>
  );
}
