import { useState } from 'react';
import useMountEffect from '@restart/hooks/useMountEffect'
import './App.css';

function App() {
  const [result, setResult] = useState<any>(null);
  useMountEffect(() => {
    fetch("/bills").then(response => response.json()).then(response => {
      setResult(JSON.stringify(response));
    });
  });

  return (
    <div className="App">
      {result}
    </div>
  );
}

export default App;
