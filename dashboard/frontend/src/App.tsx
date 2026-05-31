import { useSimulation } from './useSimulation'
import { Header } from './components/Header'
import { MortalsPanel } from './components/MortalsPanel'
import { ActionGrid } from './components/ActionGrid'
import { ChroniclePanel } from './components/ChroniclePanel'

export default function App() {
  const {
    world, mortals, deities, feed,
    activeDeity, selectedMortal,
    loading, error,
    setActiveDeity, setSelectedMortal, setError,
    doTick, divineAction,
  } = useSimulation()

  const essence = activeDeity?.divine_energy ?? 0

  const handleDecree = (text: string) => divineAction('decree', '', text)

  return (
    <>
      <Header world={world} essence={essence} />

      {error && (
        <div style={{
          position: 'fixed', top: '80px', right: '18px', zIndex: 100,
          background: 'rgba(166,77,82,0.94)', borderRadius: '0.5rem',
          padding: '12px 16px', color: '#fff', fontSize: '13px',
          maxWidth: '320px', lineHeight: 1.4,
          boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
        }}>
          {error}
          <button
            onClick={() => setError(null)}
            style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', marginLeft: '8px', fontSize: '18px', lineHeight: 1 }}
          >×</button>
        </div>
      )}

      <main style={{
        marginTop: '64px',
        padding: '1rem',
        display: 'grid',
        gridTemplateColumns: '3fr 6fr 3fr',
        gap: '1rem',
        height: 'calc(100vh - 64px)',
        overflow: 'hidden',
      }}>
        <MortalsPanel
          mortals={mortals}
          selected={selectedMortal}
          stability={world?.stability ?? 80}
          faith={world?.faith ?? 60}
          onSelect={setSelectedMortal}
        />

        <ActionGrid
          selectedMortal={selectedMortal}
          activeDeity={activeDeity}
          mortals={mortals}
          onAction={divineAction}
          onTick={doTick}
          loading={loading}
          onError={setError}
        />

        <ChroniclePanel
          feed={feed}
          deities={deities}
          activeDeity={activeDeity}
          onSelectDeity={setActiveDeity}
          onDecree={handleDecree}
        />
      </main>

      {/* Mobile bottom nav */}
      <nav className="mobile-nav" style={{
        position: 'fixed', bottom: 0, left: 0, width: '100%', zIndex: 50,
        display: 'flex', justifyContent: 'space-around', alignItems: 'center',
        padding: '0.5rem 1rem 1.5rem',
        background: 'rgba(12,14,18,0.2)', backdropFilter: 'blur(24px)',
        borderTop: '1px solid var(--glass-stroke)',
      }}>
        {[
          { icon: 'dashboard', label: 'Dashboard' },
          { icon: 'group', label: 'Mortals' },
          { icon: 'terminal', label: 'Command', active: true },
          { icon: 'account_balance', label: 'Pantheon' },
        ].map(item => (
          <button key={item.label} style={{
            display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px',
            background: 'none', border: 'none', cursor: 'pointer',
            color: item.active ? 'var(--primary-fixed-dim)' : 'var(--outline)',
          }}>
            <span className="material-symbols-outlined">{item.icon}</span>
            <span style={{ fontSize: '10px', fontFamily: 'Inter', fontWeight: 500 }}>{item.label}</span>
          </button>
        ))}
      </nav>

      <style>{`
        @media (min-width: 768px) { .mobile-nav { display: none !important; } }
        @media (max-width: 767px) {
          main { grid-template-columns: 1fr !important; overflow-y: auto !important; height: auto !important; padding-bottom: 80px; }
        }
      `}</style>
    </>
  )
}
