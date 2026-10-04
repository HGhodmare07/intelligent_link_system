import { useNavigate, useParams } from "react-router-dom";
import CodeLookup from "../components/CodeLookup.jsx";
import RouteManager from "../components/RouteManager.jsx";

export default function Routing() {
  const { code } = useParams();
  const navigate = useNavigate();
  return (
    <>
      <div className="page-head">
        <div>
          <h1>Routing</h1>
          <p className="muted">Send visitors to a different destination depending on their device. New destinations are security-checked first.</p>
        </div>
      </div>
      <CodeLookup initial={code || ""} buttonLabel="Load routes" onSubmit={(c) => navigate(`/routing/${encodeURIComponent(c)}`)} />
      {code && <RouteManager code={code} />}
    </>
  );
}
