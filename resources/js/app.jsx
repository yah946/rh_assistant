import React from 'react';
import ReactDOM from 'react-dom/client';

function App() {
    return (
        <div>
            <h1>Laravel 13 + React 🚀</h1>
        </div>
    );
}

ReactDOM.createRoot(document.getElementById('app')).render(
    <React.StrictMode>
        <App />
    </React.StrictMode>
);