/**
 * Lightweight Event-Driven State Store
 */
class StateStore {
  constructor() {
    this.state = {};
    this.listeners = new Map();
  }

  get(key, defaultValue = null) {
    return this.state[key] !== undefined ? this.state[key] : defaultValue;
  }

  set(key, value) {
    const prev = this.state[key];
    this.state[key] = value;
    if (this.listeners.has(key)) {
      this.listeners.get(key).forEach(cb => cb(value, prev));
    }
  }

  subscribe(key, callback) {
    if (!this.listeners.has(key)) {
      this.listeners.set(key, []);
    }
    this.listeners.get(key).push(callback);
    return () => {
      const arr = this.listeners.get(key);
      const idx = arr.indexOf(callback);
      if (idx >= 0) arr.splice(idx, 1);
    };
  }
}

window.AppState = new StateStore();
