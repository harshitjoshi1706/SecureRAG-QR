import { useEffect, useState } from "react";

function App() {
  const [backendStatus, setBackendStatus] = useState("Checking backend...");

  useEffect(() => {
    fetch("http://localhost:8000/api/health")
      .then((response) => response.json())
      .then((data) => {
        setBackendStatus(`${data.application}: ${data.status}`);
      })
      .catch(() => {
        setBackendStatus("Backend connection failed");
      });
  }, []);

  return (
    <div>
      <h1>SecureRAG-QR</h1>
      <p>{backendStatus}</p>
    </div>
  );
}

export default App;