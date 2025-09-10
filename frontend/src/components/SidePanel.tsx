import React, { useState, useEffect } from "react";
import { CctvMeta, Detection } from "../types";
import { useAuth } from "../contexts/AuthContext";

interface Props {
  cctvs: CctvMeta[];
  onAddOrUpdate: (meta: CctvMeta) => void;
  onDelete: (id: string) => void;
  detections: Detection[];
  onCctvNameClick?: (id: string) => void;
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
        width: "340px",
        height: "calc(100vh - 60px)", // 전체 높이에서 상단바 높이 제외
        background: "rgba(255,255,255,0.95)",
        boxShadow: "-2px 0 12px rgba(0,0,0,0.1)",
        borderLeft: "1px solid #e5e5e5",
        display: "flex",
        flexDirection: "column",
        backdropFilter: "blur(4px)",
        zIndex: 999, // 지도 위에 표시되도록
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
        <h2 className="font-bold mb-4 text-lg text-blue-700">CCTV 목록</h2>
        <ul className="mb-6">
          {cctvs.map(c => (
            <li key={c.id} className="mb-3 pb-3 border-b border-gray-200">
              <div>
                <b
                  style={{
                    cursor: "pointer",
                    color: c.color || "#007bff"
                  }}
                  onClick={() => onCctvNameClick && onCctvNameClick(c.id)}
                >
                  이름: {c.name}
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
                방향: {c.direction}°, 시야각: {c.angle}°, 길이: {c.length}km
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
              <div className="mt-2">
                {isAdmin() && (
                  <>
                    <button 
                      className="text-blue-500 hover:underline mr-3" 
                      onClick={() => setForm({ 
                        ...c, 
                        posInput: c.pos.join(","),
                        sensorSizeInput: c.sensor_size ? c.sensor_size.join(",") : "",
                        resolutionInput: c.resolution ? c.resolution.join(",") : ""
                      })}
                    >
                      수정
                    </button>
                    <button 
                      className="text-red-500 hover:underline" 
                      onClick={() => onDelete(c.id)}
                    >
                      삭제
                    </button>
                  </>
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
          borderTop: "1px solid #e5e5e5",
          padding: "16px",
          background: "rgba(255,255,255,0.98)",
          flexShrink: 0, // 크기 고정
          maxHeight: "50vh", // 최대 높이 제한
          overflowY: "auto", // 폼이 길어지면 스크롤
        }}
      >
        {isAdmin() ? (
          <>
            <h3 className="font-bold mb-3 text-blue-700">CCTV 추가/수정</h3>
            {mapClickMode && (
              <div className="mb-3 p-2 bg-orange-100 border border-orange-300 rounded text-sm text-orange-700">
                🗺️ 지도에서 CCTV를 설치할 위치를 클릭하세요
              </div>
            )}
            <form
              className="flex flex-col gap-2"
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
            className="border rounded px-2 py-1"
          />
          <input
            placeholder="이름"
            value={form.name || ""}
            onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            required
            className="border rounded px-2 py-1"
          />
          <div style={{ display: "flex", gap: "4px" }}>
            <input
              placeholder="위치 (위도,경도, 예: 37.4631,126.4407)"
              value={form.posInput ?? ""}
              onChange={e => setForm(f => ({ ...f, posInput: e.target.value }))}
              required
              className="border rounded px-2 py-1 flex-1"
            />
            <button
              type="button"
              onClick={() => {
                onPendingCctvChange(form);
                onMapClickModeChange(true);
              }}
              className={`px-3 py-1 rounded text-sm transition ${
                mapClickMode 
                  ? "bg-orange-500 text-white" 
                  : "bg-gray-200 hover:bg-gray-300"
              }`}
            >
              {mapClickMode ? "지도 클릭 대기중..." : "지도에서 선택"}
            </button>
          </div>
          <input
            placeholder="방향(각도)"
            type="number"
            value={form.direction ?? ""}
            onChange={e => setForm(f => ({ ...f, direction: Number(e.target.value) }))}
            required
            className="border rounded px-2 py-1"
          />
          <input
            placeholder="시야각(각도)"
            type="number"
            value={form.angle ?? ""}
            onChange={e => setForm(f => ({ ...f, angle: Number(e.target.value) }))}
            required
            className="border rounded px-2 py-1"
          />
          <input
            placeholder="길이"
            type="number"
            value={form.length ?? ""}
            onChange={e => setForm(f => ({ ...f, length: Number(e.target.value) }))}
            required
            className="border rounded px-2 py-1"
          />
          <input
            placeholder="센서 크기 (예: 36,24)"
            value={form.sensorSizeInput ?? ""}
            onChange={e => setForm(f => ({ ...f, sensorSizeInput: e.target.value }))}
            className="border rounded px-2 py-1"
          />
          <input
            placeholder="해상도 (예: 1920,1080)"
            value={form.resolutionInput ?? ""}
            onChange={e => setForm(f => ({ ...f, resolutionInput: e.target.value }))}
            className="border rounded px-2 py-1"
          />
          <input
            placeholder="초점거리 (mm)"
            type="number"
            value={form.focal_length ?? ""}
            onChange={e => setForm(f => ({ ...f, focal_length: Number(e.target.value) || undefined }))}
            className="border rounded px-2 py-1"
          />
          <input
            placeholder="센서 대각선 길이 (mm)"
            type="number"
            value={form.sensor_diagonal ?? ""}
            onChange={e => setForm(f => ({ ...f, sensor_diagonal: Number(e.target.value) || undefined }))}
            className="border rounded px-2 py-1"
          />
          <input
            placeholder="크롭팩터"
            type="number"
            step="0.1"
            value={form.crop_factor ?? ""}
            onChange={e => setForm(f => ({ ...f, crop_factor: Number(e.target.value) || undefined }))}
            className="border rounded px-2 py-1"
          />
          <input
            placeholder="모델명"
            value={form.model_name ?? ""}
            onChange={e => setForm(f => ({ ...f, model_name: e.target.value || undefined }))}
            className="border rounded px-2 py-1"
          />
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
            <input
              type="color"
              value={form.color || "#007bff"}
              onChange={e => setForm(f => ({ ...f, color: e.target.value }))}
              style={{ width: 40, height: 30 }}
            />
            <span className="text-sm">마커 색상</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
            <input
              type="checkbox"
              checked={form.is_photo_slides || false}
              onChange={e => setForm(f => ({ ...f, is_photo_slides: e.target.checked }))}
              id="photoSlidesCheck"
            />
            <label htmlFor="photoSlidesCheck" className="text-sm">포토 슬라이드 활성화</label>
          </div>
          <button 
            type="submit" 
            className="bg-blue-500 hover:bg-blue-600 text-white py-2 mt-2 rounded transition"
          >
            저장
          </button>
        </form>
          </>
        ) : (
          <div className="p-4 bg-gray-100 rounded-lg text-center">
            <h3 className="font-bold mb-2 text-gray-600">CCTV 관리</h3>
            {!user ? (
              <p className="text-sm text-gray-500">로그인하면 CCTV를 관리할 수 있습니다</p>
            ) : (
              <p className="text-sm text-gray-500">CCTV 추가/수정/삭제는 관리자만 가능합니다</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
