// DetectionModal.tsx
import React from "react";
import { Detection, CctvMeta } from "../types";

export default function DetectionModal({
  cctv,
  detections,
  onClose,
}: {
  cctv: CctvMeta;
  detections: Detection[];
  onClose: () => void;
}) {
  return (
    <div
      style={{
        position: "fixed",
        left: 0,
        top: 0,
        width: "100vw",
        height: "100vh",
        background: "rgba(0,0,0,0.3)",
        zIndex: 1000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          background: "#fff",
          padding: 32,                // 패딩 더 크게
          borderRadius: 12,           // 모서리 더 둥글게
          minWidth: 480,              // 최소 너비 더 크게
          maxWidth: 900,              // 최대 너비 추가
          maxHeight: "90vh",          // 최대 높이 더 크게
          overflowY: "auto",
        }}
      >
        <h2>
          {cctv.name} ({cctv.id}) 탐지 내역
        </h2>
        <button onClick={onClose} style={{ float: "right" }}>
          닫기
        </button>
        <ul>
          {detections.length === 0 && <li>탐지 내역 없음</li>}
          {detections.map((d, i) => (
            <li key={i} style={{ marginBottom: 12 }}>
              <b>{d.captured_at}</b> 위험도: {d.risk}
              <br />
              <b>탐지된 새 수:</b> {d.bird_count}
              {d.frame_url && (
                <div style={{ marginTop: 8 }}>
                  <img
                    src={`${process.env.REACT_APP_API_HTTP}${d.frame_url}`}
                    alt="탐지된 조류"
                    style={{
                      maxWidth: "400px",
                      maxHeight: "300px",
                      width: "auto",
                      height: "auto",
                      border: "1px solid #ddd",
                      borderRadius: "4px"
                    }}
                    onError={(e) => {
                      console.error("이미지 로딩 실패:", e.currentTarget.src);
                      e.currentTarget.style.display = "none";
                    }}
                    onLoad={() => {
                      console.log("이미지 로딩 성공:", `${process.env.REACT_APP_API_HTTP}${d.frame_url}`);
                    }}
                  />
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
