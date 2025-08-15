import { useState } from "react";
import { CctvMeta, Detection } from "../types";
import { useAuth } from "../contexts/AuthContext";

interface Props {
  cctvs: CctvMeta[];
  onAddOrUpdate: (meta: CctvMeta) => void;
  onDelete: (id: string) => void;
  detections: Detection[];
  onCctvNameClick?: (id: string) => void;
}

export default function SidePanel({ cctvs, onAddOrUpdate, onDelete, detections, onCctvNameClick }: Props) {
  const { user, isAdmin } = useAuth();
  const [form, setForm] = useState<Partial<CctvMeta> & { posInput?: string }>({});

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
              </div>
              <div className="text-xs text-gray-500 mt-1">
                위치: {c.pos.join(", ")}<br />
                방향: {c.direction}°, 시야각: {c.angle}°, 길이: {c.length}
              </div>
              <div className="mt-2">
                {isAdmin() && (
                  <>
                    <button 
                      className="text-blue-500 hover:underline mr-3" 
                      onClick={() => setForm({ ...c, posInput: c.pos.join(",") })}
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
        }}
      >
        {isAdmin() ? (
          <>
            <h3 className="font-bold mb-3 text-blue-700">CCTV 추가/수정</h3>
            <form
              className="flex flex-col gap-2"
              onSubmit={e => {
                e.preventDefault();
                const posArr = form.posInput?.split(",").map(Number) as [number, number] | undefined;
            if (
              form.id &&
              form.name &&
              posArr &&
              posArr.length === 2 &&
              posArr.every((v) => !isNaN(v) && v >= 0 && v <= 1) &&
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
              });
              setForm({});
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
          <input
            placeholder="위치 (u,v, 예: 0.5,0.5)"
            value={form.posInput ?? ""}
            onChange={e => setForm(f => ({ ...f, posInput: e.target.value }))}
            required
            className="border rounded px-2 py-1"
          />
          <input
            placeholder="방향"
            type="number"
            value={form.direction ?? ""}
            onChange={e => setForm(f => ({ ...f, direction: Number(e.target.value) }))}
            required
            className="border rounded px-2 py-1"
          />
          <input
            placeholder="시야각"
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
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 4 }}>
            <input
              type="color"
              value={form.color || "#007bff"}
              onChange={e => setForm(f => ({ ...f, color: e.target.value }))}
              style={{ width: 40, height: 30 }}
            />
            <span className="text-sm">마커 색상</span>
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
