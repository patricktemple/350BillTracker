import { useState } from 'react';
import './App.css';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";
import SavedBillsPage from './SavedBillsPage';
import LookupBillPage from './LookupBillPage';

function App() {
  return (
    <Router>
      <Route path="/" exact component={SavedBillsPage} />
      <Route path="/lookup" component={LookupBillPage} />
    </Router>
  )
}

export default App;
