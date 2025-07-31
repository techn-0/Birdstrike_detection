import React from "react";
import { MapContainer, ImageOverlay, Marker, Popup, Polygon, Tooltip } from "react-leaflet";
import L from "leaflet";
import { CctvMeta } from "../types";

const bounds: L.LatLngBoundsExpression = [[0, 0], [647, 1000]];
const API = process.env.REACT_APP_API_HTTP;

export default function MapView({
  cctvs,
  detections,
  onCctvClick,
}: {
  cctvs: CctvMeta[];
  detections: any[];
  onCctvClick?: (cctvId: string) => void;
}) {
  const deg2rad = (deg: number) => (deg * Math.PI) / 180;

  // CCTV별로 가장 최근 탐지 결과만 추출
  const latestDetectionByCctv: { [cctvId: string]: any } = {};
  detections.forEach((d) => {
    if (
      !latestDetectionByCctv[d.cctv_id] ||
      new Date(d.captured_at) > new Date(latestDetectionByCctv[d.cctv_id].captured_at)
    ) {
      latestDetectionByCctv[d.cctv_id] = d;
    }
  });

  // 동그란 마커 스타일 동적 생성
  function getCctvIcon(color: string) {
    return L.divIcon({
      className: "",
      html: `<div style="
        width:22px;height:22px;
        background:${color};
        border-radius:50%;
        border:2px solid #fff;
        box-shadow:0 0 4px #0003;
        display:flex;align-items:center;justify-content:center;
      "></div>`,
      iconSize: [22, 22],
      iconAnchor: [11, 11],
    });
  }

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <MapContainer
        crs={L.CRS.Simple}
        bounds={bounds}
        style={{ height: "100%", width: "100%" }}
        zoom={0}           // 초기 확대 레벨
        minZoom={-2}       // 더 멀리까지 축소 가능
        maxZoom={4}        // 더 가까이까지 확대 가능
        zoomDelta={0.25}   // 확대/축소 단위(기본은 1, 더 작게 하면 더 세밀)
        zoomSnap={0.25}    // 마우스 휠 등으로 확대/축소할 때 스냅 단위
      >
        <ImageOverlay url="/airport_bg.png" bounds={bounds} />

        {/* CCTV 마커와 FOV */}
        {cctvs.map((c) => {
          const markerPos: [number, number] = [c.pos[1] * 647, c.pos[0] * 1000];
          const center: [number, number] = [c.pos[1] * 647, c.pos[0] * 1000];
          const half = c.angle / 2;
          const rad1 = deg2rad(c.direction - half);
          const rad2 = deg2rad(c.direction + half);
          const left: [number, number] = [
            (c.pos[1] + c.length * Math.sin(rad1)) * 647,
            (c.pos[0] + c.length * Math.cos(rad1)) * 1000,
          ];
          const right: [number, number] = [
            (c.pos[1] + c.length * Math.sin(rad2)) * 647,
            (c.pos[0] + c.length * Math.cos(rad2)) * 1000,
          ];
          const polyCoords = [center, left, right];
          const color = c.color || "#007bff";

          return (
            <React.Fragment key={c.id}>
              <Marker
                position={markerPos}
                icon={getCctvIcon(color)}
                eventHandlers={{
                  click: () => onCctvClick && onCctvClick(c.id),
                }}
              >
                <Tooltip direction="bottom" offset={[0, 12]} permanent>
                  <span style={{ color: "#222", fontWeight: "bold", background: "#fff8", padding: "2px 6px", borderRadius: 4 }}>
                    {c.name}
                  </span>
                </Tooltip>
                <Popup>
                  CCTV {c.name} ({c.id})
                </Popup>
              </Marker>
              <Polygon
                positions={polyCoords}
                pathOptions={{
                  color: color,
                  weight: 2,
                  fillOpacity: 0.15,
                  fillColor: color,
                }}
              />
            </React.Fragment>
          );
        })}

        {/* 각 CCTV별로 가장 최근 탐지 결과만 위험도 마커로 표시 */}
        {Object.values(latestDetectionByCctv).map((d: any, i) => {
          const cctv = cctvs.find((c) => c.id === d.cctv_id);
          if (!cctv) return null;
          const markerPos: [number, number] = [cctv.pos[1] * 647, cctv.pos[0] * 1000];
          return (
            <Marker
              key={i}
              position={markerPos}
              icon={L.divIcon({ className: `risk-${d.risk}` })}
            >
              <Popup>
                <b>탐지!</b>
                <br />
                CCTV {d.cctv_id}
                <br />
                Risk: {d.risk}
                <br />
                {d.frame_url && (
                  <img src={`${API}${d.frame_url}`} alt="frame" width={200} />
                )}
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </div>
  );
}
