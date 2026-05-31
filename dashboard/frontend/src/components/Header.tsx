import { WorldState } from '../api'

interface Props {
  world: WorldState | null
  essence: number
}

export function Header({ world, essence }: Props) {
  return (
    <header style={{
      position: 'fixed', top: 0, left: 0, width: '100%', zIndex: 50,
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '0 1rem', height: '64px',
      background: 'rgba(30,32,36,0.1)', backdropFilter: 'blur(24px)',
      borderBottom: '1px solid var(--glass-stroke)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <span className="material-symbols-outlined" style={{ color: 'var(--primary)' }}>language</span>
        <h1 style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: '42px', fontWeight: 700, lineHeight: 1.2,
          letterSpacing: '-0.02em', color: 'var(--primary)',
        }}>
          {world?.world_name ?? 'Aetheria Prime'}
        </h1>
      </div>

      <nav style={{ display: 'flex', gap: '2rem', alignItems: 'center' }} className="desktop-nav">
        {['Dashboard', 'Mortals', 'Command', 'Pantheon'].map(label => (
          <a key={label} href="#" style={{
            color: label === 'Command' ? 'var(--primary)' : 'var(--on-surface-variant)',
            textDecoration: 'none', padding: '0.5rem 1rem', borderRadius: '0.25rem',
            transition: 'background 0.3s',
          }}>
            {label}
          </a>
        ))}
      </nav>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <span className="material-symbols-outlined" style={{ color: 'var(--primary)' }}>bolt</span>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
          <span style={{
            fontFamily: 'Inter', fontSize: '12px', fontWeight: 600,
            letterSpacing: '0.08em', color: 'var(--outline)', textTransform: 'uppercase',
          }}>Essence</span>
          <span style={{
            fontFamily: "'JetBrains Mono', monospace", fontSize: '20px',
            fontWeight: 700, color: 'var(--primary)',
          }}>
            {essence.toLocaleString()}
          </span>
        </div>
      </div>
    </header>
  )
}
