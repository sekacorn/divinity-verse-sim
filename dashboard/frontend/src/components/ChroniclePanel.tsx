import { useEffect, useRef, useState } from 'react'
import { Deity, FeedEntry } from '../api'

interface Props {
  feed: FeedEntry[]
  deities: Deity[]
  activeDeity: Deity | null
  onSelectDeity: (d: Deity) => void
  onDecree: (text: string) => void
}

function feedColor(entry: FeedEntry): string {
  if (entry.type === 'divine_act') {
    if (entry.action === 'smite') return 'var(--secondary)'
    if (entry.action === 'inspire') return 'var(--tertiary)'
    return 'var(--primary)'
  }
  if (entry.type === 'death') return 'var(--secondary)'
  if (entry.type === 'birth') return 'var(--primary)'
  if (entry.type === 'decree') return 'var(--tertiary)'
  return 'var(--on-surface-variant)'
}

export function ChroniclePanel({ feed, deities, activeDeity, onSelectDeity, onDecree }: Props) {
  const [decree, setDecree] = useState('')
  const feedRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight
    }
  }, [feed])

  const handleDecree = () => {
    const text = decree.trim()
    if (!text) return
    onDecree(text)
    setDecree('')
  }

  return (
    <aside style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Live Chronicle */}
      <section className="glass-panel" style={{
        flex: 1, borderRadius: '0.5rem', padding: '1.25rem',
        display: 'flex', flexDirection: 'column', gap: '1rem',
        borderColor: 'rgba(167,224,255,0.1)', overflow: 'hidden',
      }}>
        <h3 style={{
          fontFamily: 'Inter', fontSize: '12px', fontWeight: 600,
          letterSpacing: '0.08em', color: 'var(--primary)', textTransform: 'uppercase',
          display: 'flex', alignItems: 'center', gap: '8px',
        }}>
          <span style={{
            width: '8px', height: '8px', borderRadius: '50%',
            background: 'var(--primary)',
            animation: 'pulse 2s infinite',
            display: 'inline-block',
          }} />
          Live Chronicle
        </h3>

        <div ref={feedRef} style={{
          flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1rem',
          paddingRight: '0.5rem',
          fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', lineHeight: 1.5,
          color: 'var(--on-surface-variant)',
        }}>
          {feed.length === 0 && (
            <p style={{ opacity: 0.5 }}>[SYSTEM] Awaiting first tick...</p>
          )}
          {feed.map(entry => (
            <p key={entry.id}>
              <span style={{ color: feedColor(entry) }}>{'>'}</span>{' '}
              <span style={{ opacity: 0.6 }}>[{entry.tick}]</span>{' '}
              {entry.text}
            </p>
          ))}
          <p style={{ animation: 'pulse 2s infinite' }}>
            <span style={{ color: 'var(--primary)' }}>{'>'}</span> Awaiting next decree...
          </p>
        </div>

        {/* Decree Terminal */}
        <div style={{
          marginTop: 'auto', borderTop: '1px solid var(--glass-stroke)', paddingTop: '1rem',
        }}>
          <div style={{
            background: 'rgba(12,14,18,0.5)', padding: '0.75rem', borderRadius: '0.25rem',
            border: '1px solid var(--glass-stroke)',
            display: 'flex', alignItems: 'center', gap: '0.5rem',
            fontFamily: "'JetBrains Mono', monospace", fontSize: '14px',
          }}>
            <span style={{ color: 'var(--tertiary)', whiteSpace: 'nowrap' }}>DECREE_ID:</span>
            <input
              value={decree}
              onChange={e => setDecree(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleDecree()}
              placeholder="Enter Command..."
              style={{
                background: 'transparent', border: 'none', outline: 'none',
                color: 'var(--on-surface)', flex: 1, fontSize: '14px',
                fontFamily: "'JetBrains Mono', monospace",
              }}
            />
            <div className="terminal-cursor" />
          </div>
        </div>
      </section>

      {/* Deity / Active Modifier Panel */}
      <section className="glass-panel" style={{
        padding: '1.25rem', borderRadius: '0.5rem',
        background: 'rgba(90,200,250,0.05)',
        borderColor: 'rgba(90,200,250,0.2)',
      }}>
        {activeDeity ? (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <span className="material-symbols-outlined" style={{ color: 'var(--primary-container)' }}>account_balance</span>
              <span style={{
                fontFamily: 'Inter', fontSize: '12px', fontWeight: 600,
                letterSpacing: '0.08em', color: 'var(--primary-container)', textTransform: 'uppercase',
              }}>{activeDeity.name}</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--on-surface-variant)', lineHeight: 1.6 }}>
              <span style={{ color: 'var(--primary)' }}>{activeDeity.title}</span>{' — '}
              {activeDeity.domain} &nbsp;|&nbsp;
              Energy: <span style={{ color: 'var(--tertiary)', fontFamily: "'JetBrains Mono', monospace" }}>
                {activeDeity.divine_energy}/{activeDeity.max_energy}
              </span>
            </p>
            <div style={{
              height: '4px', background: 'var(--surface-container-highest)',
              borderRadius: '999px', overflow: 'hidden', marginTop: '0.75rem',
            }}>
              <div style={{
                height: '100%',
                background: 'linear-gradient(90deg, var(--primary-container), var(--tertiary))',
                width: `${Math.max(0, Math.min(100, (activeDeity.divine_energy / activeDeity.max_energy) * 100))}%`,
                transition: 'width 0.5s ease',
              }} />
            </div>
          </>
        ) : (
          <>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <span className="material-symbols-outlined" style={{ color: 'var(--primary-container)' }}>info</span>
              <span style={{
                fontFamily: 'Inter', fontSize: '12px', fontWeight: 600,
                letterSpacing: '0.08em', color: 'var(--primary-container)', textTransform: 'uppercase',
              }}>Active Modifier</span>
            </div>
            <p style={{ fontSize: '12px', color: 'var(--on-surface-variant)', lineHeight: 1.6 }}>
              <span style={{ color: 'var(--primary)' }}>Ethereal Resonance:</span>{' '}
              Smite costs reduced by 20% in northern sectors due to lunar alignment.
            </p>
          </>
        )}
      </section>
    </aside>
  )
}
