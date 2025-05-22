import { useState } from "react";
import MapView from "./components/MapView";
import SidePanel from "./components/SidePanel";
import { useWebSocket } from "./hooks/useWebSocket";

function App() {
  const [dets, setDets] = useState<any[]>([]);

  // WS로 새 데이터 받으면 배열 추가
  useWebSocket(d => {
  console.log("ARR PUSH", d);      // 디버깅 추가
  setDets(prev => [...prev, d]);
});

  return (
    <>
      <MapView detections={dets} />
      <SidePanel />
    </>
  );
}

export default App;
