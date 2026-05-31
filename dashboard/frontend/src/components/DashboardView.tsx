import { WorldState, Mortal, Deity, FeedEntry } from '../api'

interface Props {
  world: WorldState | null
  mortals: Mortal[]
  deities: Deity[]
  feed: FeedEntry[]
}

function StatCard({ label, value, sub, color = 'var(--primary)', icon }: {
  label: string; value: string; sub?: string; color?: string; icon: string
}) {
  return (
    <div className="glass-panel" style={{
      padding: '1.5rem', borderRadius: '0.5rem',
      display: 'flex', flexDirection: 'column', gap: '0.75rem',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span style={{
          fontFamily: 'Inter', fontSize: '12px', fontWeight: 600,
          letterSpacing: '0.08em', color: 'var(--outline)', textTransform: 'uppercase',
        }}>{label}</span>
        <span className="material-symbols-outlined" style={{ color, fontSize: '20px', opacity: 0.7 }}>{icon}</span>
      </div>
      <span style={{
        fontFamily: "'JetBrains Mono', monospace", fontSize: '32px',
        fontWeight: 700, color, lineHeight: 1,
      }}>{value}</span>
      {sub && <span style={{ fontSize: '12px', color: 'var(--outline)' }}>{sub}</span>}
    </div>
  )
}

function NeedBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <span style={{ fontSize: '11px', color: 'var(--outline)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</span>
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color }}>{Math.round(value)}%</span>
      </div>
      <div style={{ height: '3px', background: 'var(--surface-container-highest)', borderRadius: '999px', overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${value}%`, background: color, transition: 'width 0.5s' }} />
      </div>
    </div>
  )
}

export function DashboardView({ world, mortals, deities, feed }: Props) {
  const avgNeeds = (key: keyof typeof mortals[0]['needs']) =>
    mortals.length ? Math.round(mortals.reduce((s, m) => s + m.needs[key], 0) / mortals.length) : 0

  const activeDeity = deities[0]

  return (
    <div style={{ padding: '1.5rem', overflowY: 'auto', height: '100%' }}>
      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
        <StatCard
          label="World Tick"
          value={String(world?.tick ?? 0)}
          sub={world?.clock ?? '—'}
          icon="schedule"
        />
        <StatCard
          label="Population"
          value={String(mortals.length)}
          sub={`cap: ${world?.mortal_count !== undefined ? '10' : '—'}`}
          color="var(--primary-container)"
          icon="group"
        />
        <StatCard
          label="Stability"
          value={`${world?.stability ?? 0}%`}
          sub="avg mortal needs"
          color="var(--primary-fixed-dim)"
          icon="shield"
        />
        <StatCard
          label="Faith"
          value={`${world?.faith ?? 0}%`}
          sub={activeDeity ? `${activeDeity.name} energy` : '—'}
          color="var(--tertiary)"
          icon="bolt"
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
        {/* World needs overview */}
        <div className="glass-panel" style={{ padding: '1.25rem', borderRadius: '0.5rem' }}>
          <h3 style={{
            fontFamily: 'Inter', fontSize: '12px', fontWeight: 600,
            letterSpacing: '0.08em', color: 'var(--outline)', textTransform: 'uppercase',
            marginBottom: '1rem',
          }}>World Needs Average</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <NeedBar label="Hunger" value={avgNeeds('hunger')} color="var(--primary-container)" />
            <NeedBar label="Rest" value={avgNeeds('rest')} color="var(--tertiary)" />
            <NeedBar label="Purpose" value={avgNeeds('purpose')} color="var(--primary-fixed-dim)" />
          </div>
        </div>

        {/* Deity energy */}
        <div className="glass-panel" style={{ padding: '1.25rem', borderRadius: '0.5rem' }}>
          <h3 style={{
            fontFamily: 'Inter', fontSize: '12px', fontWeight: 600,
            letterSpacing: '0.08em', color: 'var(--outline)', textTransform: 'uppercase',
            marginBottom: '1rem',
          }}>Pantheon Energy</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {deities.length === 0 && (
              <p style={{ color: 'var(--outline)', fontSize: '13px' }}>No deities loaded.</p>
            )}
            {deities.map(d => (
              <div key={d.name} style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', color: 'var(--primary)' }}>{d.name}</span>
                  <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '11px', color: 'var(--tertiary)' }}>
                    {d.divine_energy}/{d.max_energy}
                  </span>
                </div>
                <div style={{ height: '3px', background: 'var(--surface-container-highest)', borderRadius: '999px', overflow: 'hidden' }}>
                  <div style={{
                    height: '100%',
                    width: `${Math.round((d.divine_energy / d.max_energy) * 100)}%`,
                    background: 'linear-gradient(90deg, var(--primary-container), var(--tertiary))',
                    transition: 'width 0.5s',
                  }} />
                </div>
                <span style={{ fontSize: '10px', color: 'var(--outline)', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {d.domain} · {d.title}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent chronicle */}
      <div className="glass-panel" style={{ padding: '1.25rem', borderRadius: '0.5rem' }}>
        <h3 style={{
          fontFamily: 'Inter', fontSize: '12px', fontWeight: 600,
          letterSpacing: '0.08em', color: 'var(--outline)', textTransform: 'uppercase',
          marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px',
        }}>
          <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: 'var(--primary)', display: 'inline-block', animation: 'pulse 2s infinite' }} />
          Recent Chronicle
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', maxHeight: '260px', overflowY: 'auto' }}>
          {feed.length === 0 && <p style={{ color: 'var(--outline)', fontFamily: "'JetBrains Mono', monospace", fontSize: '13px' }}>No events yet.</p>}
          {[...feed].reverse().slice(0, 20).map(e => (
            <p key={e.id} style={{
              fontFamily: "'JetBrains Mono', monospace", fontSize: '12px',
              color: e.type === 'divine_act' ? (
                e.action === 'smite' ? 'var(--secondary)' :
                e.action === 'inspire' ? 'var(--tertiary)' : 'var(--primary)'
              ) : 'var(--on-surface-variant)',
              margin: 0,
            }}>
              <span style={{ opacity: 0.5 }}>[{e.tick}]</span> {e.text}
            </p>
          ))}
        </div>
      </div>
    </div>
  )
}
