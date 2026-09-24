/**
 * Core Client-side TTL Cache
 */
class AppCache {
  constructor() {
    this.memory = new Map();
  }

  get(key) {
    const item = this.memory.get(key);
    if (!item) return null;
    if (Date.now() > item.expiresAt) {
      this.memory.delete(key);
      return null;
    }
    return item.value;
  }

  set(key, value, ttlSeconds = 120) {
    this.memory.set(key, {
      value,
      expiresAt: Date.now() + (ttlSeconds * 1000)
    });
  }

  invalidate(prefix) {
    for (const key of this.memory.keys()) {
      if (key.startsWith(prefix)) {
        this.memory.delete(key);
      }
    }
  }

  clear() {
    this.memory.clear();
  }
}

window.AppCache = new AppCache();
