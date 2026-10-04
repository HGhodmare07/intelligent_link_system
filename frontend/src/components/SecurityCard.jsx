export default function SecurityCard({ security, blocked = false, message }) {
  const decision = security?.decision ?? (blocked ? "BLOCK" : "UNKNOWN");
  const isBlocked = blocked || String(decision).toUpperCase() === "BLOCK";
  const p = security?.pMalicious;

  return (
    <div className={`card security ${isBlocked ? "security-blocked" : "security-ok"}`}>
      {isBlocked && <h3 className="security-headline">{message || "URL blocked by security validation"}</h3>}
      <dl className="facts">
        <div>
          <dt>Security decision</dt>
          <dd><span className={`badge ${isBlocked ? "badge-danger" : "badge-ok"}`}>{decision}</span></dd>
        </div>
        <div>
          <dt>Malicious probability</dt>
          <dd>{typeof p === "number" && !Number.isNaN(p) ? `${p} (${(p * 100).toFixed(1)}%)` : "Not provided"}</dd>
        </div>
        <div>
          <dt>Classification</dt>
          <dd>{security?.mostLikelyClass ?? "Not provided"}</dd>
        </div>
      </dl>
    </div>
  );
}
