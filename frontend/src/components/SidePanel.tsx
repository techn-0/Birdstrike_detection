import React, { useState, useEffect } from "react";
import { CctvMeta, Detection } from "../types";
import { useAuth } from "../contexts/AuthContext";

interface Props {
  cctvs: CctvMeta[];
  onAddOrUpdate: (meta: CctvMeta) => void;
  onDelete: (id: string) => void;
  detections: Detection[];
  onCctvNameClick?: (id: string) => void;
  onPhotoSlidesClick?: (id: string) => void;
  mapClickMode: boolean;
  onMapClickModeChange: (mode: boolean) => void;
  pendingCctv: Partial<CctvMeta> | null;
  onPendingCctvChange: (cctv: Partial<CctvMeta> | null) => void;
}

export default function SidePanel({ 
  cctvs, 
  onAddOrUpdate, 
  onDelete, 
  detections, 
  onCctvNameClick,
  onPhotoSlidesClick,
  mapClickMode,
  onMapClickModeChange,
  pendingCctv,
  onPendingCctvChange
}: Props) {
  const { user, isAdmin } = useAuth();
  const [form, setForm] = useState<Partial<CctvMeta> & { 
    posInput?: string;
    sensorSizeInput?: string;
    resolutionInput?: string;
  }>({});

  // pendingCctv가 변경되면 form에 반영
  useEffect(() => {
    if (pendingCctv) {
      setForm({
        ...pendingCctv,
        posInput: pendingCctv.pos ? pendingCctv.pos.join(",") : "",
        sensorSizeInput: pendingCctv.sensor_size ? pendingCctv.sensor_size.join(",") : "",
        resolutionInput: pendingCctv.resolution ? pendingCctv.resolution.join(",") : ""
      });
    }
  }, [pendingCctv]);

  const isEdit = form.id && cctvs.some(c => c.id === form.id);

  return (
    <div
      style={{
        position: "fixed",
        top: "60px", // 상단바 높이만큼 아래로
        right: "0",
        width: "400px", // 340px에서 400px로 확장
        height: "calc(100vh - 60px)", // 전체 높이에서 상단바 높이 제외
        background: "rgba(255, 255, 255, 0.95)", // 헤더와 동일한 투명도
        backdropFilter: "blur(10px)", // 헤더와 동일한 블러
        boxShadow: "-4px 0 25px rgba(0, 0, 0, 0.1)", // 더 부드러운 그림자
        borderLeft: "1px solid #e5e5e5",
        display: "flex",
        flexDirection: "column",
        zIndex: 1000, // 헤더와 동일한 z-index
      }}
    >
      {/* CCTV 목록 - 스크롤 가능한 영역 */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "24px 16px 0 16px",
        }}
      >
        <h2 style={{ 
          margin: "0 0 20px 0", 
          fontSize: "20px", 
          fontWeight: "bold", 
          color: "#2563eb" 
        }}>
          📡 CCTV 목록
        </h2>
        <ul style={{ marginBottom: "24px" }}>
          {cctvs.map(c => (
            <li key={c.id} style={{
              marginBottom: "16px",
              paddingBottom: "16px",
              borderBottom: "1px solid #e5e7eb",
              backgroundColor: "rgba(249, 250, 251, 0.5)",
              padding: "16px",
              borderRadius: "8px",
              border: "1px solid rgba(229, 231, 235, 0.5)"
            }}>
              <div>
                <b
                  style={{
                    cursor: "pointer",
                    color: c.color || "#2563eb",
                    fontSize: "16px",
                    fontWeight: "600",
                    transition: "color 0.2s"
                  }}
                  onClick={() => onCctvNameClick && onCctvNameClick(c.id)}
                  onMouseOver={(e) => e.currentTarget.style.color = "#1d4ed8"}
                  onMouseOut={(e) => e.currentTarget.style.color = c.color || "#2563eb"}
                >
                  📹 {c.name}
                </b>
                <br />
                <span className="text-sm text-gray-600"><b>ID:</b> {c.id}</span>
                {c.model_name && (
                  <>
                    <br />
                    <span className="text-sm text-gray-600"><b>모델:</b> {c.model_name}</span>
                  </>
                )}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                위치: {c.pos[0].toFixed(4)}, {c.pos[1].toFixed(4)}<br />
                방향: {c.direction}°, 시야각: {c.angle}°, 탐지거리: {c.length}m
                {c.resolution && (
                  <>
                    <br />
                    해상도: {c.resolution[0]}×{c.resolution[1]}
                  </>
                )}
                {c.sensor_size && (
                  <>
                    <br />
                    센서: {c.sensor_size[0]}×{c.sensor_size[1]}mm
                  </>
                )}
                {c.focal_length && (
                  <>
                    <br />
                    초점거리: {c.focal_length}mm
                  </>
                )}
                {c.is_photo_slides && (
                  <>
                    <br />
                    <span className="text-green-600 font-semibold">📸 포토 슬라이드 활성화</span>
                  </>
                )}
              </div>
              <div style={{ marginTop: "12px" }}>
                {c.is_photo_slides && (
                  <button 
                    style={{
                      backgroundColor: "#10b981",
                      color: "white",
                      padding: "8px 16px",
                      border: "none",
                      borderRadius: "6px",
                      fontSize: "14px",
                      fontWeight: "500",
                      cursor: "pointer",
                      marginRight: "8px",
                      marginBottom: "8px",
                      transition: "background-color 0.2s"
                    }}
                    onClick={() => onPhotoSlidesClick && onPhotoSlidesClick(c.id)}
                    onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#059669"}
                    onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#10b981"}
                  >
                    📸 포토 슬라이드 보기
                  </button>
                )}
                {isAdmin() && (
                  <div style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}>
                    <button 
                      style={{
                        backgroundColor: "#3b82f6",
                        color: "white",
                        padding: "6px 12px",
                        border: "none",
                        borderRadius: "6px",
                        fontSize: "13px",
                        fontWeight: "500",
                        cursor: "pointer",
                        transition: "background-color 0.2s"
                      }}
                      onClick={() => setForm({ 
                        ...c, 
                        posInput: c.pos.join(","),
                        sensorSizeInput: c.sensor_size ? c.sensor_size.join(",") : "",
                        resolutionInput: c.resolution ? c.resolution.join(",") : ""
                      })}
                      onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#2563eb"}
                      onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#3b82f6"}
                    >
                      ✏️ 수정
                    </button>
                    <button 
                      style={{
                        backgroundColor: "#ef4444",
                        color: "white",
                        padding: "6px 12px",
                        border: "none",
                        borderRadius: "6px",
                        fontSize: "13px",
                        fontWeight: "500",
                        cursor: "pointer",
                        transition: "background-color 0.2s"
                      }}
                      onClick={() => onDelete(c.id)}
                      onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#dc2626"}
                      onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#ef4444"}
                    >
                      🗑️ 삭제
                    </button>
                  </div>
                )}
                {!user && (
                  <span className="text-gray-400 text-sm">로그인하면 관리 기능을 사용할 수 있습니다</span>
                )}
                {user && !isAdmin() && (
                  <span className="text-gray-400 text-sm">관리자 권한이 필요합니다</span>
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>
      
      {/* CCTV 추가/수정 폼 - 하단 고정 */}
      <div
        style={{
          borderTop: "1px solid #e5e7eb",
          padding: "20px",
          background: "rgba(249, 250, 251, 0.95)",
          backdropFilter: "blur(10px)",
          flexShrink: 0, // 크기 고정
          maxHeight: "50vh", // 최대 높이 제한
          overflowY: "auto", // 폼이 길어지면 스크롤
        }}
      >
        {isAdmin() ? (
          <>
            <h3 style={{ 
              margin: "0 0 16px 0", 
              fontSize: "18px", 
              fontWeight: "600", 
              color: "#2563eb" 
            }}>
              ⚙️ CCTV 관리
            </h3>
            {mapClickMode && (
              <div style={{
                marginBottom: "16px",
                padding: "12px",
                backgroundColor: "rgba(251, 191, 36, 0.1)",
                border: "1px solid rgba(251, 191, 36, 0.3)",
                borderRadius: "8px",
                fontSize: "14px",
                color: "#92400e",
                fontWeight: "500"
              }}>
                🗺️ 지도에서 CCTV를 설치할 위치를 클릭하세요
              </div>
            )}
            <form
              style={{ display: "flex", flexDirection: "column", gap: "12px" }}
              onSubmit={e => {
                e.preventDefault();
                const posArr = form.posInput?.split(",").map(Number) as [number, number] | undefined;
                const sensorSizeArr = form.sensorSizeInput?.split(",").map(Number) as [number, number] | undefined;
                const resolutionArr = form.resolutionInput?.split(",").map(Number) as [number, number] | undefined;
                
                if (
                  form.id &&
                  form.name &&
                  posArr &&
                  posArr.length === 2 &&
                  posArr.every((v) => !isNaN(v)) &&
                  form.direction !== undefined &&
                  form.angle !== undefined &&
                  form.length !== undefined
                ) {
                  onAddOrUpdate({
                    id: form.id,
                    name: form.name,
                    pos: posArr,
                    direction: form.direction,
                    angle: form.angle,
                    length: form.length,
                    color: form.color,
                    sensor_size: sensorSizeArr && sensorSizeArr.length === 2 && sensorSizeArr.every(v => !isNaN(v)) ? sensorSizeArr : undefined,
                    resolution: resolutionArr && resolutionArr.length === 2 && resolutionArr.every(v => !isNaN(v)) ? resolutionArr : undefined,
                    focal_length: form.focal_length,
                    sensor_diagonal: form.sensor_diagonal,
                    crop_factor: form.crop_factor,
                    model_name: form.model_name,
                    is_photo_slides: form.is_photo_slides || false
                  });
                  setForm({});
                  onPendingCctvChange(null);
                  onMapClickModeChange(false);
                }
              }}
            >
          <input
            type="text"
            placeholder="ID(수정 불가)"
            value={form.id || ""}
            onChange={e => setForm(f => ({ ...f, id: e.target.value }))}
            required
            readOnly={!!isEdit}
            style={{
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              padding: "10px 12px",
              fontSize: "14px",
              backgroundColor: isEdit ? "#f9fafb" : "white",
              transition: "border-color 0.2s"
            }}
          />
          <input
            placeholder="이름"
            value={form.name || ""}
            onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            required
            style={{
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              padding: "10px 12px",
              fontSize: "14px",
              transition: "border-color 0.2s"
            }}
          />
          <div style={{ display: "flex", gap: "8px" }}>
            <input
              placeholder="위치 (위도,경도, 예: 34.8423,127.6169)"
              value={form.posInput ?? ""}
              onChange={e => setForm(f => ({ ...f, posInput: e.target.value }))}
              required
              style={{
                border: "1px solid #d1d5db",
                borderRadius: "6px",
                padding: "10px 12px",
                fontSize: "14px",
                flex: 1,
                transition: "border-color 0.2s"
              }}
            />
            <button
              type="button"
              onClick={() => {
                onPendingCctvChange(form);
                onMapClickModeChange(true);
              }}
              style={{
                padding: "10px 16px",
                borderRadius: "6px",
                fontSize: "13px",
                fontWeight: "500",
                border: "none",
                cursor: "pointer",
                transition: "background-color 0.2s",
                backgroundColor: mapClickMode ? "#f59e0b" : "#6b7280",
                color: "white"
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = mapClickMode ? "#d97706" : "#4b5563";
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = mapClickMode ? "#f59e0b" : "#6b7280";
              }}
            >
              {mapClickMode ? "대기중..." : "🗺️ 지도 선택"}
            </button>
          </div>
          <input
            placeholder="방향(각도)"
            type="number"
            value={form.direction ?? ""}
            onChange={e => setForm(f => ({ ...f, direction: Number(e.target.value) }))}
            required
            style={{
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              padding: "10px 12px",
              fontSize: "14px",
              transition: "border-color 0.2s"
            }}
          />
          <input
            placeholder="시야각(각도)"
            type="number"
            value={form.angle ?? ""}
            onChange={e => setForm(f => ({ ...f, angle: Number(e.target.value) }))}
            required
            style={{
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              padding: "10px 12px",
              fontSize: "14px",
              transition: "border-color 0.2s"
            }}
          />
          <input
            placeholder="탐지 거리 (미터, 예: 200)"
            type="number"
            value={form.length ?? ""}
            onChange={e => setForm(f => ({ ...f, length: Number(e.target.value) }))}
            required
            style={{
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              padding: "10px 12px",
              fontSize: "14px",
              transition: "border-color 0.2s"
            }}
          />
          <input
            placeholder="센서 크기 (예: 36,24)"
            value={form.sensorSizeInput ?? ""}
            onChange={e => setForm(f => ({ ...f, sensorSizeInput: e.target.value }))}
            style={{
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              padding: "10px 12px",
              fontSize: "14px",
              transition: "border-color 0.2s"
            }}
          />
          <input
            placeholder="해상도 (예: 1920,1080)"
            value={form.resolutionInput ?? ""}
            onChange={e => setForm(f => ({ ...f, resolutionInput: e.target.value }))}
            style={{
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              padding: "10px 12px",
              fontSize: "14px",
              transition: "border-color 0.2s"
            }}
          />
          <input
            placeholder="초점거리 (mm)"
            type="number"
            value={form.focal_length ?? ""}
            onChange={e => setForm(f => ({ ...f, focal_length: Number(e.target.value) || undefined }))}
            style={{
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              padding: "10px 12px",
              fontSize: "14px",
              transition: "border-color 0.2s"
            }}
          />
          <input
            placeholder="센서 대각선 길이 (mm)"
            type="number"
            value={form.sensor_diagonal ?? ""}
            onChange={e => setForm(f => ({ ...f, sensor_diagonal: Number(e.target.value) || undefined }))}
            style={{
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              padding: "10px 12px",
              fontSize: "14px",
              transition: "border-color 0.2s"
            }}
          />
          <input
            placeholder="크롭팩터"
            type="number"
            step="0.1"
            value={form.crop_factor ?? ""}
            onChange={e => setForm(f => ({ ...f, crop_factor: Number(e.target.value) || undefined }))}
            style={{
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              padding: "10px 12px",
              fontSize: "14px",
              transition: "border-color 0.2s"
            }}
          />
          <input
            placeholder="모델명"
            value={form.model_name ?? ""}
            onChange={e => setForm(f => ({ ...f, model_name: e.target.value || undefined }))}
            style={{
              border: "1px solid #d1d5db",
              borderRadius: "6px",
              padding: "10px 12px",
              fontSize: "14px",
              transition: "border-color 0.2s"
            }}
          />
          <div style={{ display: "flex", alignItems: "center", gap: "12px", marginTop: "8px" }}>
            <input
              type="color"
              value={form.color || "#2563eb"}
              onChange={e => setForm(f => ({ ...f, color: e.target.value }))}
              style={{ 
                width: "40px", 
                height: "40px", 
                border: "1px solid #d1d5db", 
                borderRadius: "6px",
                cursor: "pointer"
              }}
            />
            <span style={{ fontSize: "14px", fontWeight: "500", color: "#374151" }}>마커 색상</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "12px", marginTop: "8px" }}>
            <input
              type="checkbox"
              checked={form.is_photo_slides || false}
              onChange={e => setForm(f => ({ ...f, is_photo_slides: e.target.checked }))}
              id="photoSlidesCheck"
              style={{ 
                width: "18px", 
                height: "18px",
                cursor: "pointer"
              }}
            />
            <label 
              htmlFor="photoSlidesCheck" 
              style={{ 
                fontSize: "14px", 
                fontWeight: "500", 
                color: "#374151",
                cursor: "pointer"
              }}
            >
              📸 포토 슬라이드 활성화
            </label>
          </div>
          <button 
            type="submit" 
            style={{
              backgroundColor: "#2563eb",
              color: "white",
              padding: "12px 24px",
              border: "none",
              borderRadius: "6px",
              fontSize: "16px",
              fontWeight: "600",
              cursor: "pointer",
              marginTop: "16px",
              transition: "background-color 0.2s"
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#1d4ed8"}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#2563eb"}
          >
            💾 저장
          </button>
        </form>
          </>
        ) : (
          <div style={{
            padding: "20px",
            backgroundColor: "rgba(249, 250, 251, 0.8)",
            borderRadius: "8px",
            textAlign: "center",
            border: "1px solid #e5e7eb"
          }}>
            <h3 style={{ 
              margin: "0 0 12px 0", 
              fontSize: "16px", 
              fontWeight: "600", 
              color: "#6b7280" 
            }}>
              🔐 CCTV 관리
            </h3>
            {!user ? (
              <p style={{ 
                fontSize: "14px", 
                color: "#6b7280", 
                margin: 0,
                lineHeight: 1.5
              }}>
                로그인하면 CCTV를 관리할 수 있습니다
              </p>
            ) : (
              <p style={{ 
                fontSize: "14px", 
                color: "#6b7280", 
                margin: 0,
                lineHeight: 1.5
              }}>
                CCTV 추가/수정/삭제는 관리자만 가능합니다
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
