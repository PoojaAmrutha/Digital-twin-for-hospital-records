import React from 'react';
import Card from './Card';

const StatCard = ({ title, value, icon: Icon, color, trend, trendUp, subtitle }) => {
    const colorMap = {
        rose: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
        cyan: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
        amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
        violet: 'text-violet-400 bg-violet-500/10 border-violet-500/20',
    };

    const style = colorMap[color] || colorMap.cyan;

    return (
        <Card className="hover:shadow-lg transition-transform hover:-translate-y-1 border-none">
            <div className="flex justify-between items-start">
                <div>
                    <p className="text-gray-400 text-sm font-medium">{title}</p>
                    <div className="flex items-baseline gap-2 mt-1">
                        <h3 className="text-2xl font-bold text-white">{value}</h3>
                    </div>
                </div>
                <div className={`p-2.5 rounded-xl border ${style}`}>
                    <Icon size={20} />
                </div>
            </div>

            <div className="mt-4 flex items-center gap-2 text-sm">
                {trend && (
                    <span className={`font-medium ${trendUp === true ? 'text-emerald-400' : trendUp === false ? 'text-emerald-400' : 'text-gray-400'} flex items-center`}>
                        {trendUp === true && '↑ '}{trendUp === false && '↓ '}{trend}
                    </span>
                )}
                <span className="text-gray-500">{subtitle}</span>
            </div>
        </Card>
    );
};

export default StatCard;
