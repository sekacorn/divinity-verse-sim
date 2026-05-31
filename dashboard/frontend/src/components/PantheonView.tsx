import { Deity } from '../api'

interface Props {
  deities: Deity[]
  activeDeity: Deity | null
  onSelect: (d: Deity) => void
}

const DOMAIN_COLORS: Record<string, string> = {
  knowledge: 'var(--primary)',
  chaos:     'var(--secondary)',
  harvest:   '#86efac',
  war:       '#f97316',
  fate:      '#c084fc',
}

const DOMAIN_ICONS: Record<string, string> = {
  knowledge: 'menu_book',
  chaos:     'bolt',
  harvest:   'grass',
  war:       'swords',
  fate:      'auto_awesome',
}

export function PantheonView({ deities, activeDeity, onSelect }: Props) {
  return (
    <div style={{ padding: '1.5rem', overflowY: 'auto', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <h2 style={{
          fontFamily: "'Playfair Display', serif", fontSize: '24px', fontWeight: 600,
          color: 'var(--on-surface)',
        }}>Pantheon</h2>
        <span style={{
          fontFamily: "'JetBrains Mono', monospace", fontSize: '13px',
          color: 'var(--outline)', padding: '4px 10px',
          border: '1px solid var(--glass-stroke)', borderRadius: '0.25rem',
        }}>
          {deities.length} {deities.length === 1 ? 'deity' : 'deities'}
        </span>
      </div>

      {deities.length === 0 && (
        <div className="glass-panel" style={{ padding: '2rem', borderRadius: '0.5rem', textAlign: 'center' }}>
          <span className="material-symbols-outlined" style={{ fontSize: '48px', color: 'var(--outline)', display: 'block', marginBottom: '0.75rem' }}>account_balance</span>
          <p style={{ color: 'var(--outline)', fontFamily: "'JetBrains Mono', monospace" }}>
            No deities loaded. Add a JSON file to contributors/ and restart.
          </p>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1rem' }}>
        {deities.map(d => {
          const isActive = activeDeity?.name === d.name
          const domainColor = DOMAIN_COLORS[d.domain] ?? 'var(--primary)'
          const domainIcon = DOMAIN_ICONS[d.domain] ?? 'auto_awesome'
          const energyPct = Math.round((d.divine_energy / d.max_energy) * 100)

          return (
            <button
              key={d.name}
              onClick={() => onSelect(d)}
              style={{
                padding: '1.5rem', borderRadius: '0.5rem',
                border: `1px solid ${isActive ? domainColor + '88' : 'var(--glass-stroke)'}`,
                background: isActive ? `${domainColor}0D` : 'rgba(255,255,255,0.03)',
                backdropFilter: 'blur(12px)',
                cursor: 'pointer', textAlign: 'left',
                transition: 'all 0.2s',
                boxShadow: isActive ? `0 0 24px 2px ${domainColor}22` : 'none',
              }}
            >
              {/* Top row */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '4px' }}>
                    <span className="material-symbols-outlined" style={{ color: domainColor, fontSize: '20px' }}>
                      {domainIcon}
                    </span>
                    <span style={{
                      fontFamily: "'Playfair Display', serif", fontSize: '22px',
                      fontWeight: 600, color: isActive ? domainColor : 'var(--on-surface)',
                    }}>{d.name}</span>
                    {isActive && (
                      <span style={{
                        fontSize: '9px', fontFamily: 'Inter', fontWeight: 700,
                        color: domainColor, border: `1px solid ${domainColor}`,
                        padding: '1px 5px', borderRadius: '0.125rem', letterSpacing: '0.08em',
                        textTransform: 'uppercase',
                      }}>Active</span>
                    )}
                  </div>
                  <div style={{ fontFamily: 'Inter', fontSize: '13px', color: 'var(--on-surface-variant)', fontStyle: 'italic' }}>
                    {d.title}
                  </div>
                </div>
                <span style={{
                  fontSize: '10px', fontFamily: 'Inter', fontWeight: 600,
                  color: domainColor, border: `1px solid ${domainColor}44`,
                  padding: '2px 8px', borderRadius: '0.125rem', letterSpacing: '0.08em',
                  textTransform: 'uppercase', alignSelf: 'flex-start',
                }}>{d.domain}</span>
              </div>

              {/* Energy */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                  <span style={{ fontFamily: 'Inter', fontSize: '11px', color: 'var(--outline)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                    Divine Energy
                  </span>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '18px', fontWeight: 700, color: 'var(--tertiary)' }}>
                    {d.divine_energy}<span style={{ fontSize: '12px', color: 'var(--outline)', fontWeight: 400 }}>/{d.max_energy}</span>
                  </span>
                </div>
                <div style={{ height: '6px', background: 'var(--surface-container-highest)', borderRadius: '999px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%', width: `${energyPct}%`,
                    background: `linear-gradient(90deg, ${domainColor}, var(--tertiary))`,
                    transition: 'width 0.5s',
                  }} />
                </div>
                <div style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '10px', color: 'var(--outline)', textAlign: 'right' }}>
                  {energyPct}% · +5 per tick
                </div>
              </div>
            </button>
          )
        })}
      </div>

      {/* Contributor tip */}
      <div className="glass-panel" style={{
        marginTop: '1.5rem', padding: '1rem', borderRadius: '0.5rem',
        borderColor: 'rgba(167,224,255,0.1)',
      }}>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
          <span className="material-symbols-outlined" style={{ color: 'var(--primary-container)', fontSize: '18px', flexShrink: 0, marginTop: '1px' }}>info</span>
          <div>
            <p style={{ fontFamily: 'Inter', fontSize: '12px', color: 'var(--on-surface-variant)', lineHeight: 1.6, margin: 0 }}>
              <span style={{ color: 'var(--primary)' }}>Become a deity:</span> add a JSON file to <code style={{ fontFamily: "'JetBrains Mono', monospace", color: 'var(--tertiary)', fontSize: '11px' }}>contributors/</code> with your name, title, and domain (knowledge · chaos · harvest · war · fate), then restart the server.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
