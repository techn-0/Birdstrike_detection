import React from "react";
import { MapContainer, ImageOverlay, Marker, Popup, Polygon, Tooltip } from "react-leaflet";
import L from "leaflet";
import { CctvMeta } from "../types";

const bounds: L.LatLngBoundsExpression = [[0, 0], [647, 1000]];
const API = process.env.REACT_APP_API_HTTP;

export default function MapView({
  cctvs,
  detections,
}: {
  cctvs: CctvMeta[];
  detections: any[];
}) {
  const deg2rad = (deg: number) => (deg * Math.PI) / 180;

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
    <MapContainer
      crs={L.CRS.Simple}
      bounds={bounds}
      style={{ height: "90vh", width: "90vw" }}
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

      {/* Detection(알람) 마커: CCTV 위에만 표시 */}
      {detections.map((d, i) => {
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
  );
}
