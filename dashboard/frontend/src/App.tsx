import { useState } from 'react'
import { useSimulation } from './useSimulation'
import { Header, Tab } from './components/Header'
import { MortalsPanel } from './components/MortalsPanel'
import { ActionGrid } from './components/ActionGrid'
import { ChroniclePanel } from './components/ChroniclePanel'
import { DashboardView } from './components/DashboardView'
import { MortalsView } from './components/MortalsView'
import { PantheonView } from './components/PantheonView'

const TAB_ICONS: Record<Tab, string> = {
  Dashboard: 'dashboard',
  Mortals:   'group',
  Command:   'terminal',
  Pantheon:  'account_balance',
}

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('Command')

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
      <Header
        world={world}
        essence={essence}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Error toast */}
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

      {/* Main content area */}
      <div style={{ marginTop: '64px', height: 'calc(100vh - 64px)', overflow: 'hidden' }}>

        {/* Dashboard tab */}
        {activeTab === 'Dashboard' && (
          <DashboardView world={world} mortals={mortals} deities={deities} feed={feed} />
        )}

        {/* Mortals tab */}
        {activeTab === 'Mortals' && (
          <MortalsView mortals={mortals} selected={selectedMortal} onSelect={setSelectedMortal} />
        )}

        {/* Command tab — 3-column layout */}
        {activeTab === 'Command' && (
          <main style={{
            padding: '1rem',
            display: 'grid',
            gridTemplateColumns: '3fr 6fr 3fr',
            gap: '1rem',
            height: '100%',
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
        )}

        {/* Pantheon tab */}
        {activeTab === 'Pantheon' && (
          <PantheonView deities={deities} activeDeity={activeDeity} onSelect={setActiveDeity} />
        )}
      </div>

      {/* Mobile bottom nav */}
      <nav className="mobile-nav" style={{
        position: 'fixed', bottom: 0, left: 0, width: '100%', zIndex: 50,
        display: 'flex', justifyContent: 'space-around', alignItems: 'center',
        padding: '0.5rem 1rem 1.5rem',
        background: 'rgba(12,14,18,0.2)', backdropFilter: 'blur(24px)',
        borderTop: '1px solid var(--glass-stroke)',
      }}>
        {(['Dashboard', 'Mortals', 'Command', 'Pantheon'] as Tab[]).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px',
              background: 'none', border: 'none', cursor: 'pointer',
              color: activeTab === tab ? 'var(--primary-fixed-dim)' : 'var(--outline)',
            }}
          >
            <span className="material-symbols-outlined">{TAB_ICONS[tab]}</span>
            <span style={{ fontSize: '10px', fontFamily: 'Inter', fontWeight: 500 }}>{tab}</span>
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
