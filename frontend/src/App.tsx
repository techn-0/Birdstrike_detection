import { useState, useEffect } from "react";
import MapView from "./components/MapView";
import SidePanel from "./components/SidePanel";
import { useWebSocket } from "./hooks/useWebSocket";
import { CctvMeta } from "./types";

const API = process.env.REACT_APP_API_HTTP;

function App() {
  // CCTV 목록 상태
  const [cctvs, setCctvs] = useState<CctvMeta[]>([]);
  // Detection(알람) 상태
  const [dets, setDets] = useState<any[]>([]);

  // CCTV 목록 불러오기
  useEffect(() => {
    fetch(`${API}/cctv/meta`)
      .then((res) => res.json())
      .then(setCctvs);
  }, []);

  // WS로 새 Detection 받기
  useWebSocket((d) => {
    setDets((prev) => [...prev, d]);
  });

  // CCTV 추가/수정 함수
  const addOrUpdateCctv = async (meta: CctvMeta) => {
    await fetch(`${API}/cctv/meta`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(meta),
    });
    // 수정 후 목록을 다시 받아와서 setCctvs로 갱신
    const res = await fetch(`${API}/cctv/meta`);
    setCctvs(await res.json());
  };

  // CCTV 삭제 함수
  const deleteCctv = async (id: string) => {
    await fetch(`${API}/cctv/meta/${id}`, { method: "DELETE" });
    // 삭제 후 목록을 서버에서 다시 받아옴
    const res = await fetch(`${API}/cctv/meta`);
    setCctvs(await res.json());
  };

  return (
    <>
      <MapView cctvs={cctvs} detections={dets} />
      <SidePanel
        cctvs={cctvs}
        onAddOrUpdate={addOrUpdateCctv}
        onDelete={deleteCctv}
      />
    </>
  );
}

export default App;
