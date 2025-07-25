import { useState, useEffect } from "react";
import MapView from "./components/MapView";
import SidePanel from "./components/SidePanel";
import { useWebSocket } from "./hooks/useWebSocket";
import { CctvMeta, Detection } from "./types";
import DetectionModal from "./components/DetectionModal";

const API = process.env.REACT_APP_API_HTTP;

function App() {
  const [cctvs, setCctvs] = useState<CctvMeta[]>([]);
  const [dets, setDets] = useState<Detection[]>([]);
  const [selectedCctvId, setSelectedCctvId] = useState<string | null>(null);

  // CCTV 목록 불러오기
  useEffect(() => {
    fetch(`${API}/cctv/meta`)
      .then((res) => res.json())
      .then(setCctvs);
  }, []);

  // 앱 시작 시, 모든 CCTV의 탐지 내역을 DB에서 불러오기
  useEffect(() => {
    if (cctvs.length > 0) {
      Promise.all(
        cctvs.map((c) =>
          fetch(`${API}/detect/history/${c.id}`)
            .then((res) => res.json())
            .then((data) => {
              console.log(`API 응답 (${c.id}):`, data); // ← 여기!
              return data;
            })
            .catch((err) => {
              console.error(`Failed to fetch history for ${c.id}:`, err);
              return [];
            })
        )
      ).then((histories) => {
        const allHist = histories.flat();
        allHist.sort(
          (a, b) =>
            new Date(b.captured_at).getTime() -
            new Date(a.captured_at).getTime()
        );
        setDets(allHist);
      });
    }
  }, [cctvs]);

  // WS로 새 Detection 받기 (실시간 반영)
  useWebSocket((d) => {
    setDets((prev) => [d, ...prev]);
  });

  // CCTV 추가/수정 함수
  const addOrUpdateCctv = async (meta: CctvMeta) => {
    await fetch(`${API}/cctv/meta`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(meta),
    });
    // 수정 후 목록을 다시 받아옴
    const res = await fetch(`${API}/cctv/meta`);
    setCctvs(await res.json());
  };

  // CCTV 삭제 함수
  const deleteCctv = async (id: string) => {
    await fetch(`${API}/cctv/meta/${id}`, { method: "DELETE" });
    // 삭제 후 목록 갱신
    const res = await fetch(`${API}/cctv/meta`);
    setCctvs(await res.json());
  };

  // 모달 닫기 함수
  const closeModal = () => setSelectedCctvId(null);

  return (
    <div style={{ width: "100vw", height: "100vh", position: "relative", overflow: "hidden" }}>
      <MapView
        cctvs={cctvs}
        detections={dets}
        onCctvClick={setSelectedCctvId}
      />
      <SidePanel
        cctvs={cctvs}
        onAddOrUpdate={addOrUpdateCctv}
        onDelete={deleteCctv}
        detections={dets}
        onCctvNameClick={setSelectedCctvId}
      />
      {selectedCctvId && (
        <DetectionModal
          cctv={cctvs.find((c) => c.id === selectedCctvId)!}
          detections={dets.filter((d) => d.cctv_id === selectedCctvId)}
          onClose={closeModal}
        />
      )}
    </div>
  );
}

export default App;
