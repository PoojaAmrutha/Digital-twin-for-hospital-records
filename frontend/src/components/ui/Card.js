import React from 'react';

const Card = ({ children, className = '', hover = true, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={`glass-card p-6 relative overflow-hidden backdrop-blur-xl bg-opacity-60 border-white/5 ${className} ${hover ? 'hover:shadow-neon cursor-pointer transform hover:-translate-y-1' : ''}`}
    >
      {/* Subtle shine effect overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent opacity-0 hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
      {children}
    </div>
  );
};

export default Card;
