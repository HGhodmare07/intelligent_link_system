import { useEffect, useState } from "react";
import { listStoredUrls } from "../services/api.js";

export default function CodeLookup({ initial = "", onSubmit, buttonLabel = "Load" }) {
  const [value, setValue] = useState(initial);
  useEffect(() => setValue(initial), [initial]);
  const recent = listStoredUrls();

  return (
    <form className="card lookup" onSubmit={(e) => { e.preventDefault(); if (value.trim()) onSubmit(value.trim()); }}>
      <label htmlFor="short-code">Short code</label>
      <div className="row">
        <input id="short-code" list="recent-codes" placeholder="e.g. O" value={value} onChange={(e) => setValue(e.target.value)} />
        <datalist id="recent-codes">
          {recent.map((u) => <option key={u.shortCode} value={u.shortCode}>{u.originalUrl}</option>)}
        </datalist>
        <button className="btn btn-primary" type="submit" disabled={!value.trim()}>{buttonLabel}</button>
      </div>
    </form>
  );
}
