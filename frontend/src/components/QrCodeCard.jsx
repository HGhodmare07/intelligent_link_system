import { useState } from "react";
import { getQrCode, normalizeError } from "../services/api.js";
import Loading, { ErrorMessage } from "./Loading.jsx";
import CopyButton from "./CopyButton.jsx";

export default function QrCodeCard({ code, shortUrl }) {
  const [qr, setQr] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function show() {
    setLoading(true);
    setError(null);
    try {
      setQr(await getQrCode(code));
    } catch (err) {
      setError(err.response || err.request ? normalizeError(err) : { kind: "server", message: "The QR code could not be read from the server response." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h3>QR code</h3>
      <div className="row">
        <button className="btn btn-primary" onClick={show} disabled={loading}>{qr ? "Reload QR" : "Show QR"}</button>
        {shortUrl && <CopyButton text={shortUrl} />}
      </div>
      {loading && <Loading label="Loading QR code..." />}
      <ErrorMessage error={error} />
      {qr && <img className="qr" src={qr} alt={`QR code for short code ${code}`} />}
    </div>
  );
}
