import React, { useState, useEffect, useRef, useCallback } from 'react';
import { PhotoSlidesData, PhotoSlideImage, DetectionLabel } from '../types';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  cctvId: string;
  cctvName: string;
}

const API = process.env.REACT_APP_API_HTTP;

export default function PhotoSlidesModal({ isOpen, onClose, cctvId, cctvName }: Props) {
  const [data, setData] = useState<PhotoSlidesData | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1000); // 밀리초
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [confidenceThreshold, setConfidenceThreshold] = useState(0.3);
  const [showLabels, setShowLabels] = useState(true);
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // 이미지에 라벨 그리기
  const drawLabelsOnCanvas = useCallback((image: PhotoSlideImage, imgElement: HTMLImageElement) => {
    const canvas = canvasRef.current;
    if (!canvas || !showLabels || !imgElement) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // 이미지의 실제 표시 크기 계산
    const rect = imgElement.getBoundingClientRect();
    const scaleX = rect.width / imgElement.naturalWidth;
    const scaleY = rect.height / imgElement.naturalHeight;

    // 캔버스 크기를 표시되는 이미지 크기에 맞춤
    canvas.width = rect.width;
    canvas.height = rect.height;

    // 캔버스 초기화
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 라벨 그리기 (스케일 적용)
    image.labels.forEach((label: DetectionLabel) => {
      const { x1, y1, x2, y2, confidence, class_name } = label;
      
      // 좌표를 표시 크기에 맞게 스케일링
      const scaledX1 = x1 * scaleX;
      const scaledY1 = y1 * scaleY;
      const scaledX2 = x2 * scaleX;
      const scaledY2 = y2 * scaleY;
      
      // 바운딩 박스 그리기
      ctx.strokeStyle = confidence >= 0.7 ? '#ff0000' : confidence >= 0.5 ? '#ff8800' : '#ffff00';
      ctx.lineWidth = 2;
      ctx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1);

      // 라벨 텍스트 배경
      const textHeight = 20;
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      ctx.fillRect(scaledX1, scaledY1 - textHeight, 120, textHeight);

      // 라벨 텍스트
      ctx.fillStyle = '#ffffff';
      ctx.font = '12px Arial';
      ctx.fillText(`${class_name} ${(confidence * 100).toFixed(1)}%`, scaledX1 + 3, scaledY1 - 5);
    });
  }, [showLabels]);

  const loadPhotoSlidesData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API}/api/photo-slides/${cctvId}?confidence_threshold=${confidenceThreshold}`);
      if (!response.ok) {
        throw new Error('데이터를 불러올 수 없습니다.');
      }
      const result: PhotoSlidesData = await response.json();
      setData(result);
      setCurrentIndex(0);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [cctvId, confidenceThreshold]);

  // 데이터 로드
  useEffect(() => {
    if (isOpen && cctvId) {
      loadPhotoSlidesData();
    }
  }, [isOpen, cctvId, loadPhotoSlidesData]);

  // 자동 재생 제어
  useEffect(() => {
    if (isPlaying && data && data.images.length > 0) {
      intervalRef.current = setInterval(() => {
        setCurrentIndex(prev => (prev + 1) % data.images.length);
      }, speed);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isPlaying, speed, data]);

  // 컴포넌트 언마운트 시 정리
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // 라벨 표시 상태나 현재 인덱스가 변경될 때 캔버스 다시 그리기
  useEffect(() => {
    if (data && data.images[currentIndex]) {
      const imgElement = document.querySelector(`img[alt="${data.images[currentIndex].image_name}"]`) as HTMLImageElement;
      if (imgElement && imgElement.complete) {
        drawLabelsOnCanvas(data.images[currentIndex], imgElement);
      }
    }
  }, [showLabels, currentIndex, data, drawLabelsOnCanvas]);

  const handleImageLoad = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const imgElement = e.currentTarget;
    if (data && data.images[currentIndex] && showLabels) {
      // 이미지 로드 후 약간의 지연을 두고 라벨 그리기
      setTimeout(() => {
        drawLabelsOnCanvas(data.images[currentIndex], imgElement);
      }, 100);
    }
  };

  if (!isOpen) return null;

  console.log('PhotoSlidesModal 렌더링:', { isOpen, cctvId, cctvName });

  return (
    <div 
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(0, 0, 0, 0.9)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 99999
      }}
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div style={{
        backgroundColor: "#ffffff",
        borderRadius: "12px",
        maxWidth: "90vw",
        maxHeight: "95vh",
        width: "1200px",
        margin: "0 16px",
        display: "flex",
        flexDirection: "column",
        boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.5)",
        border: "2px solid #374151",
        position: "relative"
      }}>
        {/* 헤더 */}
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "20px 24px",
          borderBottom: "2px solid #e5e5e5",
          backgroundColor: "#ffffff",
          borderRadius: "12px 12px 0 0"
        }}>
          <h2 style={{
            margin: 0,
            fontSize: "20px",
            fontWeight: "bold",
            color: "#2563eb"
          }}>
            📸 {cctvName} - 포토 슬라이드
          </h2>
          <button 
            onClick={onClose}
            style={{
              background: "none",
              border: "none",
              fontSize: "24px",
              color: "#6b7280",
              cursor: "pointer",
              padding: "4px 8px",
              borderRadius: "6px",
              transition: "all 0.2s"
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.color = "#374151";
              e.currentTarget.style.backgroundColor = "#f3f4f6";
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.color = "#6b7280";
              e.currentTarget.style.backgroundColor = "transparent";
            }}
          >
            ×
          </button>
        </div>

        {/* 컨트롤 패널 */}
        <div style={{
          padding: "16px 24px",
          borderBottom: "1px solid #e5e5e5",
          backgroundColor: "#f9fafb"
        }}>
          <div style={{
            display: "flex",
            flexWrap: "wrap",
            gap: "16px",
            alignItems: "center"
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <label style={{ fontSize: "14px", fontWeight: "500", color: "#374151" }}>
                신뢰도 임계값:
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={confidenceThreshold}
                onChange={(e) => {
                  setLoading(true); // 즉시 로딩 상태 시작
                  setConfidenceThreshold(Number(e.target.value));
                }}
                style={{ width: "80px" }}
              />
              <span style={{
                fontSize: "14px",
                fontWeight: "600",
                color: "#2563eb",
                minWidth: "36px"
              }}>
                {(confidenceThreshold * 100).toFixed(0)}%
              </span>
            </div>
            
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <label style={{ fontSize: "14px", fontWeight: "500", color: "#374151" }}>
                속도:
              </label>
              <select 
                value={speed} 
                onChange={(e) => setSpeed(Number(e.target.value))}
                style={{
                  border: "1px solid #d1d5db",
                  borderRadius: "6px",
                  padding: "4px 8px",
                  fontSize: "14px",
                  backgroundColor: "white"
                }}
              >
                <option value={2000}>느림 (2초)</option>
                <option value={1000}>보통 (1초)</option>
                <option value={500}>빠름 (0.5초)</option>
                <option value={200}>매우 빠름 (0.2초)</option>
              </select>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <input
                type="checkbox"
                checked={showLabels}
                onChange={(e) => setShowLabels(e.target.checked)}
                id="showLabels"
                style={{ marginRight: "4px" }}
              />
              <label htmlFor="showLabels" style={{ fontSize: "14px", fontWeight: "500", color: "#374151" }}>
                라벨 표시
              </label>
            </div>

            <div style={{ display: "flex", gap: "8px" }}>
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                style={{
                  padding: "8px 16px",
                  borderRadius: "6px",
                  border: "none",
                  fontSize: "14px",
                  fontWeight: "500",
                  cursor: "pointer",
                  transition: "all 0.2s",
                  backgroundColor: isPlaying ? "#ef4444" : "#22c55e",
                  color: "white"
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = isPlaying ? "#dc2626" : "#16a34a";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = isPlaying ? "#ef4444" : "#22c55e";
                }}
              >
                {isPlaying ? '⏸ 일시정지' : '▶ 재생'}
              </button>
              
              <button
                onClick={() => setCurrentIndex(0)}
                style={{
                  padding: "8px 16px",
                  backgroundColor: "#6b7280",
                  color: "white",
                  border: "none",
                  borderRadius: "6px",
                  fontSize: "14px",
                  fontWeight: "500",
                  cursor: "pointer",
                  transition: "all 0.2s"
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = "#4b5563";
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = "#6b7280";
                }}
              >
                ⏮ 처음
              </button>
            </div>
          </div>

          {data && (
            <div style={{
              marginTop: "12px",
              fontSize: "14px",
              color: "#6b7280"
            }}>
              총 {data.total_images}개 이미지 | 현재: {currentIndex + 1}/{data.images.length} | 
              신뢰도 {(confidenceThreshold * 100).toFixed(0)}% 이상
            </div>
          )}
        </div>

        {/* 메인 콘텐츠 */}
        <div style={{
          flex: 1,
          padding: "24px",
          overflowY: "auto",
          backgroundColor: "#ffffff",
          borderRadius: "0 0 12px 12px"
        }}>
          {loading && (
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "300px"
            }}>
              <div style={{
                color: "#6b7280",
                fontSize: "16px",
                fontWeight: "500"
              }}>
                데이터를 불러오는 중...
              </div>
            </div>
          )}

          {error && (
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "300px"
            }}>
              <div style={{
                color: "#ef4444",
                fontSize: "16px",
                fontWeight: "500"
              }}>
                {error}
              </div>
            </div>
          )}

          {data && data.images.length === 0 && (
            <div style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              height: "300px"
            }}>
              <div style={{
                color: "#6b7280",
                fontSize: "16px",
                fontWeight: "500"
              }}>
                신뢰도 {(confidenceThreshold * 100).toFixed(0)}% 이상의 이미지가 없습니다.
              </div>
            </div>
          )}

          {data && data.images.length > 0 && !loading && (
            <div style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center"
            }}>
              <div style={{
                position: "relative",
                display: "inline-block",
                border: "2px solid #e5e7eb",
                borderRadius: "12px",
                overflow: "hidden",
                boxShadow: "0 10px 25px -3px rgba(0, 0, 0, 0.1)"
              }}>
                <img
                  src={`${API}${data.images[currentIndex].image_url}`}
                  alt={data.images[currentIndex].image_name}
                  style={{
                    maxWidth: "100%",
                    maxHeight: "60vh",
                    display: "block"
                  }}
                  onLoad={(e) => {
                    console.log('이미지 로드 성공:', `${API}${data.images[currentIndex].image_url}`);
                    handleImageLoad(e);
                  }}
                  onError={(e) => {
                    console.error('이미지 로드 실패:', `${API}${data.images[currentIndex].image_url}`);
                    console.error('Error details:', e);
                    setError('이미지를 불러올 수 없습니다.');
                  }}
                />
                
                {showLabels && (
                  <canvas 
                    ref={canvasRef}
                    style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      maxWidth: "100%",
                      maxHeight: "60vh",
                      pointerEvents: "none",
                      zIndex: 1
                    }}
                  />
                )}
              </div>

              <div style={{
                marginTop: "20px",
                textAlign: "center"
              }}>
                <h3 style={{
                  fontSize: "18px",
                  fontWeight: "600",
                  color: "#1f2937",
                  margin: "0 0 8px 0"
                }}>
                  {data.images[currentIndex].image_name}
                </h3>
                <p style={{
                  fontSize: "14px",
                  color: "#6b7280",
                  margin: 0
                }}>
                  최대 신뢰도: <span style={{ fontWeight: "600", color: "#2563eb" }}>
                    {(data.images[currentIndex].max_confidence * 100).toFixed(1)}%
                  </span> | 
                  탐지 개수: <span style={{ fontWeight: "600", color: "#16a34a" }}>
                    {data.images[currentIndex].detection_count}개
                  </span>
                </p>
              </div>

              {/* 이미지 네비게이션 */}
              <div style={{
                display: "flex",
                gap: "12px",
                marginTop: "20px"
              }}>
                <button
                  onClick={() => setCurrentIndex(prev => Math.max(0, prev - 1))}
                  disabled={currentIndex === 0}
                  style={{
                    padding: "8px 16px",
                    backgroundColor: currentIndex === 0 ? "#e5e7eb" : "#3b82f6",
                    color: currentIndex === 0 ? "#9ca3af" : "white",
                    border: "none",
                    borderRadius: "6px",
                    fontSize: "14px",
                    fontWeight: "500",
                    cursor: currentIndex === 0 ? "not-allowed" : "pointer",
                    transition: "all 0.2s"
                  }}
                  onMouseOver={(e) => {
                    if (currentIndex !== 0) {
                      e.currentTarget.style.backgroundColor = "#2563eb";
                    }
                  }}
                  onMouseOut={(e) => {
                    if (currentIndex !== 0) {
                      e.currentTarget.style.backgroundColor = "#3b82f6";
                    }
                  }}
                >
                  ← 이전
                </button>
                <button
                  onClick={() => setCurrentIndex(prev => Math.min(data.images.length - 1, prev + 1))}
                  disabled={currentIndex === data.images.length - 1}
                  style={{
                    padding: "8px 16px",
                    backgroundColor: currentIndex === data.images.length - 1 ? "#e5e7eb" : "#3b82f6",
                    color: currentIndex === data.images.length - 1 ? "#9ca3af" : "white",
                    border: "none",
                    borderRadius: "6px",
                    fontSize: "14px",
                    fontWeight: "500",
                    cursor: currentIndex === data.images.length - 1 ? "not-allowed" : "pointer",
                    transition: "all 0.2s"
                  }}
                  onMouseOver={(e) => {
                    if (currentIndex !== data.images.length - 1) {
                      e.currentTarget.style.backgroundColor = "#2563eb";
                    }
                  }}
                  onMouseOut={(e) => {
                    if (currentIndex !== data.images.length - 1) {
                      e.currentTarget.style.backgroundColor = "#3b82f6";
                    }
                  }}
                >
                  다음 →
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
