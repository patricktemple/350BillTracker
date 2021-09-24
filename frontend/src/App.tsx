import './App.css';
import { BrowserRouter as Router, Route } from "react-router-dom";
import SavedBillsPage from './SavedBillsPage';
import CouncilMembersPage from './CouncilMembersPage';
import React from 'react';

function App() {
  return (
    <Router>
      <Route path="/" exact component={SavedBillsPage} />
      <Route path="/council-members" component={CouncilMembersPage} />
    </Router>
  )
}

export default App;
