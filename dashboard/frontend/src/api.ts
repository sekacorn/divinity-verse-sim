export interface WorldState {
  world_name: string
  current_era: string
  clock: string
  tick: number
  stability: number
  faith: number
  mortal_count: number
}

export interface MortalNeeds {
  hunger: number
  rest: number
  purpose: number
}

export interface Mortal {
  name: string
  archetype: string
  traits: string[]
  location: string
  needs: MortalNeeds
  alive: boolean
  tick_born: number
}

export interface Deity {
  name: string
  title: string
  domain: string
  divine_energy: number
  max_energy: number
  color?: string
}

export interface LoreEntry {
  tick: number
  source_name: string
  description: string
  event_type: string
}

export interface FeedEntry {
  id: string
  type: string        // "action" | "divine_act" | "tick" | "death" | "birth" | "decree"
  tick: number
  text: string
  action?: string     // "smite" | "bless" | "inspire" | "curse" | "spawn" | "decree"
  mortal?: string
}

// Real action costs matching backend ACTION_COSTS
export const ACTION_COSTS: Record<string, number> = {
  bless: 15,
  smite: 20,
  inspire: 10,
  curse: 20,
  spawn: 25,
  decree: 10,
}

const BASE = ''

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    let detail = 'Request failed'
    try {
      const body = await res.json()
      detail = body.detail ?? JSON.stringify(body)
    } catch (_) {}
    throw new Error(detail)
  }
  return res.json()
}

export const api = {
  world: () => request<WorldState>('/api/world'),
  mortals: () => request<Mortal[]>('/api/mortals'),
  deities: () => request<Deity[]>('/api/deities'),
  lore: () => request<LoreEntry[]>('/api/lore'),
  memories: (name: string) => request<LoreEntry[]>(`/api/mortals/${encodeURIComponent(name)}/memories`),
  tick: (n = 1) => request<{ tick: number; actions: string[] }>('/api/tick', {
    method: 'POST', body: JSON.stringify({ n }),
  }),
  action: (body: { deity: string; action: string; target?: string; message?: string }) =>
    request<{ result: string }>('/api/action', { method: 'POST', body: JSON.stringify(body) }),
}
