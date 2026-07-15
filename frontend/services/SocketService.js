import * as SecureStore from 'expo-secure-store';
import { API_URL } from '../api';

class SocketService {
    constructor() {
        this.ws = null;
        this.callbacks = {};
    }

    connect() {
        return new Promise(async (resolve, reject) => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                return resolve();
            }
            
            const token = await SecureStore.getItemAsync('userToken');
            if (!token) return reject(new Error("No token"));

            // API_URL = http://.../api, so we replace http with ws, and remove /api at the end if we append it
            let wsUrl = API_URL.replace('http://', 'ws://').replace('https://', 'wss://');
            if (wsUrl.endsWith('/api')) {
                wsUrl = wsUrl.substring(0, wsUrl.length - 4);
            }
            wsUrl += '/api/multiplayer/ws?token=' + token;
            
            this.ws = new WebSocket(wsUrl);

            this.ws.onopen = () => {
                console.log("WebSocket connected");
                resolve();
            };

            this.ws.onerror = (e) => {
                console.error("WebSocket error:", e);
            };

        this.ws.onmessage = (e) => {
            try {
                const message = JSON.parse(e.data);
                console.log("WS Recv:", message);
                if (this.callbacks[message.type]) {
                    this.callbacks[message.type].forEach(cb => cb(message));
                }
            } catch (err) {
                console.error("Error parsing websocket message", err);
            }
        };

        this.ws.onclose = () => {
            console.log("WebSocket disconnected");
            this.ws = null;
        };
        });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }

    send(action, data = {}) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            const msg = { action, ...data };
            console.log("WS Send:", msg);
            this.ws.send(JSON.stringify(msg));
        } else {
            console.error("WS Send failed: Socket not connected");
            // Optionally, we could dispatch an internal error event here
            if (this.callbacks['error']) {
                this.callbacks['error'].forEach(cb => cb({ message: "Sunucuya bağlanılamadı. Lobiye tekrar girin." }));
            }
        }
    }

    on(type, callback) {
        if (!this.callbacks[type]) {
            this.callbacks[type] = [];
        }
        this.callbacks[type].push(callback);
    }

    off(type, callback) {
        if (this.callbacks[type]) {
            this.callbacks[type] = this.callbacks[type].filter(cb => cb !== callback);
        }
    }
}

export default new SocketService();
