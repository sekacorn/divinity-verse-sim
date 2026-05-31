import { useCallback, useEffect, useRef, useState } from 'react'
import { api, Deity, FeedEntry, Mortal, WorldState } from './api'

export function useSimulation() {
  const [world, setWorld] = useState<WorldState | null>(null)
  const [mortals, setMortals] = useState<Mortal[]>([])
  const [deities, setDeities] = useState<Deity[]>([])
  const [feed, setFeed] = useState<FeedEntry[]>([])
  const [activeDeity, setActiveDeity] = useState<Deity | null>(null)
  const [selectedMortal, setSelectedMortal] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const sourceRef = useRef<EventSource | null>(null)

  const addFeed = useCallback((entry: FeedEntry) => {
    setFeed(prev => [...prev.slice(-299), entry])
  }, [])

  const refreshAll = useCallback(async () => {
    try {
      const [w, m, d] = await Promise.all([api.world(), api.mortals(), api.deities()])
      setWorld(w)
      setMortals(m)
      setDeities(d)
      setActiveDeity(prev => {
        if (prev) return d.find(x => x.name === prev.name) ?? d[0] ?? null
        return d[0] ?? null
      })
      setSelectedMortal(prev => (m.some(x => x.name === prev) ? prev : null))
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Failed to load')
    }
  }, [])

  useEffect(() => {
    refreshAll()
  }, [refreshAll])

  useEffect(() => {
    function connect() {
      const src = new EventSource('/api/stream')
      sourceRef.current = src

      src.onmessage = async (evt) => {
        // Real backend SSE shape: { type, tick, text?, mortal?, action? }
        const data = JSON.parse(evt.data) as {
          type: string
          tick: number
          text?: string
          mortal?: string
          action?: string
        }

        if (data.type === 'tick') {
          // Tick heartbeat — refresh state, don't add a feed entry
          await refreshAll()
          return
        }

        const entry: FeedEntry = {
          id: `${Date.now()}-${Math.random()}`,
          type: data.type,
          tick: data.tick,
          text: data.text ?? '',
          action: data.action,
          mortal: data.mortal,
        }
        addFeed(entry)
      }

      src.onerror = () => {
        src.close()
        setTimeout(connect, 2000)
      }
    }

    connect()
    return () => sourceRef.current?.close()
  }, [addFeed, refreshAll])

  const doTick = useCallback(async (n = 1) => {
    setLoading(true)
    setError(null)
    try {
      const result = await api.tick(n)
      // Backend tick is synchronous — actions come back in response, also via SSE
      result.actions.forEach((text, i) => {
        addFeed({
          id: `tick-${Date.now()}-${i}`,
          type: 'action',
          tick: result.tick,
          text,
        })
      })
      await refreshAll()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Tick failed')
    } finally {
      setLoading(false)
    }
  }, [refreshAll, addFeed])

  const divineAction = useCallback(async (
    action: string,
    target = '',
    message = '',
  ) => {
    if (!activeDeity) { setError('Select a deity first'); return }
    setLoading(true)
    setError(null)
    try {
      const res = await api.action({ deity: activeDeity.name, action, target, message })
      addFeed({
        id: `divine-${Date.now()}`,
        type: 'divine_act',
        tick: world?.tick ?? 0,
        text: res.result,
        action,
        mortal: target || undefined,
      })
      await refreshAll()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Action failed')
    } finally {
      setLoading(false)
    }
  }, [activeDeity, refreshAll, addFeed, world?.tick])

  return {
    world, mortals, deities, feed, activeDeity, selectedMortal,
    loading, error,
    setActiveDeity, setSelectedMortal, setError,
    doTick, divineAction,
  }
}
