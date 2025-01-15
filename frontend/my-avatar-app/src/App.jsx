// App.jsx
import React from 'react';
import AnimatedAvatar from './AnimatedAvatar';
import './App.css';

function App() {
  console.log("App component is rendering");  
  console.log("API_BASE_URL:", import.meta.env.VITE_APP_API_BASE_URL);
  return (
    <div className="App p-2">
      <main className="flex justify-center">
        <AnimatedAvatar />
      </main>
    </div>
  );
}

export default App;