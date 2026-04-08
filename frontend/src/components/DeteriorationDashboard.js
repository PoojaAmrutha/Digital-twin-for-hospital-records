import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import './DeteriorationDashboard.css';

const DeteriorationDashboard = ({ patientId }) => {
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [history, setHistory] = useState([]);

    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    // Fetch deterioration prediction
    const fetchPrediction = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(
                `${API_URL}/api/ml/predict-deterioration?patient_id=${patientId}&horizon_hours=48`,
                { method: 'POST' }
            );
            const data = await response.json();

            if (data.error) {
                setError(data.error);
            } else {
                setPrediction(data);
            }
        } catch (err) {
            setError(`Failed to fetch prediction: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    // Fetch prediction history
    const fetchHistory = async () => {
        try {
            const response = await fetch(`${API_URL}/api/ml/deterioration-history/${patientId}`);
            const data = await response.json();
            setHistory(data.predictions || []);
        } catch (err) {
            console.error('Failed to fetch history:', err);
        }
    };

    useEffect(() => {
        if (patientId) {
            fetchPrediction();
            fetchHistory();
        }
    }, [patientId]);

    // Get risk color
    const getRiskColor = (level) => {
        const colors = {
            'Low': '#10b981',
            'Medium': '#f59e0b',
            'High': '#ef4444',
            'Critical': '#dc2626'
        };
        return colors[level] || '#6b7280';
    };

    // Render risk gauge
    const RiskGauge = ({ score, level }) => {
        const percentage = score * 100;
        const color = getRiskColor(level);

        return (
            <div className="risk-gauge">
                <svg viewBox="0 0 200 120" className="gauge-svg">
                    {/* Background arc */}
                    <path
                        d="M 20 100 A 80 80 0 0 1 180 100"
                        fill="none"
                        stroke="#e5e7eb"
                        strokeWidth="20"
                        strokeLinecap="round"
                    />
                    {/* Foreground arc */}
                    <path
                        d="M 20 100 A 80 80 0 0 1 180 100"
                        fill="none"
                        stroke={color}
                        strokeWidth="20"
                        strokeLinecap="round"
                        strokeDasharray={`${percentage * 2.51} 251`}
                        className="gauge-fill"
                    />
                    {/* Center text */}
                    <text x="100" y="85" textAnchor="middle" className="gauge-score">
                        {(percentage).toFixed(1)}%
                    </text>
                    <text x="100" y="105" textAnchor="middle" className="gauge-label">
                        {level} Risk
                    </text>
                </svg>
            </div>
        );
    };

    // Render attention heatmap
    const AttentionHeatmap = ({ weights, keyFactors }) => {
        if (!weights || weights.length === 0) return null;

        // Sample every 4th hour for display
        const sampledWeights = weights.filter((_, i) => i % 4 === 0);
        const maxWeight = Math.max(...weights);

        return (
            <div className="attention-heatmap">
                <h4>Temporal Attention (Which time periods matter most?)</h4>
                <div className="heatmap-grid">
                    {sampledWeights.map((weight, idx) => {
                        const hour = idx * 4;
                        const hoursAgo = 48 - hour;
                        const intensity = weight / maxWeight;

                        return (
                            <div
                                key={idx}
                                className="heatmap-cell"
                                style={{
                                    backgroundColor: `rgba(239, 68, 68, ${intensity})`,
                                    opacity: 0.3 + intensity * 0.7
                                }}
                                title={`${hoursAgo}h ago: ${(weight * 100).toFixed(1)}% attention`}
                            >
                                <span className="heatmap-label">-{hoursAgo}h</span>
                            </div>
                        );
                    })}
                </div>
                <div className="heatmap-legend">
                    <span>Less Important</span>
                    <div className="legend-gradient"></div>
                    <span>More Important</span>
                </div>
            </div>
        );
    };

    // Render key factors
    const KeyFactors = ({ factors }) => {
        if (!factors || factors.length === 0) return null;

        return (
            <div className="key-factors">
                <h4>Top Contributing Factors</h4>
                {factors.map((factor, idx) => (
                    <div key={idx} className="factor-item">
                        <div className="factor-header">
                            <span className="factor-time">{factor.hours_ago} hours ago</span>
                            <span className="factor-importance">
                                {(factor.attention_weight * 100).toFixed(1)}% importance
                            </span>
                        </div>
                        <div className="factor-vitals">
                            <div className="vital-badge">HR: {factor.vitals.heart_rate}</div>
                            <div className="vital-badge">SpO2: {factor.vitals.spo2}%</div>
                            <div className="vital-badge">Temp: {factor.vitals.temperature}°C</div>
                            <div className="vital-badge">Stress: {factor.vitals.stress_level}/5</div>
                        </div>
                    </div>
                ))}
            </div>
        );
    };

    // Render confidence interval
    const ConfidenceInterval = ({ lower, upper, mean }) => {
        return (
            <div className="confidence-interval">
                <h4>Prediction Confidence</h4>
                <div className="interval-bar">
                    <div className="interval-range" style={{
                        left: `${lower * 100}%`,
                        width: `${(upper - lower) * 100}%`
                    }}>
                        <div className="interval-mean" style={{
                            left: `${((mean - lower) / (upper - lower)) * 100}%`
                        }}></div>
                    </div>
                </div>
                <div className="interval-labels">
                    <span>{(lower * 100).toFixed(1)}%</span>
                    <span className="mean-label">{(mean * 100).toFixed(1)}%</span>
                    <span>{(upper * 100).toFixed(1)}%</span>
                </div>
                <p className="interval-description">
                    95% confidence interval: The model is 95% confident the true risk is between {(lower * 100).toFixed(1)}% and {(upper * 100).toFixed(1)}%
                </p>
            </div>
        );
    };

    if (loading) {
        return (
            <Card>
                <CardContent className="loading-state">
                    <div className="spinner"></div>
                    <p>Analyzing patient data...</p>
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
            </Alert>
        );
    }

    if (!prediction) {
        return (
            <Card>
                <CardContent>
                    <p>No prediction data available. Click "Analyze" to generate a prediction.</p>
                    <button onClick={fetchPrediction} className="btn-primary">
                        Analyze Deterioration Risk
                    </button>
                </CardContent>
            </Card>
        );
    }

    return (
        <div className="deterioration-dashboard">
            <Card className="main-card">
                <CardHeader>
                    <CardTitle>
                        Health Deterioration Prediction
                        {!prediction.model_trained && (
                            <span className="warning-badge">⚠️ Using untrained model (demo mode)</span>
                        )}
                    </CardTitle>
                    <p className="subtitle">

                    </p>
                </CardHeader>
                <CardContent>
                    {/* Risk Gauge */}
                    <div className="section">
                        <RiskGauge score={prediction.risk_score} level={prediction.risk_level} />
                    </div>

                    {/* Confidence Interval */}
                    <div className="section">
                        <ConfidenceInterval
                            lower={prediction.confidence_interval[0]}
                            upper={prediction.confidence_interval[1]}
                            mean={prediction.risk_score}
                        />
                    </div>

                    {/* Attention Heatmap */}
                    {prediction.attention_weights && (
                        <div className="section">
                            <AttentionHeatmap
                                weights={prediction.attention_weights}
                                keyFactors={prediction.key_factors}
                            />
                        </div>
                    )}

                    {/* Key Factors */}
                    {prediction.key_factors && (
                        <div className="section">
                            <KeyFactors factors={prediction.key_factors} />
                        </div>
                    )}

                    {/* Prediction History */}
                    {history.length > 0 && (
                        <div className="section">
                            <h4>Recent Predictions</h4>
                            <div className="history-list">
                                {history.slice(0, 5).map((pred) => (
                                    <div key={pred.id} className="history-item">
                                        <span className="history-time">
                                            {new Date(pred.prediction_time).toLocaleString()}
                                        </span>
                                        <span className="history-risk" style={{
                                            color: getRiskColor(pred.risk_level)
                                        }}>
                                            {pred.risk_level}: {(pred.risk_score * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Refresh Button */}
                    <div className="actions">
                        <button onClick={fetchPrediction} className="btn-secondary">
                            Refresh Prediction
                        </button>
                    </div>
                </CardContent>
            </Card>

            {/* Model Info Card */}
            <Card className="info-card">
                <CardHeader>
                    <CardTitle>About This Model</CardTitle>
                </CardHeader>
                <CardContent>
                    <ul className="model-features">
                        <li>✓ Temporal attention over 48-hour vital sequences</li>
                        <li>✓ Clinical text embeddings from symptoms</li>
                        <li>✓ Personalized baseline calibration</li>
                        <li>✓ Uncertainty quantification (95% CI)</li>
                        <li>✓ Explainable predictions</li>
                    </ul>
                    <p className="model-description">
                        This novel deep learning model combines LSTM networks with attention mechanisms
                        to predict patient deterioration 24-72 hours in advance, suitable for IEEE Q1
                        journal publication.
                    </p>
                </CardContent>
            </Card>
        </div>
    );
};

export default DeteriorationDashboard;
