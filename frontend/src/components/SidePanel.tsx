import { useState } from "react";
import { CctvMeta } from "../types";

interface Props {
  cctvs: CctvMeta[];
  onAddOrUpdate: (meta: CctvMeta) => void;
  onDelete: (id: string) => void;
}

export default function SidePanel({ cctvs, onAddOrUpdate, onDelete }: Props) {
  // 위치 입력은 문자열로 관리
  const [form, setForm] = useState<Partial<CctvMeta> & { posInput?: string }>({});

  // 수정 모드 판별: form.id가 cctvs에 이미 존재하면 수정
  const isEdit = form.id && cctvs.some(c => c.id === form.id);

  return (
    <div className="fixed top-0 right-0 w-64 h-full bg-white shadow-lg p-4 overflow-y-auto">
      <h2 className="font-bold mb-2">CCTV 목록</h2>
      <ul>
        {cctvs.map(c => (
          <li key={c.id} className="mb-2 border-b pb-1">
            <div>
              <b>이름:</b> {c.name}<br />
              <b>ID:</b> {c.id}
            </div>
            <div className="text-xs text-gray-500">
              위치: {c.pos.join(", ")}<br />
              방향: {c.direction}°, 시야각: {c.angle}°, 길이: {c.length}
            </div>
            <button className="text-blue-500 mr-2" onClick={() => setForm({ ...c, posInput: c.pos.join(",") })}>
              수정
            </button>
            <button className="text-red-500" onClick={() => onDelete(c.id)}>
              삭제
            </button>
          </li>
        ))}
      </ul>
      <h3 className="font-bold mt-4">CCTV 추가/수정</h3>
      <form
        className="flex flex-col gap-1"
        onSubmit={e => {
          e.preventDefault();
          // 위치 변환
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
        />
        <input
          placeholder="이름"
          value={form.name || ""}
          onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
          required
        />
        <input
          placeholder="위치 (u,v, 예: 0.5,0.5)"
          value={form.posInput ?? ""}
          onChange={e => setForm(f => ({ ...f, posInput: e.target.value }))}
          required
        />
        <input
          placeholder="방향"
          type="number"
          value={form.direction ?? ""}
          onChange={e => setForm(f => ({ ...f, direction: Number(e.target.value) }))}
          required
        />
        <input
          placeholder="시야각"
          type="number"
          value={form.angle ?? ""}
          onChange={e => setForm(f => ({ ...f, angle: Number(e.target.value) }))}
          required
        />
        <input
          placeholder="길이"
          type="number"
          value={form.length ?? ""}
          onChange={e => setForm(f => ({ ...f, length: Number(e.target.value) }))}
          required
        />
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input
            type="color"
            value={form.color || "#007bff"}
            onChange={e => setForm(f => ({ ...f, color: e.target.value }))}
            style={{ width: 40, height: 30 }}
          />
          <span>마커 색상</span>
        </div>
        <button type="submit" className="bg-blue-500 text-white py-1 mt-2">저장</button>
      </form>
    </div>
  );
}
