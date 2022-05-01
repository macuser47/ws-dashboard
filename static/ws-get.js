const ws_port = 5000
window.onload = () => {
    const ws = new WebSocket(`ws://localhost:${ws_port}`);
    ws.onmessage = (event) => {
        const kv = JSON.parse(event.data);
        for (const key in kv) {
            const value = kv[key];
            const element = document.getElementById(key);
            if (element) {
                element.innerHTML = value;
            }
        }
    };
};