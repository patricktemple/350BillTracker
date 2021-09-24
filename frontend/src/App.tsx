import './App.css';
import { BrowserRouter as Router, Route } from "react-router-dom";
import SavedBillsPage from './SavedBillsPage';
import React from 'react';

function App() {
  return (
    <Router>
      <Route path="/" exact component={SavedBillsPage} />
    </Router>
  )
}

export default App;
