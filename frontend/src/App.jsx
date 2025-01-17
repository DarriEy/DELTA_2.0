// App.jsx
import React from 'react';
import AnimatedAvatar from './AnimatedAvatar';
import './App.css';

function App() {
  console.log("App component is rendering");  

  return (
    <div className="App p-2">
      <main className="flex justify-center">
        <AnimatedAvatar />
      </main>
    </div>
  );
}

export default App;