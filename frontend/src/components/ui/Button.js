import React from 'react';

const Button = ({ children, variant = 'primary', icon: Icon, onClick, className = '' }) => {
    const baseClass = "btn flex items-center gap-2 justify-center transition-all duration-300 font-medium active:scale-95";

    const variants = {
        primary: "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 border border-indigo-500/50",
        secondary: "bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white border border-gray-700",
        danger: "bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20"
    };

    return (
        <button
            onClick={onClick}
            className={`${baseClass} ${variants[variant]} ${className}`}
        >
            {Icon && <Icon size={18} />}
            {children}
        </button>
    );
};

export default Button;
