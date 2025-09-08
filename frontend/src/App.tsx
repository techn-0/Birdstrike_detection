import { useState, useEffect } from "react";
import MapView from "./components/MapView";
import SidePanel from "./components/SidePanel";
import Header from "./components/Header";
import { useWebSocket } from "./hooks/useWebSocket";
import { CctvMeta, Detection } from "./types";
import DetectionModal from "./components/DetectionModal";
import { AuthProvider } from "./contexts/AuthContext";

const API = process.env.REACT_APP_API_HTTP || 'http://localhost:8000';

function App() {
  const [cctvs, setCctvs] = useState<CctvMeta[]>([]);
  const [dets, setDets] = useState<Detection[]>([]);
  const [selectedCctvId, setSelectedCctvId] = useState<string | null>(null);
  const [mapClickMode, setMapClickMode] = useState(false);
  const [pendingCctv, setPendingCctv] = useState<Partial<CctvMeta> | null>(null);

  // CCTV 목록 불러오기
  useEffect(() => {
    fetch(`${API}/cctv/meta`, {
      credentials: "include" // 쿠키 포함
    })
      .then((res) => res.json())
      .then((data: CctvMeta[]) => {
        // 기존 정규화된 좌표(0-1)를 실제 좌표로 변환
        const convertedCctvs = data.map(cctv => {
          // 좌표가 0-1 범위면 정규화된 좌표로 간주하고 변환 (이전 버전 호환성 유지용)
          if (cctv.pos[0] >= 0 && cctv.pos[0] <= 1 && cctv.pos[1] >= 0 && cctv.pos[1] <= 1) {
            const [u, v] = cctv.pos;
            // 인천공항 영역으로 변환
            const lat = 37.4550 + v * (37.4712 - 37.4550);
            const lng = 126.4200 + u * (126.4614 - 126.4200);
            return { ...cctv, pos: [lat, lng] as [number, number] };
          }
          return cctv;
        });
        setCctvs(convertedCctvs);
      });
  }, []);

  // 앱 시작 시, 모든 CCTV의 탐지 내역을 DB에서 불러오기
  useEffect(() => {
    if (cctvs.length > 0) {
      Promise.all(
        cctvs.map((c) =>
          fetch(`${API}/detect/history/${c.id}`)
            .then((res) => res.json())
            .then((data) => {
              console.log(`API 응답 (${c.id}):`, data);
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
      credentials: "include", // 쿠키 포함
      body: JSON.stringify(meta),
    });
    const res = await fetch(`${API}/cctv/meta`, {
      credentials: "include"
    });
    const data: CctvMeta[] = await res.json();
    // 좌표 변환 적용
    const convertedCctvs = data.map(cctv => {
      if (cctv.pos[0] >= 0 && cctv.pos[0] <= 1 && cctv.pos[1] >= 0 && cctv.pos[1] <= 1) {
        const [u, v] = cctv.pos;
        const lat = 37.4550 + v * (37.4712 - 37.4550);
        const lng = 126.4200 + u * (126.4614 - 126.4200);
        return { ...cctv, pos: [lat, lng] as [number, number] };
      }
      return cctv;
    });
    setCctvs(convertedCctvs);
  };

  // CCTV 삭제 함수
  const deleteCctv = async (id: string) => {
    await fetch(`${API}/cctv/meta/${id}`, { 
      method: "DELETE",
      credentials: "include" // 쿠키 포함
    });
    const res = await fetch(`${API}/cctv/meta`, {
      credentials: "include"
    });
    const data: CctvMeta[] = await res.json();
    // 좌표 변환 적용
    const convertedCctvs = data.map(cctv => {
      if (cctv.pos[0] >= 0 && cctv.pos[0] <= 1 && cctv.pos[1] >= 0 && cctv.pos[1] <= 1) {
        const [u, v] = cctv.pos;
        const lat = 37.4550 + v * (37.4712 - 37.4550);
        const lng = 126.4200 + u * (126.4614 - 126.4200);
        return { ...cctv, pos: [lat, lng] as [number, number] };
      }
      return cctv;
    });
    setCctvs(convertedCctvs);
  };

  // 모달 닫기 함수
  const closeModal = () => setSelectedCctvId(null);

  // 지도 클릭으로 CCTV 위치 설정
  const handleMapClick = (lat: number, lng: number) => {
    if (mapClickMode && pendingCctv) {
      const updatedCctv = { ...pendingCctv, pos: [lat, lng] as [number, number] };
      setPendingCctv(updatedCctv);
      setMapClickMode(false);
    }
  };

  return (
    <div style={{ width: "100vw", height: "100vh", display: "flex", flexDirection: "column" }}>
      {/* 상단바 - 고정 높이 */}
      <Header />

      {/* 메인 컨텐츠 영역 - 상단바 아래 나머지 공간 */}
      <div style={{ 
        flex: 1, 
        display: "flex", 
        overflow: "hidden" 
      }}>
        {/* 지도 영역 - 전체 공간을 차지 */}
        <div style={{ flex: 1 }}>
          <MapView
            cctvs={cctvs}
            detections={dets}
            onCctvClick={setSelectedCctvId}
            onMapClick={handleMapClick}
          />
        </div>
      </div>

      {/* 사이드 패널 - fixed로 오른쪽에 고정 */}
      <SidePanel
        cctvs={cctvs}
        onAddOrUpdate={addOrUpdateCctv}
        onDelete={deleteCctv}
        detections={dets}
        onCctvNameClick={setSelectedCctvId}
        mapClickMode={mapClickMode}
        onMapClickModeChange={setMapClickMode}
        pendingCctv={pendingCctv}
        onPendingCctvChange={setPendingCctv}
      />

      {/* 탐지 내역 모달 */}
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

// AuthProvider로 App을 감싸는 래퍼 컴포넌트
function AppWithAuth() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}

export default AppWithAuth;
