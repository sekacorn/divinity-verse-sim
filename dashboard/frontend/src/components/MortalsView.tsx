import { Mortal } from '../api'

interface Props {
  mortals: Mortal[]
  selected: string | null
  onSelect: (name: string) => void
}

function needColor(v: number) {
  if (v > 60) return 'var(--primary-container)'
  if (v > 20) return 'var(--tertiary)'
  return 'var(--secondary-container)'
}

function NeedRow({ label, value }: { label: string; value: number }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <span style={{
          fontFamily: 'Inter', fontSize: '10px', fontWeight: 600,
          letterSpacing: '0.06em', color: 'var(--outline)', textTransform: 'uppercase',
        }}>{label}</span>
        <span style={{
          fontFamily: "'JetBrains Mono', monospace", fontSize: '10px',
          color: needColor(value),
        }}>{value}</span>
      </div>
      <div style={{ height: '4px', background: 'var(--surface-container-highest)', borderRadius: '999px', overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: `${value}%`,
          background: needColor(value),
          transition: 'width 0.5s, background 0.5s',
        }} />
      </div>
    </div>
  )
}

export function MortalsView({ mortals, selected, onSelect }: Props) {
  return (
    <div style={{ padding: '1.5rem', overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <h2 style={{
          fontFamily: "'Playfair Display', serif", fontSize: '24px', fontWeight: 600,
          color: 'var(--on-surface)',
        }}>Mortals</h2>
        <span style={{
          fontFamily: "'JetBrains Mono', monospace", fontSize: '13px',
          color: 'var(--outline)', padding: '4px 10px',
          border: '1px solid var(--glass-stroke)', borderRadius: '0.25rem',
        }}>
          {mortals.length} living
        </span>
      </div>

      {mortals.length === 0 && (
        <div className="glass-panel" style={{ padding: '2rem', borderRadius: '0.5rem', textAlign: 'center' }}>
          <span className="material-symbols-outlined" style={{ fontSize: '48px', color: 'var(--outline)', display: 'block', marginBottom: '0.75rem' }}>group_off</span>
          <p style={{ color: 'var(--outline)', fontFamily: "'JetBrains Mono', monospace" }}>No living mortals. Spawn one from the Command tab.</p>
        </div>
      )}

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
        gap: '1rem',
      }}>
        {mortals.map(m => {
          const isSelected = selected === m.name
          const isCritical = Object.values(m.needs).some(v => v <= 20)
          const borderColor = isSelected
            ? 'var(--primary)'
            : isCritical
            ? 'rgba(197,2,11,0.5)'
            : 'var(--glass-stroke)'

          return (
            <button
              key={m.name}
              onClick={() => onSelect(m.name)}
              style={{
                padding: '1.25rem', borderRadius: '0.5rem',
                border: `1px solid ${borderColor}`,
                background: isSelected ? 'rgba(167,224,255,0.06)' : 'rgba(255,255,255,0.03)',
                backdropFilter: 'blur(12px)',
                cursor: 'pointer', textAlign: 'left',
                transition: 'all 0.2s',
                boxShadow: isSelected ? '0 0 20px 2px rgba(116,209,255,0.15)' : 'none',
              }}
            >
              {/* Header row */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                <div>
                  <div style={{
                    fontFamily: "'JetBrains Mono', monospace", fontSize: '14px', fontWeight: 500,
                    color: isSelected ? 'var(--primary)' : 'var(--on-surface)',
                    marginBottom: '2px',
                  }}>{m.name}</div>
                  <div style={{ fontSize: '11px', color: 'var(--outline)', fontStyle: 'italic' }}>{m.location}</div>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '4px' }}>
                  <span style={{
                    fontSize: '10px', color: 'var(--primary-container)',
                    border: '1px solid rgba(90,200,250,0.3)',
                    padding: '1px 6px', borderRadius: '0.125rem',
                    fontFamily: 'Inter', fontWeight: 600, letterSpacing: '0.06em',
                    textTransform: 'uppercase',
                  }}>{m.archetype}</span>
                  <span style={{ fontSize: '10px', color: 'var(--outline)', fontFamily: "'JetBrains Mono', monospace" }}>
                    born T{m.tick_born}
                  </span>
                </div>
              </div>

              {/* Needs */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <NeedRow label="Hunger" value={m.needs.hunger} />
                <NeedRow label="Rest" value={m.needs.rest} />
                <NeedRow label="Purpose" value={m.needs.purpose} />
              </div>

              {/* Traits */}
              <div style={{ marginTop: '0.75rem', display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                {m.traits?.map(t => (
                  <span key={t} style={{
                    fontSize: '10px', color: 'var(--on-surface-variant)',
                    background: 'rgba(255,255,255,0.05)', borderRadius: '0.25rem',
                    padding: '2px 6px', fontFamily: 'Inter',
                  }}>{t}</span>
                ))}
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
