import { Mortal } from '../api'

interface Props {
  mortals: Mortal[]
  selected: string | null
  stability: number
  faith: number
  onSelect: (name: string) => void
}

function needColor(v: number) {
  if (v > 60) return 'var(--primary-container)'
  if (v > 20) return 'var(--tertiary)'
  return 'var(--secondary-container)'
}

function purposeLabel(v: number) {
  if (v >= 80) return 'Exalted'
  if (v >= 50) return 'Seeking'
  if (v >= 20) return 'Fading'
  return 'Voidbound'
}

export function MortalsPanel({ mortals, selected, stability, faith, onSelect }: Props) {
  return (
    <aside style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* World Status */}
      <section className="glass-panel" style={{
        padding: '1.25rem', borderRadius: '0.5rem',
        display: 'flex', flexDirection: 'column', gap: '1rem',
      }}>
        <h3 style={{
          fontFamily: 'Inter', fontSize: '12px', fontWeight: 600,
          letterSpacing: '0.08em', color: 'var(--outline)', textTransform: 'uppercase',
        }}>World Status</h3>

        <StatBar label="Stability" value={stability} color="var(--primary-fixed-dim)" />
        <StatBar label="Faith Level" value={faith} color="var(--tertiary)" />
      </section>

      {/* Priority Mortals */}
      <section className="glass-panel" style={{
        padding: '1.25rem', borderRadius: '0.5rem',
        flex: 1, display: 'flex', flexDirection: 'column', gap: '1rem',
        overflow: 'hidden',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{
            fontFamily: 'Inter', fontSize: '12px', fontWeight: 600,
            letterSpacing: '0.08em', color: 'var(--outline)', textTransform: 'uppercase',
          }}>Priority Mortals</h3>
          <span className="material-symbols-outlined" style={{ color: 'var(--outline)', fontSize: '18px' }}>filter_alt</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', overflowY: 'auto', flex: 1 }}>
          {mortals.length === 0 && (
            <p style={{ color: 'var(--outline)', fontFamily: "'JetBrains Mono', monospace", fontSize: '13px' }}>
              No mortals yet.
            </p>
          )}
          {mortals.map(m => (
            <MortalChip key={m.name} mortal={m} selected={selected === m.name} onClick={() => onSelect(m.name)} />
          ))}
        </div>
      </section>
    </aside>
  )
}

function StatBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <span style={{ color: 'var(--on-surface-variant)' }}>{label}</span>
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '20px', fontWeight: 700, color }}>
          {Math.round(value)}%
        </span>
      </div>
      <div style={{ height: '4px', background: 'var(--surface-container-highest)', borderRadius: '999px', overflow: 'hidden' }}>
        <div style={{ height: '100%', background: color, width: `${value}%`, transition: 'width 0.5s ease' }} />
      </div>
    </div>
  )
}

function MortalChip({ mortal, selected, onClick }: { mortal: Mortal; selected: boolean; onClick: () => void }) {
  const purpose = mortal.needs.purpose
  const isHero = purpose >= 70
  const isFallen = purpose < 20
  const borderColor = selected
    ? 'var(--primary-fixed-dim)'
    : isFallen
    ? 'rgba(197,2,11,0.4)'
    : 'var(--glass-stroke)'
  const nameColor = isFallen ? 'var(--secondary)' : 'var(--primary)'
  const badge = isHero ? 'HERO' : isFallen ? 'FALLEN' : mortal.archetype.toUpperCase()

  return (
    <button onClick={onClick} style={{
      padding: '0.75rem', border: `1px solid ${borderColor}`, borderRadius: '0.25rem',
      background: 'transparent', cursor: 'pointer', textAlign: 'left',
      transition: 'border-color 0.2s',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '14px', fontWeight: 500, color: nameColor }}>
          {mortal.name}
        </span>
        <span style={{
          fontSize: '10px', color: 'var(--outline)', padding: '0 4px',
          border: '1px solid var(--outline)', borderRadius: '0.125rem',
        }}>{badge}</span>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <div style={{ height: '2px', background: 'var(--surface-container-highest)', borderRadius: '999px', overflow: 'hidden' }}>
          <div style={{
            height: '100%',
            background: needColor(purpose),
            width: `${purpose}%`,
            transition: 'width 0.5s, background 0.5s',
          }} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', textTransform: 'uppercase', color: 'var(--outline)' }}>
          <span>Purpose</span>
          <span style={{ color: needColor(purpose) }}>{purposeLabel(purpose)}</span>
        </div>
      </div>
    </button>
  )
}
