import { useEffect } from "react";

export function useWebSocket(onData: (d: any) => void) {
     console.log("useWebSocket init");   // 디버깅 추가
  useEffect(() => {
    const url = process.env.REACT_APP_API_WS!;  // 디버깅 추가
    console.log("connect WS ->", url);   // 디버깅 추가
    const ws = new WebSocket(process.env.REACT_APP_API_WS!);
    ws.onopen    = () => ws.send("ping");
    ws.onmessage = e => onData(JSON.parse(e.data));
    return () => ws.close();
  }, [onData]);
}
