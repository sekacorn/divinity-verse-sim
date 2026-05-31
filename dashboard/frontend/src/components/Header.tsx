import { WorldState } from '../api'

export type Tab = 'Dashboard' | 'Mortals' | 'Command' | 'Pantheon'

const NAV_TABS: { label: Tab; icon: string }[] = [
  { label: 'Dashboard', icon: 'dashboard' },
  { label: 'Mortals',   icon: 'group' },
  { label: 'Command',   icon: 'terminal' },
  { label: 'Pantheon',  icon: 'account_balance' },
]

interface Props {
  world: WorldState | null
  essence: number
  activeTab: Tab
  onTabChange: (tab: Tab) => void
}

export function Header({ world, essence, activeTab, onTabChange }: Props) {
  return (
    <header style={{
      position: 'fixed', top: 0, left: 0, width: '100%', zIndex: 50,
      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      padding: '0 1rem', height: '64px',
      background: 'rgba(30,32,36,0.1)', backdropFilter: 'blur(24px)',
      borderBottom: '1px solid var(--glass-stroke)',
    }}>
      {/* Logo + world name */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <span className="material-symbols-outlined" style={{ color: 'var(--primary)' }}>language</span>
        <h1 style={{
          fontFamily: "'Playfair Display', serif",
          fontSize: '42px', fontWeight: 700, lineHeight: 1.2,
          letterSpacing: '-0.02em', color: 'var(--primary)',
          whiteSpace: 'nowrap',
        }}>
          {world?.world_name ?? 'Aetheria Prime'}
        </h1>
      </div>

      {/* Desktop nav */}
      <nav style={{ display: 'flex', gap: '0.25rem', alignItems: 'center' }} className="desktop-nav">
        {NAV_TABS.map(({ label }) => {
          const isActive = activeTab === label
          return (
            <button
              key={label}
              onClick={() => onTabChange(label)}
              style={{
                color: isActive ? 'var(--primary)' : 'var(--on-surface-variant)',
                background: isActive ? 'rgba(167,224,255,0.08)' : 'none',
                border: 'none',
                borderBottom: isActive ? '2px solid var(--primary)' : '2px solid transparent',
                padding: '0.5rem 1.25rem',
                cursor: 'pointer',
                fontFamily: 'Inter', fontSize: '13px', fontWeight: isActive ? 600 : 500,
                transition: 'all 0.2s',
                borderRadius: '0.25rem 0.25rem 0 0',
              }}
            >
              {label}
            </button>
          )
        })}
      </nav>

      {/* Essence counter */}
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
