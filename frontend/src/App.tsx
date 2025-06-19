import { useState, useEffect } from "react";
import MapView from "./components/MapView";
import SidePanel from "./components/SidePanel";
import { useWebSocket } from "./hooks/useWebSocket";

const DETS_KEY = "cctv_detections";

function App() {
  // 1. LocalStorage에서 초기값 불러오기
  const [dets, setDets] = useState<any[]>(() => {
    const saved = localStorage.getItem(DETS_KEY);
    return saved ? JSON.parse(saved) : [];
  });

  // 2. 상태가 바뀔 때마다 LocalStorage에 저장
  useEffect(() => {
    localStorage.setItem(DETS_KEY, JSON.stringify(dets));
  }, [dets]);

  // 3. WS로 새 데이터 받으면 배열 추가
  useWebSocket((d) => {
    setDets((prev) => [...prev, d]);
  });

  return (
    <>
      <MapView detections={dets} />
      <SidePanel />
    </>
  );
}

export default App;
