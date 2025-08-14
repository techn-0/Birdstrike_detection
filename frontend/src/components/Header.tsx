import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LoginModal } from './LoginModal';

interface HeaderProps {
  // 나중에 추가할 props
  // user?: { name: string } | null;
  // onLogin?: () => void;
  // onLogout?: () => void;
}

export default function Header({}: HeaderProps) {
  const { user, logout, isAdmin } = useAuth();
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  const handleLogout = async () => {
    await logout();
  };

  return (
    <>
      <div 
        style={{ 
          height: "60px", 
          backgroundColor: "rgba(255, 255, 255, 0.95)", 
          backdropFilter: "blur(10px)", 
          borderBottom: "1px solid #e5e5e5",
          zIndex: 1000,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 20px",
          flexShrink: 0 // 높이가 줄어들지 않도록
        }}
      >
        {/* 좌측: 제목 */}
        <h1 style={{ margin: 0, fontSize: "20px", fontWeight: "bold", color: "#2563eb" }}>
          Birdstrike Detection
        </h1>
        
        {/* 우측: 로그인 관련 버튼들 */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          {user ? (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <span style={{ fontSize: "14px", color: "#374151" }}>
                  안녕하세요, <span style={{ fontWeight: "600" }}>{user.name}</span>
                </span>
                {isAdmin() && (
                  <span style={{
                    backgroundColor: "#fbbf24",
                    color: "#92400e",
                    padding: "2px 8px",
                    borderRadius: "12px",
                    fontSize: "12px",
                    fontWeight: "500"
                  }}>
                    관리자
                  </span>
                )}
              </div>
              <button 
                onClick={handleLogout}
                style={{
                  backgroundColor: "#ef4444",
                  color: "white",
                  padding: "8px 16px",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontWeight: "500",
                  transition: "background-color 0.2s"
                }}
                onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#dc2626"}
                onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#ef4444"}
              >
                로그아웃
              </button>
            </>
          ) : (
            <button 
              onClick={() => setIsLoginModalOpen(true)}
              style={{
                backgroundColor: "#3b82f6",
                color: "white",
                padding: "8px 16px",
                border: "none",
                borderRadius: "6px",
                cursor: "pointer",
                fontWeight: "500",
                transition: "background-color 0.2s"
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = "#2563eb"}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = "#3b82f6"}
            >
              로그인
            </button>
          )}
        </div>
      </div>

      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
      />
    </>
  );
}