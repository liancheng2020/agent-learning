export class PreferenceMemory {
  constructor() { this.values = new Map([["reviewProfile", "balanced"]]); }
  get(key) { return this.values.get(key); }
  set(key, value) { this.values.set(key, value); return { key, value, updatedAt: new Date().toISOString() }; }
  all() { return Object.fromEntries(this.values); }
}
