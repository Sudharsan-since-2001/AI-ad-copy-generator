import { useState } from 'react'
import { generateAds, type AdRequest, type AdResponse } from './api'

function App() {
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [data, setData] = useState<AdResponse | null>(null)
    const [editingIndex, setEditingIndex] = useState<number | null>(null)
    const [editedVariation, setEditedVariation] = useState<{ headline: string; primary_text: string; cta: string } | null>(null)
    const [formData, setFormData] = useState<AdRequest>({
        product_name: '',
        description: '',
        target_audience: '',
        platform: 'Instagram',
        campaign_goal: 'Sales',
        tone: 'Professional',
        framework: 'AIDA'
    })

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        setData(null) // Clear previous data
        try {
            console.log('Submitting form with data:', formData)
            const resp = await generateAds(formData)
            console.log('Received response:', resp)
            // Validate response has required fields
            if (!resp || !resp.insights || !resp.variations || !resp.compliance || !resp.channel_opt) {
                throw new Error('Invalid response format from server')
            }
            // Ensure new fields exist with defaults
            if (!resp.insights.demographics) {
                resp.insights.demographics = 'Not specified'
            }
            if (!resp.insights.targeting_interests || resp.insights.targeting_interests.length === 0) {
                resp.insights.targeting_interests = ['Online shopping', 'Fashion', 'Lifestyle']
            }
            if (!resp.insights.behaviors || resp.insights.behaviors.length === 0) {
                resp.insights.behaviors = ['Frequent online shoppers', 'Engages with brand content']
            }
            setData(resp)
        } catch (err: any) {
            console.error('Error generating ads:', err)
            const errorMessage = err.message || 'Failed to generate ad copies. Please check your connection and try again.'
            setError(errorMessage)
        } finally {
            setLoading(false)
        }
    }

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text)
        const btn = document.activeElement as HTMLButtonElement;
        const originalText = btn.innerHTML;
        btn.innerHTML = 'COPIED';
        setTimeout(() => { btn.innerHTML = originalText; }, 2000);
    }

    const handleEdit = (index: number) => {
        if (data) {
            const variation = data.variations[index]
            setEditingIndex(index)
            setEditedVariation({
                headline: variation.headline,
                primary_text: variation.primary_text,
                cta: variation.cta
            })
        }
    }

    const handleSaveEdit = (index: number) => {
        if (data && editedVariation) {
            const updatedVariations = [...data.variations]
            updatedVariations[index] = {
                ...updatedVariations[index],
                headline: editedVariation.headline,
                primary_text: editedVariation.primary_text,
                cta: editedVariation.cta
            }
            setData({
                ...data,
                variations: updatedVariations
            })
            setEditingIndex(null)
            setEditedVariation(null)
        }
    }

    const handleCancelEdit = () => {
        setEditingIndex(null)
        setEditedVariation(null)
    }

    return (
        <div className="app-wrapper">
            <div className="main-content">
                {/* SIDEBAR MODULE */}
                <aside className="sidebar">
                    <div className="brand-cloud">
                        <h1>AI Copy Ad Generator</h1>
                    </div>

                    <form onSubmit={handleSubmit}>
                        <div className="form-section">
                            <span className="section-lbl">Campaign Configuration</span>
                            <div className="field-group">
                                <label className="field-label">Product Name</label>
                                <input
                                    type="text"
                                    placeholder="e.g. Lavender Dream Mist"
                                    required
                                    value={formData.product_name}
                                    onChange={e => setFormData({ ...formData, product_name: e.target.value })}
                                />
                            </div>

                            <div className="field-group">
                                <label className="field-label">Short Description</label>
                                <textarea
                                    rows={4}
                                    placeholder="Explain the core benefit..."
                                    required
                                    value={formData.description}
                                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="form-section" style={{ marginTop: '2rem' }}>
                            <span className="section-lbl">Targeting Strategy</span>
                            <div className="field-group">
                                <label className="field-label">Target Audience</label>
                                <input
                                    type="text"
                                    placeholder="e.g. Stressed Professionals"
                                    required
                                    value={formData.target_audience}
                                    onChange={e => setFormData({ ...formData, target_audience: e.target.value })}
                                />
                            </div>

                            <div className="field-group">
                                <label className="field-label">Platform</label>
                                <select value={formData.platform} onChange={e => setFormData({ ...formData, platform: e.target.value })}>
                                    <option>Instagram</option>
                                    <option>Facebook</option>
                                    <option>LinkedIn</option>
                                    <option>WhatsApp</option>
                                </select>
                            </div>

                            <div className="field-group">
                                <label className="field-label">Marketing Framework</label>
                                <select value={formData.framework} onChange={e => setFormData({ ...formData, framework: e.target.value })}>
                                    <option>AIDA</option>
                                    <option>PAS</option>
                                    <option>Problem-Solution</option>
                                    <option>Urgency-Scarcity</option>
                                </select>
                            </div>

                            <div className="field-group">
                                <label className="field-label">Ad Tone</label>
                                <select value={formData.tone} onChange={e => setFormData({ ...formData, tone: e.target.value })}>
                                    <option>Professional</option>
                                    <option>Emotional</option>
                                    <option>Casual</option>
                                    <option>Urgent</option>
                                </select>
                            </div>
                        </div>

                        <button type="submit" className="btn-dream" disabled={loading} style={{ marginTop: '2.5rem' }}>
                            {loading ? 'Synthesizing...' : 'Execute Synthesis'}
                        </button>
                    </form>
                    {error && (
                        <div style={{
                            marginTop: '2rem',
                            padding: '1rem',
                            background: 'rgba(255, 181, 216, 0.1)',
                            border: '1px solid rgba(255, 181, 216, 0.3)',
                            borderRadius: '8px',
                            fontSize: '0.85rem',
                            color: '#ffb5d8',
                            textAlign: 'center'
                        }}>
                            <strong>Error:</strong> {error}
                        </div>
                    )}
                </aside>

                {/* RESULT CANVAS */}
                <main className="canvas">
                    {!data && !loading && !error && (
                        <div className="dream-state fade-in-blur">
                            <h2 style={{ fontSize: '3.5rem', fontFamily: 'Playfair Display' }}>Campaign Headquarters</h2>
                            <p style={{ color: 'var(--text-dim)', fontSize: '1.2rem' }}>Enter your product details to generate high-converting ad copy.</p>
                        </div>
                    )}

                    {error && !loading && (
                        <div className="dream-state fade-in-blur" style={{ textAlign: 'center' }}>
                            <h2 style={{ fontSize: '2.5rem', fontFamily: 'Playfair Display', color: '#ffb5d8', marginBottom: '1rem' }}>Error</h2>
                            <p style={{ color: 'var(--text-dim)', fontSize: '1.1rem', marginBottom: '2rem' }}>{error}</p>
                            <button
                                onClick={() => { setError(null); setData(null); }}
                                className="btn-dream"
                                style={{ marginTop: '1rem' }}
                            >
                                Try Again
                            </button>
                        </div>
                    )}

                    {loading && (
                        <div className="dream-state">
                            <h2 style={{ marginTop: '2rem', letterSpacing: '0.2em' }}>GENERATING COPIES...</h2>
                        </div>
                    )}

                    {data && !loading && (
                        <>
                            {/* HEADER */}
                            <div className="campaign-header fade-in-blur" style={{ gridColumn: 'span 2', marginBottom: '2rem' }}>
                                <h1 className="header-title">Ad Campaign Results</h1>
                                <p className="header-subtitle">
                                    {formData.product_name} • {formData.platform} • {formData.target_audience} • {formData.framework} Framework
                                </p>
                            </div>

                            {/* INTELLIGENCE PANEL - Left Side */}
                            <div className="cloud-card blob-1 fade-in-blur">
                                {/* Pain Points Section */}
                                <div className="panel-section">
                                    <div className="section-header">
                                        <div className="section-icon">💡</div>
                                        <h3 className="section-title">Pain Points</h3>
                                    </div>
                                    <div style={{ marginTop: '1rem' }}>
                                        {data.insights.pain_points.map((p, i) => (
                                            <div key={i} className="pain-point">{p}</div>
                                        ))}
                                    </div>
                                </div>

                                {/* Emotional Triggers Section */}
                                <div className="panel-section">
                                    <div className="section-header">
                                        <div className="section-icon">🎯</div>
                                        <h3 className="section-title">Emotional Triggers</h3>
                                    </div>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', marginTop: '1rem' }}>
                                        {data.insights.emotional_triggers.map((t, i) => (
                                            <span key={i} className="trigger-tag">{t}</span>
                                        ))}
                                    </div>
                                </div>

                                {/* Target Audience Section */}
                                <div className="panel-section">
                                    <div className="section-header">
                                        <div className="section-icon">🎯</div>
                                        <h3 className="section-title">Target Audience</h3>
                                    </div>
                                    <div style={{ marginTop: '1rem' }}>
                                        <div style={{ marginBottom: '1rem' }}>
                                            <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Demographics</span>
                                            <p style={{ fontSize: '0.9rem', color: '#cbd5e1', marginTop: '0.5rem' }}>{data.insights.demographics || 'Not specified'}</p>
                                        </div>
                                        <div style={{ marginBottom: '1rem' }}>
                                            <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Interests (Meta/Google Ads)</span>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
                                                {(data.insights.targeting_interests || []).length > 0 ? (
                                                    data.insights.targeting_interests.map((interest, i) => (
                                                        <span key={i} className="targeting-tag">{interest}</span>
                                                    ))
                                                ) : (
                                                    <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>No interests specified</span>
                                                )}
                                            </div>
                                        </div>
                                        <div>
                                            <span style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Behaviors</span>
                                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
                                                {(data.insights.behaviors || []).length > 0 ? (
                                                    data.insights.behaviors.map((behavior, i) => (
                                                        <span key={i} className="behavior-tag">{behavior}</span>
                                                    ))
                                                ) : (
                                                    <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>No behaviors specified</span>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Compliance Check Section */}
                                <div className="panel-section">
                                    <div className="section-header">
                                        <div className="section-icon">✓</div>
                                        <h3 className="section-title">Compliance Check</h3>
                                    </div>
                                    <div className="compliance-box">
                                        <span className="risk-badge">✓ {data.compliance.risk_level} Risk</span>
                                        {data.compliance.suggestions.map((s, i) => (
                                            <div key={i} className="compliance-item">{s}</div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* VARIATIONS CONTAINER - Right Side */}
                            <div className="blob-full fade-in-blur" style={{ animationDelay: '0.2s' }}>
                                <div className="panel-section" style={{ marginBottom: '2rem', borderBottom: '1px solid rgba(255, 255, 255, 0.05)', paddingBottom: '1.5rem' }}>
                                    <div className="section-header">
                                        <div className="section-icon" style={{ background: 'linear-gradient(135deg, #c084fc, #7dd3fc)' }}>🧪</div>
                                        <h3 className="section-title" style={{ color: 'var(--accent-purple)', fontSize: '1.2rem' }}>A/B Testing Matrix</h3>
                                    </div>
                                    <p style={{ fontSize: '0.9rem', color: 'var(--text-dim)', marginTop: '0.5rem' }}>
                                        We've synthesized 3 unique angles for your A/B testing strategy. Deploy these simultaneously to identify the highest-performing psychological trigger.
                                    </p>
                                </div>

                                {data.variations.map((v, i) => {
                                    const variantLabels = ['Variant A', 'Variant B', 'Variant C'];
                                    const modeIcons: { [key: string]: string } = {
                                        'Emotional': '❤️',
                                        'Logical': '🧠',
                                        'Scarcity': '⚡'
                                    };
                                    const modeColors: { [key: string]: { bg: string, border: string, color: string } } = {
                                        'Emotional': { bg: 'rgba(192, 132, 252, 0.15)', border: 'rgba(192, 132, 252, 0.3)', color: '#c084fc' },
                                        'Logical': { bg: 'rgba(125, 211, 252, 0.15)', border: 'rgba(125, 211, 252, 0.3)', color: '#7dd3fc' },
                                        'Scarcity': { bg: 'rgba(239, 68, 68, 0.15)', border: 'rgba(239, 68, 68, 0.3)', color: '#f87171' }
                                    };
                                    const modeColor = modeColors[v.angle] || modeColors['Emotional'];

                                    const isEditing = editingIndex === i

                                    return (
                                        <div key={i} className="ad-card" style={{ marginBottom: i < data.variations.length - 1 ? '1.5rem' : '0' }}>
                                            <div className="ad-header">
                                                <div className="mode-badge" style={{ background: modeColor.bg, borderColor: modeColor.border, color: modeColor.color }}>
                                                    <span>{modeIcons[v.angle] || '📝'}</span>
                                                    <span style={{ fontWeight: 800, borderRight: `1px solid ${modeColor.border}`, paddingRight: '0.6rem', marginRight: '0.6rem' }}>{variantLabels[i]}</span>
                                                    <span>{v.angle} Appeal</span>
                                                </div>
                                                <div className="ad-actions">
                                                    {!isEditing ? (
                                                        <>
                                                            <button className="action-btn" onClick={() => copyToClipboard(`${v.headline}\n\n${v.primary_text}\n\nCTA: ${v.cta}`)}>📋 Copy</button>
                                                            <button className="action-btn" onClick={() => handleEdit(i)}>✏️ Edit</button>
                                                        </>
                                                    ) : (
                                                        <>
                                                            <button className="action-btn" onClick={() => handleSaveEdit(i)} style={{ background: 'rgba(34, 197, 94, 0.2)', borderColor: 'rgba(34, 197, 94, 0.3)', color: '#4ade80' }}>✓ Save</button>
                                                            <button className="action-btn" onClick={handleCancelEdit} style={{ background: 'rgba(239, 68, 68, 0.2)', borderColor: 'rgba(239, 68, 68, 0.3)', color: '#f87171' }}>✕ Cancel</button>
                                                        </>
                                                    )}
                                                </div>
                                            </div>
                                            {isEditing ? (
                                                <>
                                                    <input
                                                        type="text"
                                                        value={editedVariation?.headline || ''}
                                                        onChange={(e) => setEditedVariation({ ...editedVariation!, headline: e.target.value })}
                                                        className="ad-headline"
                                                        style={{
                                                            width: '100%',
                                                            background: 'rgba(255, 255, 255, 0.05)',
                                                            border: '1px solid rgba(255, 255, 255, 0.2)',
                                                            borderRadius: '8px',
                                                            padding: '0.75rem',
                                                            color: 'var(--text-bright)',
                                                            fontSize: '1.4rem',
                                                            fontWeight: 700,
                                                            marginBottom: '1rem'
                                                        }}
                                                        placeholder="Headline"
                                                    />
                                                    <textarea
                                                        value={editedVariation?.primary_text || ''}
                                                        onChange={(e) => setEditedVariation({ ...editedVariation!, primary_text: e.target.value })}
                                                        className="ad-body"
                                                        style={{
                                                            width: '100%',
                                                            background: 'rgba(255, 255, 255, 0.05)',
                                                            border: '1px solid rgba(255, 255, 255, 0.2)',
                                                            borderRadius: '8px',
                                                            padding: '0.75rem',
                                                            color: '#cbd5e1',
                                                            fontSize: '1rem',
                                                            lineHeight: '1.7',
                                                            marginBottom: '1.5rem',
                                                            minHeight: '100px',
                                                            resize: 'vertical',
                                                            fontFamily: 'inherit'
                                                        }}
                                                        placeholder="Body text"
                                                    />
                                                    <input
                                                        type="text"
                                                        value={editedVariation?.cta || ''}
                                                        onChange={(e) => setEditedVariation({ ...editedVariation!, cta: e.target.value })}
                                                        style={{
                                                            width: '100%',
                                                            background: 'rgba(255, 255, 255, 0.05)',
                                                            border: '1px solid rgba(255, 255, 255, 0.2)',
                                                            borderRadius: '8px',
                                                            padding: '0.75rem',
                                                            color: 'var(--text-bright)',
                                                            fontSize: '1rem',
                                                            fontWeight: 600,
                                                            marginBottom: '1rem'
                                                        }}
                                                        placeholder="Call to Action"
                                                    />
                                                </>
                                            ) : (
                                                <>
                                                    <h2 className="ad-headline">{v.headline}</h2>
                                                    <p className="ad-body">{v.primary_text}</p>
                                                    <a href="#" className="ad-cta">
                                                        <span>🛍️</span>
                                                        <span>{v.cta}</span>
                                                    </a>
                                                </>
                                            )}
                                        </div>
                                    );
                                })}

                                {/* CHANNEL OPTIMIZATION */}
                                <div className="cloud-card fade-in-blur" style={{ animationDelay: '0.4s', marginTop: '1.5rem' }}>
                                    <span className="section-lbl">Channel Optimization</span>
                                    <div style={{ marginTop: '1.5rem' }}>
                                        <span className="field-label">WhatsApp Broadcast</span>
                                        <div className="channel-pre">{data.channel_opt.whatsapp}</div>
                                    </div>
                                    <div style={{ marginTop: '2rem' }}>
                                        <span className="field-label">SMS Message</span>
                                        <div className="channel-pre">{data.channel_opt.sms}</div>
                                    </div>
                                </div>
                            </div>
                        </>
                    )}
                </main>
            </div>

            {/* FOOTER */}
            <footer className="app-footer">
                <div className="footer-content">
                    <p className="footer-text">
                        Developed by <a href="https://portfolio-sudharsan-karthikeyan.vercel.app/" target="_blank" rel="noopener noreferrer" className="footer-name" style={{ textDecoration: 'none' }}>Sudharsan</a>
                    </p>
                    <div className="social-icons">
                        <a href="https://www.facebook.com/sudharsanmilburnhere" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="Facebook">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                            </svg>
                        </a>
                        <a href="https://www.instagram.com/sudharsan_milburn" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="Instagram">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                            </svg>
                        </a>
                        <a href="https://medium.com/@sudharsanmilburn" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="Medium">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M13.54 12a6.8 6.8 0 01-6.77 6.82A6.8 6.8 0 010 12a6.8 6.8 0 016.77-6.82A6.8 6.8 0 0113.54 12zM20.96 12c0 3.54-1.51 6.42-3.38 6.42-1.87 0-3.39-2.88-3.39-6.42s1.52-6.42 3.39-6.42 3.38 2.88 3.38 6.42M24 12c0 3.17-.53 5.75-1.19 5.75-.66 0-1.19-2.58-1.19-5.75s.53-5.75 1.19-5.75C23.47 6.25 24 8.83 24 12z" />
                            </svg>
                        </a>
                        <a href="https://www.linkedin.com/in/sudharsan-karthikeyan-seo-analyst" target="_blank" rel="noopener noreferrer" className="social-icon" aria-label="LinkedIn">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                            </svg>
                        </a>
                    </div>
                </div>
            </footer>
        </div>
    )
}

export default App




