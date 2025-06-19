import React from "react";
import { MapContainer, ImageOverlay, Marker, Popup, Polygon } from "react-leaflet";
import L from "leaflet";

interface Det {
  _id?: string;
  cctv_id: string;
  pos: [number, number];      // [u,v] 0~1
  risk: "red" | "orange" | "yellow" | "green";
  frame_url?: string;
  fov?: {
    direction: number; // 중심 방향 (도)
    angle: number;     // 시야각 (도)
    length: number;    // 시야 거리 (0~1)
  };
}

const bounds: L.LatLngBoundsExpression = [[0, 0], [647, 1000]]; // 배경 해상도 세로, 가로
const API = process.env.REACT_APP_API_HTTP;   // http://localhost:8000

export default function MapView({ detections }: { detections: Det[] }) {
  // 각도(도) → 라디안 변환 함수
  const deg2rad = (deg: number) => (deg * Math.PI) / 180;

  return (
    <MapContainer
      crs={L.CRS.Simple}
      bounds={bounds}
      style={{ height: "90vh", width: "90vw" }}
    >
      <ImageOverlay url="/airport_bg.png" bounds={bounds} />

      {detections.map((d, i) => {
        // 1) 마커 위치 계산
        const markerPos: [number, number] = [d.pos[1] * 647, d.pos[0] * 1000];

        // 2) fov가 각도 정보일 때 삼각형 꼭짓점 계산
        let polyCoords: [number, number][] | undefined = undefined;
        if (d.fov) {
          const { direction, angle, length } = d.fov;
          const [u, v] = d.pos;
          // 중심점(카메라)
          const center: [number, number] = [v * 647, u * 1000];
          // 좌우 끝점 계산
          const half = angle / 2;
          const rad1 = deg2rad(direction - half);
          const rad2 = deg2rad(direction + half);
          // Leaflet 좌표계: [y, x] = [v*647, u*1000]
          const left: [number, number] = [
            (v + length * Math.sin(rad1)) * 647,
            (u + length * Math.cos(rad1)) * 1000,
          ];
          const right: [number, number] = [
            (v + length * Math.sin(rad2)) * 647,
            (u + length * Math.cos(rad2)) * 1000,
          ];
          polyCoords = [center, left, right];
        }

        return (
          <React.Fragment key={i}>
            {/* 마커 */}
            <Marker
              position={markerPos}
              icon={L.divIcon({ className: `risk-${d.risk}` })}
            >
              <Popup>
                CCTV {d.cctv_id}<br />
                Risk: {d.risk}<br />
                {d.frame_url && (
                  <img src={`${API}${d.frame_url}`} alt="frame" width={200} />
                )}
              </Popup>
            </Marker>

            {/* FOV 다각형 */}
            {polyCoords && (
              <Polygon
                positions={polyCoords}
                pathOptions={{
                  color:
                    d.risk === "red"
                      ? "#f03"
                      : d.risk === "orange"
                      ? "#f80"
                      : d.risk === "yellow"
                      ? "#fc0"
                      : "#0a0",
                  weight: 2,
                  fillOpacity: 0.1,
                }}
              />
            )}
          </React.Fragment>
        );
      })}
    </MapContainer>
  );
}
