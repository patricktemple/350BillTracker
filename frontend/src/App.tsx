import { useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
import SavedBillsPage from './SavedBillsPage';
import SearchBillsPage from './SearchBillsModal';

function App() {
  return (
    <Router>
      <Route path="/" exact component={SavedBillsPage} />
      {/* <Route path="/search" component={SearchBillsPage} /> */}
    </Router>
  )
}

export default App;
