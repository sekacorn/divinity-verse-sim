import { useState } from 'react'
import { Mortal, Deity, ACTION_COSTS } from '../api'

const ARCHETYPES = ['farmer', 'merchant', 'scholar', 'guard', 'wanderer', 'priest', 'blacksmith', 'thief']

interface Props {
  selectedMortal: string | null
  activeDeity: Deity | null
  mortals: Mortal[]
  onAction: (action: string, target: string, message: string) => void
  onTick: (n: number) => void
  loading: boolean
  onError: (msg: string) => void
}

const ACTIONS = [
  { key: 'bless',   label: 'Bless',   icon: 'auto_awesome', color: 'var(--primary)',       needsTarget: true  },
  { key: 'smite',   label: 'Smite',   icon: 'flash_on',     color: 'var(--secondary)',     needsTarget: true  },
  { key: 'inspire', label: 'Inspire', icon: 'lightbulb',    color: 'var(--tertiary)',      needsTarget: true  },
  { key: 'curse',   label: 'Curse',   icon: 'skull',        color: '#c084fc',             needsTarget: true  },
  { key: 'spawn',   label: 'Spawn',   icon: 'person_add',   color: 'var(--primary-fixed)', needsTarget: false },
]

function glowColor(key: string) {
  if (key === 'smite' || key === 'curse') return 'rgba(197, 2, 11, 0.25)'
  if (key === 'inspire') return 'rgba(255, 212, 79, 0.25)'
  return 'rgba(116, 209, 255, 0.25)'
}

const viewportImg = 'https://lh3.googleusercontent.com/aida-public/AB6AXuAEWfbsRyrgkhgOZQEArPM9vhrx6BwHbRTekO2NU4iwb_8x8brZCsnLs7Gw_mF2QtAg_Ovu_ptl53LsYSnl_SJyN4W90nsNilVK5nazB-B_4i65UhJRAS2zpp5iAAu24wlhZ2agj400sAGzn0hn5yLssJkS2frZsKAEt5o4EJ8xBMhBOgp69yU8NO4k3FFGCk_Vh4ZPnL1uepoK79-vpJxeF8C8GB7k1plnbJn1u2uIDZJphq4D5wMe2AEYkhKb8WN41n5OjXn_pFo'

export function ActionGrid({ selectedMortal, activeDeity, onAction, onTick, loading, onError }: Props) {
  const [hoveredAction, setHoveredAction] = useState<string | null>(null)
  const [spawnArch, setSpawnArch] = useState('farmer')
  const [showSpawnPicker, setShowSpawnPicker] = useState(false)

  function handleAction(key: string) {
    const def = ACTIONS.find(a => a.key === key)!
    if (def.needsTarget && !selectedMortal) {
      onError(`Select a mortal before using ${key}.`)
      return
    }
    if (key === 'spawn') {
      setShowSpawnPicker(p => !p)
      return
    }
    onAction(key, selectedMortal ?? '', '')
  }

  function handleSpawnConfirm() {
    onAction('spawn', spawnArch, '')
    setShowSpawnPicker(false)
  }

  const energyPct = activeDeity
    ? Math.max(0, Math.min(100, (activeDeity.divine_energy / activeDeity.max_energy) * 100))
    : 0

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {/* Strategic Viewport */}
      <div className="glass-panel" style={{ position: 'relative', borderRadius: '0.5rem', overflow: 'hidden', aspectRatio: '16/9' }}>
        <img src={viewportImg} alt="Divine View" style={{ width: '100%', height: '100%', objectFit: 'cover', opacity: 0.4 }} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, var(--background), transparent)' }} />

        <div style={{ position: 'absolute', top: '1rem', left: '1rem', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {(['COORD: 48.2N / 12.9E', 'SECTOR: AURORA-7'] as const).map((label, i) => (
            <span key={label} style={{
              fontFamily: 'Inter', fontSize: '12px', fontWeight: 600, letterSpacing: '0.08em',
              color: i === 0 ? 'var(--primary)' : 'var(--outline)',
              background: 'rgba(0,0,0,0.4)', backdropFilter: 'blur(4px)',
              padding: '2px 8px', borderRadius: '0.25rem',
            }}>{label}</span>
          ))}
        </div>

        {selectedMortal && (
          <div style={{
            position: 'absolute', bottom: '1rem', left: '1rem',
            fontFamily: "'JetBrains Mono', monospace", fontSize: '12px',
            color: 'var(--primary)', background: 'rgba(0,0,0,0.6)',
            padding: '4px 10px', borderRadius: '0.25rem',
          }}>
            TARGET: {selectedMortal}
          </div>
        )}

        {/* Energy bar overlay */}
        {activeDeity && (
          <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: '3px', background: 'rgba(255,255,255,0.06)' }}>
            <div style={{
              height: '100%', width: `${energyPct}%`,
              background: 'linear-gradient(90deg, var(--primary-container), var(--tertiary))',
              transition: 'width 0.5s ease',
            }} />
          </div>
        )}

        <div style={{ position: 'absolute', inset: 0, border: '1px solid rgba(167,224,255,0.2)', pointerEvents: 'none' }} />
      </div>

      {/* Action Buttons — 5 actions, 3+2 grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '0.75rem' }}>
        {ACTIONS.map(action => {
          const isHovered = hoveredAction === action.key
          const canUse = action.needsTarget ? !!selectedMortal : true
          const energyCost = ACTION_COSTS[action.key] ?? 0
          const canAfford = activeDeity ? activeDeity.divine_energy >= energyCost : false

          return (
            <button
              key={action.key}
              onClick={() => handleAction(action.key)}
              disabled={loading || !canAfford}
              onMouseEnter={() => setHoveredAction(action.key)}
              onMouseLeave={() => setHoveredAction(null)}
              style={{
                padding: '0.75rem 0.5rem', borderRadius: '0.5rem',
                backdropFilter: 'blur(12px)',
                background: isHovered ? `${action.color}1A` : 'rgba(255,255,255,0.03)',
                border: `1px solid ${isHovered ? action.color + '66' : 'var(--glass-stroke)'}`,
                boxShadow: isHovered ? `0 0 20px 2px ${glowColor(action.key)}` : 'none',
                display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.4rem',
                cursor: loading || !canAfford ? 'not-allowed' : 'pointer',
                transition: 'all 0.25s',
                opacity: !canAfford ? 0.45 : !canUse && action.needsTarget ? 0.6 : 1,
              }}
              title={!canAfford ? 'Insufficient energy' : action.needsTarget && !selectedMortal ? 'Select a mortal first' : ''}
            >
              <div style={{
                width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                borderRadius: '50%',
                border: `1px solid ${isHovered ? action.color : action.color + '4D'}`,
                transition: 'border-color 0.25s',
              }}>
                <span className="material-symbols-outlined" style={{ color: action.color, fontSize: '20px' }}>
                  {action.icon}
                </span>
              </div>
              <span style={{ fontFamily: 'Inter', fontSize: '11px', fontWeight: 600, letterSpacing: '0.08em', color: action.color, textTransform: 'uppercase' }}>
                {action.label}
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '2px', opacity: isHovered ? 1 : 0.55, transition: 'opacity 0.25s' }}>
                <span className="material-symbols-outlined" style={{ fontSize: '11px', color: 'var(--tertiary)' }}>bolt</span>
                <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: '10px', color: 'var(--tertiary)' }}>
                  {energyCost}
                </span>
              </div>
            </button>
          )
        })}
      </div>

      {/* Spawn archetype picker (inline) */}
      {showSpawnPicker && (
        <div style={{
          padding: '0.75rem', borderRadius: '0.5rem',
          background: 'rgba(255,255,255,0.04)', border: '1px solid var(--primary-fixed)4D',
          display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap',
        }}>
          <span style={{ fontFamily: 'Inter', fontSize: '12px', color: 'var(--outline)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Archetype:
          </span>
          <select
            value={spawnArch}
            onChange={e => setSpawnArch(e.target.value)}
            style={{
              background: 'var(--surface-container-lowest)', border: '1px solid var(--glass-stroke)',
              borderRadius: '0.25rem', color: 'var(--on-surface)',
              fontFamily: "'JetBrains Mono', monospace", fontSize: '13px', padding: '4px 8px',
            }}
          >
            {ARCHETYPES.map(a => <option key={a} value={a}>{a}</option>)}
          </select>
          <button onClick={handleSpawnConfirm} disabled={loading} style={{
            background: 'rgba(193,232,255,0.1)', border: '1px solid var(--primary-fixed)',
            borderRadius: '0.25rem', color: 'var(--primary-fixed)',
            fontFamily: 'Inter', fontSize: '12px', fontWeight: 600, padding: '4px 12px', cursor: 'pointer',
          }}>
            Spawn
          </button>
          <button onClick={() => setShowSpawnPicker(false)} style={{
            background: 'none', border: 'none', color: 'var(--outline)', cursor: 'pointer', fontSize: '16px',
          }}>×</button>
        </div>
      )}

      {/* Tick Controls */}
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        {([1, 5] as const).map(n => (
          <button
            key={n}
            onClick={() => onTick(n)}
            disabled={loading}
            style={{
              flex: 1, padding: '0.6rem',
              background: loading ? 'rgba(255,255,255,0.02)' : 'rgba(167,224,255,0.06)',
              border: '1px solid var(--glass-stroke)',
              borderRadius: '0.25rem',
              color: loading ? 'var(--outline)' : 'var(--primary)',
              fontFamily: "'JetBrains Mono', monospace", fontSize: '13px',
              cursor: loading ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s',
              letterSpacing: '0.05em',
            }}
          >
            {loading ? '...' : `Tick +${n}`}
          </button>
        ))}
      </div>
    </div>
  )
}
